#!/usr/bin/env python3
"""CodeMind - MCP Memory Server using FastMCP"""
import json, logging, os, sqlite3, hashlib, re, ast, warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Set, Dict, Optional
from fastmcp import FastMCP

# Suppress transformers/sentence-transformers progress bars and warnings for clean MCP output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

# Setup session logging to .codemind/logs/
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path(".codemind/logs")
log_dir.mkdir(parents=True, exist_ok=True)
session_log_file = log_dir / f"session_{session_id}.log"

# Configure logging to both console and session file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(session_log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"📝 Session logging to: {session_log_file}")

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    from radon.raw import analyze
    HAS_RADON = True
except ImportError:
    HAS_RADON = False
    logger.warning("⚠️  Radon not installed - code metrics will use fallback implementation")

CONFIG = {"project_root": "./", "db_path": ".codemind/memory.db", "watched_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".java", ".cs", ".cpp", ".go", ".rs"], "max_file_size_kb": 500, "embedding_model": "all-MiniLM-L6-v2"}
mcp = FastMCP("CodeMind")
db_conn, embedding_model = None, None

def init_database():
    db_path = CONFIG["db_path"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, purpose TEXT, last_scanned TIMESTAMP, embedding BLOB, key_exports TEXT, file_hash TEXT, size_kb INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT NOT NULL, reasoning TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, affected_files TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS changes (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT NOT NULL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, change_summary TEXT)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_last_scanned ON files(last_scanned)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_changes_timestamp ON changes(timestamp)")
    conn.commit()
    return conn

def load_config():
    if os.path.exists("codemind_config.json"):
        try:
            with open("codemind_config.json") as f:
                CONFIG.update(json.load(f))
            logger.info(" Loaded configuration")
        except Exception as e:
            logger.warning(f" Error loading config: {e}")

def extract_purpose(content, file_path):
    m = re.search(r'^\s*"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
    if m: return m.group(1).strip()[:200]
    m = re.search(r'^\s*#\s*(.*?)(?:\n|$)', content, re.MULTILINE)
    if m: return m.group(1).strip()[:200]
    return f"File: {os.path.basename(file_path)}"

def extract_key_exports(content, file_path):
    exports = []
    exports.extend(re.findall(r'class\s+(\w+)', content)[:10])
    exports.extend([f for f in re.findall(r'def\s+([a-zA-Z_]\w*)', content) if not f.startswith('_')][:10])
    if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
        exports.extend(re.findall(r'export\s+(?:function|class|const|let|var)\s+(\w+)', content)[:10])
    return list(set(exports))[:15]

# AST-based helper functions for production-quality code analysis
class ImportVisitor(ast.NodeVisitor):
    """Extract imports using AST for accurate parsing"""
    def __init__(self):
        self.imports: Set[str] = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

class CallVisitor(ast.NodeVisitor):
    """Extract function calls using AST for accurate parsing"""
    def __init__(self):
        self.calls: Set[str] = set()
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.add(node.func.attr)
        self.generic_visit(node)

class FunctionVisitor(ast.NodeVisitor):
    """Extract function definitions and their details using AST"""
    def __init__(self):
        self.functions: List[Dict] = []
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'params': len(node.args.args),
            'decorators': len(node.decorator_list),
            'has_docstring': ast.get_docstring(node) is not None
        })
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

def parse_imports_ast(content: str) -> Set[str]:
    """Parse imports using AST (production-quality replacement for regex)"""
    try:
        tree = ast.parse(content)
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports
    except SyntaxError:
        # Fallback to regex if AST parsing fails
        imports = set()
        import_patterns = [
            r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
        ]
        for pattern in import_patterns:
            imports.update(re.findall(pattern, content, re.MULTILINE))
        return imports

def parse_calls_ast(content: str, function_name: str) -> Set[str]:
    """Parse function calls using AST (production-quality replacement for regex)"""
    try:
        tree = ast.parse(content)
        # Find the specific function
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                visitor = CallVisitor()
                visitor.visit(node)
                # Filter out built-ins and common keywords
                keywords = {'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'print', 'range'}
                return {c for c in visitor.calls if c not in keywords}
        return set()
    except SyntaxError:
        # Fallback to regex
        import re
        func_pattern = rf'def {re.escape(function_name)}\s*\('
        func_match = re.search(func_pattern, content)
        if not func_match:
            return set()
        start = func_match.start()
        next_def = re.search(r'\ndef \w+\s*\(', content[start + 1:])
        end = start + next_def.start() if next_def else len(content)
        func_body = content[start:end]
        call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        calls = set(re.findall(call_pattern, func_body))
        keywords = {'if', 'for', 'while', 'return', 'yield', 'def', 'class', 'with', 'try', 'except', 'print'}
        return {c for c in calls if c not in keywords and c != function_name}

def parse_functions_ast(content: str) -> List[Dict]:
    """Parse function definitions using AST"""
    try:
        tree = ast.parse(content)
        visitor = FunctionVisitor()
        visitor.visit(tree)
        return visitor.functions
    except SyntaxError:
        return []

def _index_file_internal(file_path, conn):
    """Internal function to index a file - called by scan_project"""
    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        file_hash = hashlib.md5(content.encode()).hexdigest()
        cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (file_path,))
        if cursor.fetchone() and cursor.fetchone()[0] == file_hash: return
        purpose = extract_purpose(content, file_path)
        key_exports = extract_key_exports(content, file_path)
        embedding_blob = None
        if HAS_EMBEDDINGS and embedding_model:
            embedding_blob = embedding_model.encode(purpose, convert_to_numpy=True).tobytes()
        conn.execute("INSERT OR REPLACE INTO files (path, purpose, last_scanned, embedding, key_exports, file_hash, size_kb) VALUES (?, ?, ?, ?, ?, ?, ?)", (file_path, purpose, datetime.now(), embedding_blob, json.dumps(key_exports), file_hash, len(content.encode()) // 1024))
        conn.commit()
    except Exception as e:
        logger.debug(f" Error indexing {file_path}: {e}")

def scan_project(conn):
    project_root = Path(CONFIG["project_root"]).resolve()
    indexed = 0
    for ext in CONFIG["watched_extensions"]:
        for fp in project_root.rglob(f"*{ext}"):
            if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                try:
                    if fp.stat().st_size // 1024 <= CONFIG["max_file_size_kb"]:
                        _index_file_internal(str(fp), conn)
                        indexed += 1
                except OSError: pass
    logger.info(f" Indexed {indexed} files")

def cosine_similarity(a, b):
    if not HAS_EMBEDDINGS: return 0.0
    va, vb = np.frombuffer(a, dtype=np.float32), np.frombuffer(b, dtype=np.float32)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))

@mcp.tool()
def search_existing_code(query: str, limit: int = 5) -> str:
    """Search for existing functionality before creating new files."""
    lazy_scan()
    if not HAS_EMBEDDINGS or not embedding_model:
        return " Semantic search not available"
    query_blob = embedding_model.encode(query, convert_to_numpy=True).tobytes()
    results = [(p, pu, cosine_similarity(query_blob, e)) for p, pu, e in db_conn.execute('SELECT path, purpose, embedding FROM files WHERE embedding IS NOT NULL').fetchall() if e]
    results.sort(key=lambda x: x[2], reverse=True)
    if not results[:limit]: return f"No code found for: {query}"
    lines = [f"Found {len(results[:limit])} files for '{query}':\n"]
    for i, (p, pu, s) in enumerate(results[:limit], 1):
        lines.append(f"{i}. {p} ({int(s*100)}% match)\n   Purpose: {pu}\n")
    return "\n".join(lines)

@mcp.tool()
def get_file_context(file_path: str) -> str:
    """Get detailed information about a file."""
    lazy_scan()
    row = db_conn.execute('SELECT path, purpose, last_scanned, key_exports, size_kb FROM files WHERE path = ?', (file_path,)).fetchone()
    if not row: return f" File not found: {file_path}"
    p, pu, ls, ke, sz = row
    exports = json.loads(ke) if ke else []
    return f" {p}\n Purpose: {pu}\n Last scanned: {ls}\n Size: {sz} KB\n Exports: {', '.join(exports) or 'None'}"

@mcp.tool()
def record_decision(description: str, reasoning: str, affected_files: List[str] = None) -> str:
    """Store architectural decisions."""
    affected_files = affected_files or []
    cursor = db_conn.execute('INSERT INTO decisions (description, reasoning, affected_files) VALUES (?, ?, ?)', (description, reasoning, json.dumps(affected_files)))
    db_conn.commit()
    return f" Decision #{cursor.lastrowid} recorded\n {description}\n {reasoning}\n Files: {', '.join(affected_files)}"

@mcp.tool()
def query_recent_changes(hours: int = 24) -> str:
    """See recent file modifications."""
    changes = db_conn.execute('SELECT file_path, timestamp, change_summary FROM changes WHERE timestamp > ? ORDER BY timestamp DESC', (datetime.now() - timedelta(hours=hours),)).fetchall()
    if not changes: return f"No changes in last {hours} hours"
    lines = [f"Changes in last {hours} hours:\n"]
    for fp, ts, cs in changes:
        lines.append(f" {fp}\n  {ts}: {cs or 'Modified'}\n")
    return "\n".join(lines)

@mcp.tool()
def check_functionality_exists(feature_description: str, confidence_threshold: float = 0.7) -> str:
    """Check if functionality exists."""
    lazy_scan()
    if not HAS_EMBEDDINGS or not embedding_model:
        return " Check not available"
    query_blob = embedding_model.encode(feature_description, convert_to_numpy=True).tobytes()
    best, best_sim = None, 0.0
    for p, pu, e in db_conn.execute('SELECT path, purpose, embedding FROM files WHERE embedding IS NOT NULL').fetchall():
        if e:
            sim = cosine_similarity(query_blob, e)
            if sim > best_sim:
                best_sim, best = sim, (p, pu)
    if best_sim >= confidence_threshold and best:
        return f" YES!\n {best[0]}\n {best[1]}\n {int(best_sim*100)}%"
    return f" NO\n Searched: {feature_description}\n Closest: {best[0]} ({int(best_sim*100)}%)" if best else f" NO - nothing similar found"

@mcp.tool()
def search_by_export(export_name: str, limit: int = 10) -> str:
    """Find files that export a specific function, class, or variable."""
    lazy_scan()
    results = []
    for path, ke in db_conn.execute('SELECT path, key_exports FROM files WHERE key_exports IS NOT NULL').fetchall():
        exports = json.loads(ke) if ke else []
        if export_name in exports:
            results.append(path)
    if not results: return f"❌ '{export_name}' not found in any exports"
    lines = [f"✅ Found '{export_name}' in {len(results)} file(s):\n"]
    for i, p in enumerate(results[:limit], 1):
        lines.append(f"{i}. {p}\n")
    return "\n".join(lines)

@mcp.tool()
def find_dependencies(file_path: str) -> str:
    """Show what this file imports and what imports this file."""
    lazy_scan()
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
    
    # Parse imports from this file using AST (production-quality)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return f"❌ Error reading file: {e}"
    
    # Use AST-based parsing for accurate import extraction
    imports = parse_imports_ast(content)
    
    # Find files that import this file
    file_name = os.path.basename(file_path).replace('.py', '')
    importers = []
    for path in db_conn.execute('SELECT path FROM files').fetchall():
        if path[0] == file_path: continue
        try:
            with open(path[0], 'r', encoding='utf-8', errors='ignore') as f:
                other_content = f.read()
                other_imports = parse_imports_ast(other_content)
                # Check if this file is imported
                if file_name in other_imports or any(file_name in imp for imp in other_imports):
                    importers.append(path[0])
        except: 
            pass
    
    lines = [f"📦 Dependencies for: {file_path}\n"]
    lines.append(f"\n📥 This file imports ({len(imports)}):")
    if imports:
        for imp in sorted(imports)[:20]:
            lines.append(f"  • {imp}")
        if len(imports) > 20:
            lines.append(f"  ... and {len(imports) - 20} more")
    else:
        lines.append("  (none)")
    
    lines.append(f"\n📤 Files that import this ({len(importers)}):")
    if importers:
        for imp in importers[:20]:
            lines.append(f"  • {imp}")
        if len(importers) > 20:
            lines.append(f"  ... and {len(importers) - 20} more")
    else:
        lines.append("  (none)")
    
    lines.append(f"\n✨ Using AST-based parsing for production-quality analysis")
    
    return "\n".join(lines)

@mcp.tool()
def get_similar_files(file_path: str, limit: int = 5) -> str:
    """Find files similar to the given file (based on purpose/content)."""
    lazy_scan()
    if not HAS_EMBEDDINGS or not embedding_model:
        return "❌ Similarity search not available (embeddings disabled)"
    
    row = db_conn.execute('SELECT embedding, purpose FROM files WHERE path = ? AND embedding IS NOT NULL', (file_path,)).fetchone()
    if not row:
        return f"❌ File not found or not indexed: {file_path}"
    
    target_embedding, target_purpose = row
    results = []
    
    for p, pu, e in db_conn.execute('SELECT path, purpose, embedding FROM files WHERE path != ? AND embedding IS NOT NULL', (file_path,)).fetchall():
        if e:
            sim = cosine_similarity(target_embedding, e)
            results.append((p, pu, sim))
    
    results.sort(key=lambda x: x[2], reverse=True)
    
    if not results[:limit]:
        return f"❌ No similar files found for: {file_path}"
    
    lines = [f"📊 Files similar to: {file_path}\n"]
    lines.append(f"Purpose: {target_purpose}\n")
    for i, (p, pu, s) in enumerate(results[:limit], 1):
        lines.append(f"{i}. {p} ({int(s*100)}% similar)\n   {pu}\n")
    
    return "\n".join(lines)

@mcp.tool()
def list_all_decisions(keyword: str = None, limit: int = 10) -> str:
    """Query architectural decisions, optionally filtered by keyword."""
    if keyword:
        query = 'SELECT id, description, reasoning, timestamp, affected_files FROM decisions WHERE description LIKE ? OR reasoning LIKE ? ORDER BY timestamp DESC LIMIT ?'
        pattern = f'%{keyword}%'
        decisions = db_conn.execute(query, (pattern, pattern, limit)).fetchall()
    else:
        query = 'SELECT id, description, reasoning, timestamp, affected_files FROM decisions ORDER BY timestamp DESC LIMIT ?'
        decisions = db_conn.execute(query, (limit,)).fetchall()
    
    if not decisions:
        return f"❌ No decisions found" + (f" matching '{keyword}'" if keyword else "")
    
    lines = [f"📋 Architectural Decisions" + (f" (matching '{keyword}')" if keyword else "") + f":\n"]
    for id, desc, reason, ts, files in decisions:
        affected = json.loads(files) if files else []
        lines.append(f"\n#{id} - {desc}")
        lines.append(f"  📅 {ts}")
        lines.append(f"  💭 {reason}")
        if affected:
            lines.append(f"  📁 Affects: {', '.join(affected[:5])}")
            if len(affected) > 5:
                lines.append(f"     ... and {len(affected) - 5} more")
    
    return "\n".join(lines)

def _force_reindex_impl() -> str:
    """Implementation of force_reindex"""
    lazy_scan()  # Ensure initialized
    
    start_time = datetime.now()
    
    # Clear existing data
    db_conn.execute('DELETE FROM files')
    db_conn.execute('DELETE FROM changes')
    db_conn.commit()
    
    # Re-scan everything
    scan_project(db_conn)
    
    # Get stats
    cursor = db_conn.execute('SELECT COUNT(*) FROM files')
    file_count = cursor.fetchone()[0]
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    return f"✅ Re-indexed {file_count} files in {elapsed:.1f} seconds\n" + \
           f"📊 Database refreshed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@mcp.tool()
def force_reindex() -> str:
    """
    Force a complete re-scan of the entire project.
    
    Use this when:
    - You've made major changes to multiple files
    - The database seems out of sync
    - You want to refresh all file metadata
    - New files were added and need immediate indexing
    
    Returns summary of indexing operation.
    """
    return _force_reindex_impl()

def _index_file_impl(file_path: str) -> str:
    """Implementation of index_file"""
    lazy_scan()  # Ensure initialized
    
    # Resolve absolute path
    full_path = Path(CONFIG['project_root']) / file_path
    
    if not full_path.exists():
        return f"❌ File not found: {file_path}"
    
    if not full_path.is_file():
        return f"❌ Not a file: {file_path}"
    
    # Check if it's a supported file type
    if full_path.suffix.lower() not in CONFIG['watched_extensions']:
        return f"⚠️ File type {full_path.suffix} not in supported extensions\n" + \
               f"Supported: {', '.join(CONFIG['watched_extensions'])}"
    
    # Index the file
    try:
        _index_file_internal(str(full_path), db_conn)
        
        # Get updated info
        cursor = db_conn.execute(
            'SELECT purpose, key_exports, size_kb, last_scanned FROM files WHERE path = ?',
            (str(full_path.relative_to(CONFIG['project_root'])),)
        )
        row = cursor.fetchone()
        
        if row:
            purpose, exports, size, scanned = row
            exports_list = json.loads(exports) if exports else []
            
            return f"✅ Indexed: {file_path}\n" + \
                   f"📝 Purpose: {purpose or 'Not determined'}\n" + \
                   f"📦 Exports: {', '.join(exports_list[:5])}\n" + \
                   f"📏 Size: {size:.1f} KB\n" + \
                   f"🕐 Scanned: {scanned}"
        else:
            return f"✅ File indexed but details not available: {file_path}"
            
    except Exception as e:
        return f"❌ Error indexing file: {str(e)}"

@mcp.tool()
def index_file(file_path: str) -> str:
    """
    Index or re-index a specific file immediately.
    
    Args:
        file_path: Path to file to index (relative to project root)
    
    Use this when:
    - You just created a new file
    - You made significant changes to a file
    - You want to update a file's metadata immediately
    
    Returns confirmation with file details.
    """
    return _index_file_impl(file_path)

def _get_call_tree_impl(function_name: str, file_path: str = None, depth: int = 2) -> str:
    """
    Show the call tree for a function - what it calls and what calls it.
    
    Args:
        function_name: Name of the function to analyze
        file_path: Optional path to file containing the function (helps narrow search)
        depth: How many levels deep to trace (default: 2)
    
    Use this for:
    - Debugging: "Where is this function called from?"
    - Understanding: "What does this function call?"
    - Refactoring: "What's the execution path?"
    - Performance analysis: "What's the call chain?"
    
    Returns call tree showing callers and callees.
    """
    lazy_scan()  # Ensure initialized
    
    # Find files that might contain the function
    if file_path:
        search_files = [Path(CONFIG['project_root']) / file_path]
    else:
        # Search in key_exports to find the file
        cursor = db_conn.execute(
            "SELECT path FROM files WHERE key_exports LIKE ?",
            (f'%"{function_name}"%',)
        )
        search_files = [Path(CONFIG['project_root']) / row[0] for row in cursor.fetchall()]
    
    if not search_files:
        return f"❌ Function '{function_name}' not found in any indexed file\n" + \
               f"Try: search_by_export('{function_name}') or index_file() first"
    
    result = [f"🌲 Call Tree for '{function_name}':\n"]
    
    # For each file that might contain the function
    for fpath in search_files[:3]:  # Limit to first 3 files
        if not fpath.exists():
            continue
            
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            
            # Use AST for production-quality function call extraction
            import re
            
            # Find the function definition using AST
            try:
                tree = ast.parse(content)
                func_found = False
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name == function_name:
                            func_found = True
                            break
                if not func_found:
                    continue
            except SyntaxError:
                # Fallback to regex if AST fails
                func_pattern = rf'def {re.escape(function_name)}\s*\('
                if not re.search(func_pattern, content):
                    continue
            
            result.append(f"\n📁 Found in: {fpath.relative_to(CONFIG['project_root'])}")
            
            # Use AST-based call extraction
            calls = parse_calls_ast(content, function_name)
            unique_calls = sorted(set(calls))[:10]  # Top 10 unique calls
            
            if unique_calls:
                result.append(f"\n  ⬇️  CALLS (what {function_name} calls):")
                for call in unique_calls:
                    result.append(f"    • {call}()")
            
            # Find what calls this function (search all files)
            result.append(f"\n  ⬆️  CALLED BY (what calls {function_name}):")
            cursor = db_conn.execute('SELECT path FROM files')
            callers = []
            
            for (path,) in cursor.fetchall():
                caller_path = Path(CONFIG['project_root']) / path
                if not caller_path.exists() or caller_path == fpath:
                    continue
                    
                try:
                    caller_content = caller_path.read_text(encoding='utf-8', errors='ignore')
                    # Check if function is called
                    if re.search(rf'\b{re.escape(function_name)}\s*\(', caller_content):
                        # Find which functions in this file call it
                        # Extract all function definitions
                        caller_funcs = re.findall(r'def (\w+)\s*\(', caller_content)
                        if caller_funcs:
                            callers.append(f"{path} → {', '.join(caller_funcs[:3])}")
                        else:
                            callers.append(path)
                            
                        if len(callers) >= 10:  # Limit results
                            break
                except:
                    continue
            
            if callers:
                for caller in callers[:10]:
                    result.append(f"    • {caller}")
            else:
                result.append(f"    (no callers found in indexed files)")
            
            break  # Only process first matching file
            
        except Exception as e:
            result.append(f"  ⚠️ Error analyzing: {str(e)}")
    
    if len(result) == 1:  # Only header
        return f"❌ Could not analyze '{function_name}'\n" + \
               f"Make sure the file is indexed and function exists"
    
    result.append(f"\n💡 Tip: Use find_dependencies() to see module-level imports")
    
    return "\n".join(result)

@mcp.tool()
def get_call_tree(function_name: str, file_path: str = None, depth: int = 2) -> str:
    """
    Show the call tree for a function - what it calls and what calls it.
    
    Args:
        function_name: Name of the function to analyze
        file_path: Optional path to file containing the function (helps narrow search)
        depth: How many levels deep to trace (default: 2)
    
    Use this for:
    - Debugging: "Where is this function called from?"
    - Understanding: "What does this function call?"
    - Refactoring: "What's the execution path?"
    - Performance analysis: "What's the call chain?"
    
    Returns call tree showing callers and callees.
    """
    return _get_call_tree_impl(function_name, file_path, depth)

def _check_breaking_changes_impl(function_name: str, file_path: str) -> str:
    """Implementation of check_breaking_changes"""
    lazy_scan()
    
    result = [f"🔍 Breaking Change Analysis for '{function_name}':\n"]
    
    # Check if it's exported (public API)
    is_public = False
    cursor = db_conn.execute(
        "SELECT key_exports FROM files WHERE path = ?",
        (file_path,)
    )
    row = cursor.fetchone()
    if row and row[0]:
        exports = json.loads(row[0])
        is_public = function_name in exports
    
    # Find all call sites
    call_sites = []
    cursor = db_conn.execute('SELECT path FROM files')
    
    for (path,) in cursor.fetchall():
        fpath = Path(CONFIG['project_root']) / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            # Find calls to this function
            pattern = rf'\b{re.escape(function_name)}\s*\('
            matches = list(re.finditer(pattern, content))
            
            if matches:
                # Get line numbers
                lines = content.split('\n')
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    # Get surrounding context
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 1)
                    context = '\n    '.join(lines[context_start:context_end])
                    
                    call_sites.append({
                        'file': path,
                        'line': line_num,
                        'context': context[:200]  # Limit context
                    })
        except:
            continue
    
    # Calculate severity
    num_sites = len(call_sites)
    if num_sites == 0:
        severity = "✅ SAFE"
        severity_desc = "No call sites found - safe to modify"
    elif num_sites <= 3:
        severity = "⚠️ LOW RISK"
        severity_desc = f"Only {num_sites} call sites - easy to fix"
    elif num_sites <= 10:
        severity = "⚠️ MODERATE RISK"
        severity_desc = f"{num_sites} call sites - needs careful review"
    else:
        severity = "🚨 HIGH RISK"
        severity_desc = f"{num_sites} call sites - significant refactoring needed"
    
    # Build report
    result.append(f"📊 **Call Sites Found**: {num_sites}")
    result.append(f"🔐 **Public API**: {'Yes - exported in module' if is_public else 'No - internal function'}")
    result.append(f"⚡ **Severity**: {severity}")
    result.append(f"📝 **Assessment**: {severity_desc}\n")
    
    if is_public:
        result.append("⚠️ WARNING: This is a public API. Changes may break external code!\n")
    
    if call_sites:
        # Group by file
        by_file = {}
        for site in call_sites:
            if site['file'] not in by_file:
                by_file[site['file']] = []
            by_file[site['file']].append(site)
        
        result.append(f"📁 **Affected Files** ({len(by_file)} files):\n")
        
        for file, sites in sorted(by_file.items())[:10]:  # Limit to 10 files
            result.append(f"  • {file} ({len(sites)} occurrences)")
            for site in sites[:2]:  # Show first 2 per file
                result.append(f"    Line {site['line']}")
        
        if len(by_file) > 10:
            result.append(f"\n  ... and {len(by_file) - 10} more files")
    else:
        result.append("✅ No call sites found - safe to modify or remove")
    
    result.append(f"\n💡 Tip: Use get_call_tree() for detailed call flow analysis")
    
    return "\n".join(result)

@mcp.tool()
def check_breaking_changes(function_name: str, file_path: str) -> str:
    """
    Analyze impact of modifying a function/class signature.
    
    Args:
        function_name: Name of function/class to analyze
        file_path: File containing the function
    
    Critical for:
    - Refactoring safety: Know what will break
    - Impact assessment: How many files affected
    - Risk evaluation: Public API vs internal
    
    Returns:
    - Number of call sites
    - List of affected files
    - Severity rating (safe/moderate/dangerous)
    - Public API status
    """
    return _check_breaking_changes_impl(function_name, file_path)

def _find_usage_examples_impl(function_name: str, file_path: str | None = None, limit: int = 5) -> str:
    """Implementation of find_usage_examples"""
    lazy_scan()
    
    result = [f"📚 Usage Examples for '{function_name}':\n"]
    
    examples = []
    cursor = db_conn.execute('SELECT path FROM files')
    
    # Skip the definition file if provided
    skip_file = file_path
    
    for (path,) in cursor.fetchall():
        if path == skip_file:
            continue  # Skip definition file, show usage elsewhere
            
        fpath = Path(CONFIG['project_root']) / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Find usage (not definition)
            pattern = rf'\b{re.escape(function_name)}\s*\('
            
            for i, line in enumerate(lines):
                # Skip if this is the definition line
                if re.match(rf'\s*(def|class)\s+{re.escape(function_name)}\b', line):
                    continue
                
                if re.search(pattern, line):
                    # Get surrounding context
                    context_start = max(0, i - 1)
                    context_end = min(len(lines), i + 2)
                    context_lines = lines[context_start:context_end]
                    
                    examples.append({
                        'file': path,
                        'line': i + 1,
                        'context': '\n'.join(context_lines),
                        'usage_line': line.strip()
                    })
                    
                    if len(examples) >= limit * 3:  # Collect more than needed
                        break
        except:
            continue
        
        if len(examples) >= limit * 3:
            break
    
    if not examples:
        result.append(f"❌ No usage examples found for '{function_name}'")
        result.append(f"\nPossible reasons:")
        result.append(f"  • Function is defined but not yet used")
        result.append(f"  • Function name is incorrect")
        result.append(f"  • Files haven't been indexed yet")
        result.append(f"\n💡 Try: search_by_export('{function_name}') to verify it exists")
        return "\n".join(result)
    
    # Show top examples
    for i, ex in enumerate(examples[:limit], 1):
        result.append(f"\n**Example {i}**: {ex['file']}:{ex['line']}")
        result.append(f"```")
        result.append(ex['context'])
        result.append(f"```")
    
    if len(examples) > limit:
        result.append(f"\n... found {len(examples) - limit} more examples")
        result.append(f"(use limit parameter to see more)")
    
    result.append(f"\n💡 Found {min(limit, len(examples))} of {len(examples)} total usages")
    
    return "\n".join(result)

@mcp.tool()
def find_usage_examples(function_name: str, file_path: str | None = None, limit: int = 5) -> str:
    """
    Find real usage examples of a function/class across the codebase.
    
    Args:
        function_name: Function or class name to find examples for
        file_path: Optional file containing the function (helps filter)
        limit: Maximum number of examples (default: 5)
    
    Use this when:
    - "How is this function used?"
    - Learning API contracts from actual usage
    - Understanding parameter patterns
    - Finding usage best practices
    
    Returns examples with file, line number, and surrounding context.
    """
    return _find_usage_examples_impl(function_name, file_path, limit)

def _find_todo_and_fixme_impl(tag_type: str = "TODO", search_term: str | None = None, limit: int = 20) -> str:
    """Implementation of find_todo_and_fixme"""
    lazy_scan()
    
    tag_type = tag_type.upper()
    valid_tags = ["TODO", "FIXME", "HACK", "XXX", "NOTE", "BUG"]
    
    if tag_type not in valid_tags:
        return f"❌ Invalid tag type. Use one of: {', '.join(valid_tags)}"
    
    result = [f"🔍 Searching for {tag_type} comments" + (f" matching '{search_term}'" if search_term else "") + ":\n"]
    
    findings = []
    cursor = db_conn.execute('SELECT path FROM files')
    
    for (path,) in cursor.fetchall():
        fpath = Path(CONFIG['project_root']) / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Match comments with tag
            pattern = rf'#.*{tag_type}:?\s*(.+)$'
            
            for i, line in enumerate(lines):
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    comment_text = match.group(1).strip()
                    
                    # Filter by search term if provided
                    if search_term and search_term.lower() not in comment_text.lower():
                        continue
                    
                    # Get surrounding context (code being marked)
                    context_start = max(0, i - 1)
                    context_end = min(len(lines), i + 2)
                    context = '\n    '.join(lines[context_start:context_end])
                    
                    findings.append({
                        'file': path,
                        'line': i + 1,
                        'comment': comment_text,
                        'context': context[:300]  # Limit context
                    })
                    
                    if len(findings) >= limit * 2:
                        break
        except:
            continue
        
        if len(findings) >= limit * 2:
            break
    
    if not findings:
        result.append(f"✅ No {tag_type} comments found" + (f" matching '{search_term}'" if search_term else ""))
        result.append(f"\nThis could mean:")
        result.append(f"  • Clean codebase (good!)")
        result.append(f"  • Different tag conventions used")
        result.append(f"  • Files not yet indexed")
        return "\n".join(result)
    
    # Group by file
    by_file = {}
    for finding in findings:
        if finding['file'] not in by_file:
            by_file[finding['file']] = []
        by_file[finding['file']].append(finding)
    
    result.append(f"📊 Found {len(findings)} {tag_type} comments in {len(by_file)} files:\n")
    
    # Show findings grouped by file
    for file, items in sorted(by_file.items())[:limit]:
        result.append(f"\n📁 **{file}** ({len(items)} items):")
        for item in items[:3]:  # Show first 3 per file
            result.append(f"  • Line {item['line']}: {item['comment']}")
    
    if len(findings) > limit:
        result.append(f"\n... {len(findings) - limit} more {tag_type} comments found")
        result.append(f"(increase limit parameter to see more)")
    
    # Priority hints
    if tag_type == "FIXME":
        result.append(f"\n⚠️ FIXME comments indicate bugs or issues that need attention")
    elif tag_type == "HACK":
        result.append(f"\n⚠️ HACK comments indicate technical debt or workarounds")
    elif tag_type == "XXX":
        result.append(f"\n🚨 XXX comments often indicate critical issues")
    
    result.append(f"\n💡 Tip: Use search_term parameter to filter by keyword")
    
    return "\n".join(result)

@mcp.tool()
def find_todo_and_fixme(tag_type: str = "TODO", search_term: str | None = None, limit: int = 20) -> str:
    """
    Search all TODO, FIXME, HACK, XXX comments with context.
    
    Args:
        tag_type: Type of tag (TODO/FIXME/HACK/XXX/NOTE)
        search_term: Optional keyword to filter results
        limit: Maximum results (default: 20)
    
    Critical for:
    - Technical debt awareness: Know what needs fixing
    - Avoiding duplicate work: Don't fix what's already marked
    - Context for changes: Understand known issues
    - Planning: Prioritize tech debt
    
    Returns grouped comments with file, line, and context.
    """
    return _find_todo_and_fixme_impl(tag_type, search_term, limit)

async def _get_file_history_summary_impl_async(file_path: str, days_back: int = 90) -> str:
    """Async implementation of get_file_history_summary using asyncio subprocess"""
    import asyncio
    
    lazy_scan()
    
    result = [f"📜 Git History for '{file_path}' (last {days_back} days):\n"]
    
    fpath = Path(CONFIG['project_root']) / file_path
    if not fpath.exists():
        return f"❌ File not found: {file_path}"
    
    try:
        logger.debug(f"Running git log for {file_path}...")
        
        # Quick check: is git available?
        try:
            proc = await asyncio.create_subprocess_exec(
                'git', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(proc.communicate(), timeout=2)
            if proc.returncode != 0:
                return f"❌ Git not found\n💡 Install Git to use this tool"
        except (FileNotFoundError, asyncio.TimeoutError):
            return f"❌ Git not found\n💡 Install Git to use this tool"
        
        # Get commit count
        proc = await asyncio.create_subprocess_exec(
            'git', 'log', '--oneline', f'--since={days_back} days ago', '--', file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=CONFIG['project_root']
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
        
        logger.debug(f"Git log completed with returncode={proc.returncode}")
        
        if proc.returncode != 0:
            logger.debug(f"Git error: {stderr.decode()}")
            return f"❌ Git not available or not a git repository\n💡 This tool requires Git to be installed"
        
        commits = stdout.decode().strip().split('\n')
        commit_count = len([c for c in commits if c])
        
        # Get contributors
        proc = await asyncio.create_subprocess_exec(
            'git', 'log', '--format=%an', f'--since={days_back} days ago', '--', file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=CONFIG['project_root']
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        
        authors = [a for a in stdout.decode().strip().split('\n') if a]
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get last modified date
        proc = await asyncio.create_subprocess_exec(
            'git', 'log', '-1', '--format=%ar', '--', file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=CONFIG['project_root']
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        last_modified = stdout.decode().strip() or "Unknown"
        
        # Calculate metrics
        months = days_back / 30
        commits_per_month = commit_count / months if months > 0 else 0
        
        # Risk rating
        if commits_per_month >= 10:
            risk = "🔴 HIGH"
            risk_desc = "Very frequently changed - high fragility risk"
        elif commits_per_month >= 5:
            risk = "🟡 MEDIUM"
            risk_desc = "Moderately active - some risk of conflicts"
        elif commits_per_month >= 1:
            risk = "🟢 LOW"
            risk_desc = "Stable with occasional updates"
        else:
            risk = "✅ VERY LOW"
            risk_desc = "Rarely changed - very stable"
        
        # Build report
        result.append(f"📊 **Commits** ({days_back} days): {commit_count}")
        result.append(f"📈 **Change Rate**: {commits_per_month:.1f} commits/month")
        result.append(f"🕐 **Last Modified**: {last_modified}")
        result.append(f"⚡ **Risk Level**: {risk}")
        result.append(f"📝 **Assessment**: {risk_desc}\n")
        
        if top_authors:
            result.append(f"👥 **Top Contributors**:")
            for author, count in top_authors:
                percentage = (count / commit_count * 100) if commit_count > 0 else 0
                result.append(f"  • {author}: {count} commits ({percentage:.0f}%)")
        
        result.append(f"\n💡 Expert to ask: {top_authors[0][0] if top_authors else 'Unknown'}")
        
        if commit_count == 0:
            result.append(f"\n✅ No recent commits - file is stable")
        
    except asyncio.TimeoutError:
        return f"❌ Git command timed out\n💡 Large repository - try shorter days_back"
    except FileNotFoundError:
        return f"❌ Git not found\n💡 Install Git to use this tool"
    except Exception as e:
        return f"❌ Error analyzing git history: {str(e)}"
    
    return "\n".join(result)

@mcp.tool()
async def get_file_history_summary(file_path: str, days_back: int = 90) -> str:
    """
    Git history analysis - who changes this file, how often, recent activity.
    
    Args:
        file_path: File to analyze
        days_back: How many days of history (default: 90)
    
    Use this for:
    - Risk assessment: Frequently changed = fragile
    - Expert identification: Who to ask for context
    - Change patterns: Stable vs active development
    - Impact understanding: Recent activity level
    
    Returns commit count, contributors, frequency, and risk rating.
    """
    return await _get_file_history_summary_impl_async(file_path, days_back)

def _get_test_coverage_impl(file_path: str) -> str:
    """Implementation of get_test_coverage"""
    lazy_scan()
    
    result = [f"🧪 Test Coverage Analysis for '{file_path}':\n"]
    
    fpath = Path(CONFIG['project_root']) / file_path
    if not fpath.exists():
        return f"❌ File not found: {file_path}"
    
    try:
        # Read the file to get functions
        content = fpath.read_text(encoding='utf-8', errors='ignore')
        
        # Extract function/class names
        functions = re.findall(r'def\s+([a-zA-Z_]\w*)\s*\(', content)
        classes = re.findall(r'class\s+([a-zA-Z_]\w*)', content)
        
        # Filter out private functions
        public_functions = [f for f in functions if not f.startswith('_')]
        
        if not public_functions and not classes:
            return f"⚠️ No public functions or classes found in {file_path}"
        
        result.append(f"📦 **Found**:")
        if classes:
            result.append(f"  • {len(classes)} classes: {', '.join(classes[:5])}")
        if public_functions:
            result.append(f"  • {len(public_functions)} public functions: {', '.join(public_functions[:5])}")
        result.append("")
        
        # Find test files (heuristic approach)
        test_files = []
        cursor = db_conn.execute('SELECT path FROM files')
        
        base_name = Path(file_path).stem
        
        for (test_path,) in cursor.fetchall():
            # Look for test files that might test this file
            if 'test' in test_path.lower() and base_name.lower() in test_path.lower():
                test_files.append(test_path)
        
        # Count tested items by searching test files
        tested_items = set()
        
        for test_file in test_files:
            test_fpath = Path(CONFIG['project_root']) / test_file
            if not test_fpath.exists():
                continue
            
            try:
                test_content = test_fpath.read_text(encoding='utf-8', errors='ignore')
                
                # Check which functions/classes are referenced in tests
                for func in public_functions:
                    if re.search(rf'\b{re.escape(func)}\b', test_content):
                        tested_items.add(func)
                
                for cls in classes:
                    if re.search(rf'\b{re.escape(cls)}\b', test_content):
                        tested_items.add(cls)
            except:
                continue
        
        # Calculate coverage
        total_items = len(public_functions) + len(classes)
        tested_count = len(tested_items)
        coverage_pct = (tested_count / total_items * 100) if total_items > 0 else 0
        
        # Rating
        if coverage_pct >= 80:
            rating = "✅ EXCELLENT"
            color = "🟢"
        elif coverage_pct >= 60:
            rating = "👍 GOOD"
            color = "🟡"
        elif coverage_pct >= 40:
            rating = "⚠️ MODERATE"
            color = "🟠"
        else:
            rating = "🔴 LOW"
            color = "🔴"
        
        result.append(f"{color} **Estimated Coverage**: {coverage_pct:.0f}% ({tested_count}/{total_items} items)")
        result.append(f"📊 **Rating**: {rating}\n")
        
        if tested_items:
            result.append(f"✅ **Tested** ({len(tested_items)} items):")
            for item in sorted(tested_items)[:10]:
                result.append(f"  • {item}")
            if len(tested_items) > 10:
                result.append(f"  ... and {len(tested_items) - 10} more")
            result.append("")
        
        untested = set(public_functions + classes) - tested_items
        if untested:
            result.append(f"❌ **Untested** ({len(untested)} items):")
            for item in sorted(untested)[:10]:
                result.append(f"  • {item}")
            if len(untested) > 10:
                result.append(f"  ... and {len(untested) - 10} more")
            result.append("")
        
        if test_files:
            result.append(f"📁 **Test Files** ({len(test_files)}):")
            for tf in test_files[:5]:
                result.append(f"  • {tf}")
            if len(test_files) > 5:
                result.append(f"  ... and {len(test_files) - 5} more")
        else:
            result.append(f"⚠️ **No test files found**")
            result.append(f"  Suggestion: Create tests/test_{base_name}.py")
        
        # Recommendations
        result.append(f"\n💡 **Recommendations**:")
        if coverage_pct < 60:
            result.append(f"  • Add tests for untested functions")
            result.append(f"  • Target: 60%+ coverage for production code")
        if not test_files:
            result.append(f"  • Create test file: tests/test_{base_name}.py")
        if coverage_pct >= 80:
            result.append(f"  • Excellent coverage - maintain this level!")
        
    except Exception as e:
        return f"❌ Error analyzing coverage: {str(e)}"
    
    return "\n".join(result)

@mcp.tool()
def get_test_coverage(file_path: str) -> str:
    """
    Show test coverage for a specific file/module.
    
    Args:
        file_path: File to check coverage for
    
    Use this for:
    - Risk assessment: Is this tested?
    - Quality check: What's untested?
    - Test discovery: Where are the tests?
    - Refactoring safety: High coverage = safer changes
    
    Returns coverage estimate, test file locations, and recommendations.
    """
    return _get_test_coverage_impl(file_path)

# ============================================================================
# PHASE 5: ZERO-LLM STATIC ANALYSIS TOOLS
# ============================================================================

@mcp.tool()
def get_code_metrics_summary(detailed: bool = False) -> str:
    """
    Comprehensive static analysis metrics across entire project.
    
    Provides objective code quality dashboard with:
    - Project statistics (files, lines, comments)
    - Complexity metrics (cyclomatic complexity estimates)
    - Function statistics (count, avg length, long functions)
    - Documentation coverage (docstrings, comments)
    - Code smells (magic numbers, long params, deep nesting)
    - Maintainability index (0-100 score)
    
    Args:
        detailed: Show detailed file-by-file breakdown (default: False)
    
    Use this for:
    - Project health assessment
    - Technical debt identification
    - Code review prioritization
    - Quality gate checks
    - Onboarding (understand codebase scope)
    
    Returns comprehensive metrics with actionable recommendations.
    Zero LLM calls - pure static analysis.
    """
    try:
        project_root = Path(CONFIG["project_root"]).resolve()
        
        # Initialize counters
        total_files = 0
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        total_functions = 0
        total_classes = 0
        function_lengths = []
        param_counts = []
        
        files_with_docstrings = 0
        high_complexity_files = []
        long_functions = []
        code_smells = {
            "magic_numbers": 0,
            "long_parameter_lists": 0,
            "deep_nesting": 0,
            "dead_imports": 0,
            "long_lines": 0
        }
        
        file_metrics = []
        
        # Scan all files
        for ext in CONFIG["watched_extensions"]:
            for fp in project_root.rglob(f"*{ext}"):
                if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                    try:
                        if fp.stat().st_size // 1024 > CONFIG["max_file_size_kb"]:
                            continue
                        
                        with open(fp, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                        
                        total_files += 1
                        file_total_lines = len(lines)
                        total_lines += file_total_lines
                        
                        # Classify lines
                        file_code_lines = 0
                        file_comment_lines = 0
                        file_blank_lines = 0
                        file_has_docstring = False
                        
                        in_multiline_comment = False
                        for line in lines:
                            stripped = line.strip()
                            
                            if not stripped:
                                file_blank_lines += 1
                                blank_lines += 1
                            elif stripped.startswith('"""') or stripped.startswith("'''"):
                                file_comment_lines += 1
                                comment_lines += 1
                                file_has_docstring = True
                                if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                                    in_multiline_comment = not in_multiline_comment
                            elif in_multiline_comment:
                                file_comment_lines += 1
                                comment_lines += 1
                            elif stripped.startswith('#'):
                                file_comment_lines += 1
                                comment_lines += 1
                            elif stripped.startswith('//') or stripped.startswith('/*'):
                                file_comment_lines += 1
                                comment_lines += 1
                            else:
                                file_code_lines += 1
                                code_lines += 1
                                
                                # Check for long lines
                                if len(line) > 120:
                                    code_smells["long_lines"] += 1
                        
                        if file_has_docstring:
                            files_with_docstrings += 1
                        
                        # Extract functions and complexity using AST/radon for Python
                        file_functions = 0
                        file_classes = 0
                        file_complexity = 0
                        
                        # Use radon for Python files when available
                        if fp.suffix == '.py' and HAS_RADON:
                            try:
                                # Use radon for production-quality cyclomatic complexity
                                complexity_results = cc_visit(content)
                                for result in complexity_results:
                                    file_functions += 1
                                    total_functions += 1
                                    
                                    # Get function metrics from radon
                                    func_complexity = result.complexity
                                    func_lines = result.endline - result.lineno
                                    
                                    file_complexity += func_complexity
                                    function_lengths.append(min(func_lines, 50))
                                    
                                    # Count parameters from name field (contains signature)
                                    param_count = len([p for p in result.name.split('(')[1].split(')')[0].split(',') if p.strip() and p.strip() != 'self']) if '(' in result.name else 0
                                    param_counts.append(param_count)
                                    if param_count > 5:
                                        code_smells["long_parameter_lists"] += 1
                                    
                                    if func_lines > 100:
                                        long_functions.append({
                                            "file": str(fp.relative_to(project_root)),
                                            "function": result.name.split('(')[0],
                                            "lines": func_lines
                                        })
                                    
                                    # High complexity threshold (radon uses McCabe)
                                    if func_complexity > 10:
                                        code_smells["deep_nesting"] += 1
                                
                                # Find classes using AST
                                try:
                                    tree = ast.parse(content)
                                    file_classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                                    total_classes += file_classes
                                except:
                                    pass
                                    
                            except Exception as e:
                                logger.debug(f"Radon analysis failed for {fp}, falling back to regex: {e}")
                                # Fallback to regex method below
                                HAS_RADON_FOR_FILE = False
                            else:
                                HAS_RADON_FOR_FILE = True
                        else:
                            HAS_RADON_FOR_FILE = False
                        
                        # Fallback regex method for non-Python or if radon fails
                        if not HAS_RADON_FOR_FILE or fp.suffix != '.py':
                            # Find functions (Python, JS, TS)
                            function_pattern = r'(?:def|function|const\s+\w+\s*=\s*(?:async\s+)?\()\s+(\w+)\s*\('
                            for match in re.finditer(function_pattern, content):
                                file_functions += 1
                                total_functions += 1
                                
                                # Get function body to analyze
                                func_start = match.start()
                                func_content = content[func_start:func_start + 2000]  # Sample
                                
                                # Count parameters
                                param_match = re.search(r'\((.*?)\)', func_content)
                                if param_match:
                                    params = [p.strip() for p in param_match.group(1).split(',') if p.strip() and p.strip() != 'self']
                                    param_count = len(params)
                                    param_counts.append(param_count)
                                    if param_count > 5:
                                        code_smells["long_parameter_lists"] += 1
                                
                                # Estimate function length
                                func_lines = len(func_content.split('\n'))
                                function_lengths.append(min(func_lines, 50))
                                
                                if func_lines > 100:
                                    long_functions.append({
                                        "file": str(fp.relative_to(project_root)),
                                        "function": match.group(1) if match.groups() else "unknown",
                                        "lines": func_lines
                                    })
                                
                                # Estimate complexity (count branches)
                                complexity = len(re.findall(r'\b(if|elif|else|for|while|and|or|try|except|case)\b', func_content))
                                file_complexity += complexity
                                
                                # Check for deep nesting
                                max_indent = 0
                                for line in func_content.split('\n'):
                                    if line.strip():
                                        indent = len(line) - len(line.lstrip())
                                        max_indent = max(max_indent, indent)
                                if max_indent > 16:  # 4+ levels of nesting
                                    code_smells["deep_nesting"] += 1
                            
                            # Find classes
                            class_pattern = r'class\s+(\w+)'
                            file_classes = len(re.findall(class_pattern, content))
                            total_classes += file_classes
                        
                        # Find magic numbers (numeric literals not 0, 1, -1)
                        magic_numbers = re.findall(r'\b(?<!\.)\d{2,}\b(?!\.)', content)
                        code_smells["magic_numbers"] += len([n for n in magic_numbers if n not in ['0', '1', '2', '10', '100']])
                        
                        # Find dead imports (imported but not used)
                        if fp.suffix == '.py':
                            import_pattern = r'(?:from\s+[\w.]+\s+)?import\s+([\w\s,]+)'
                            for match in re.finditer(import_pattern, content):
                                imports = [i.strip() for i in match.group(1).split(',')]
                                for imp in imports:
                                    imp_name = imp.split()[0] if imp else ''
                                    if imp_name and content.count(imp_name) == 1:  # Only appears in import
                                        code_smells["dead_imports"] += 1
                        
                        # Calculate file complexity score
                        if file_functions > 0:
                            avg_complexity = file_complexity / file_functions
                        else:
                            avg_complexity = 0
                        
                        if avg_complexity > 10 or file_complexity > 30:
                            high_complexity_files.append({
                                "file": str(fp.relative_to(project_root)),
                                "complexity": file_complexity,
                                "functions": file_functions
                            })
                        
                        file_metrics.append({
                            "file": str(fp.relative_to(project_root)),
                            "lines": file_total_lines,
                            "code": file_code_lines,
                            "comments": file_comment_lines,
                            "functions": file_functions,
                            "classes": file_classes,
                            "complexity": file_complexity
                        })
                        
                    except Exception as e:
                        logger.debug(f"Error analyzing {fp}: {e}")
        
        # Calculate maintainability index using radon when available
        # Based on Halstead Volume, Cyclomatic Complexity, Lines of Code
        # Formula: 171 - 5.2 * ln(Halstead Volume) - 0.23 * CC - 16.2 * ln(LOC)
        import math
        
        if HAS_RADON and file_metrics:
            # Use radon's production-quality MI calculation for Python files
            mi_scores = []
            for fm in file_metrics:
                if fm["file"].endswith('.py'):
                    try:
                        fpath = project_root / fm["file"]
                        with open(fpath, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        # mi_visit returns a float (maintainability index)
                        mi_score = mi_visit(content, multi=False)
                        if isinstance(mi_score, (int, float)) and mi_score > 0:
                            mi_scores.append(mi_score)
                    except:
                        pass
            
            if mi_scores:
                maintainability = sum(mi_scores) / len(mi_scores)
            else:
                # Fallback to simplified calculation
                avg_complexity = (sum(f["complexity"] for f in file_metrics) / len(file_metrics)) if file_metrics else 0
                avg_file_size = total_lines / total_files if total_files > 0 else 0
                maintainability = max(0, min(100, 
                    171 - 0.23 * avg_complexity - 16.2 * math.log(max(1, avg_file_size))
                ))
        else:
            # Simplified version using available metrics
            avg_complexity = (sum(f["complexity"] for f in file_metrics) / len(file_metrics)) if file_metrics else 0
            avg_file_size = total_lines / total_files if total_files > 0 else 0
            maintainability = max(0, min(100, 
                171 - 0.23 * avg_complexity - 16.2 * math.log(max(1, avg_file_size))
            ))
        
        # Build result
        result = [""]
        result.append("=" * 70)
        result.append("📊 CODE METRICS SUMMARY")
        result.append("=" * 70)
        result.append("")
        
        # Project Statistics
        result.append("📁 **PROJECT STATISTICS**")
        result.append(f"  Total Files:    {total_files:,}")
        result.append(f"  Total Lines:    {total_lines:,}")
        result.append(f"  Code Lines:     {code_lines:,} ({100*code_lines/max(1,total_lines):.1f}%)")
        result.append(f"  Comment Lines:  {comment_lines:,} ({100*comment_lines/max(1,total_lines):.1f}%)")
        result.append(f"  Blank Lines:    {blank_lines:,} ({100*blank_lines/max(1,total_lines):.1f}%)")
        result.append("")
        
        # Complexity
        result.append("🔥 **COMPLEXITY METRICS**")
        result.append(f"  Average per File: {avg_complexity:.1f}")
        if file_metrics:
            complexities = [f["complexity"] for f in file_metrics]
            result.append(f"  Median:           {sorted(complexities)[len(complexities)//2]}")
            result.append(f"  Max:              {max(complexities)}")
        
        if high_complexity_files:
            result.append(f"\n  ⚠️  High Complexity Files ({len(high_complexity_files)}):")
            for fc in sorted(high_complexity_files, key=lambda x: x["complexity"], reverse=True)[:5]:
                result.append(f"    • {fc['file']}: complexity={fc['complexity']}, functions={fc['functions']}")
            if len(high_complexity_files) > 5:
                result.append(f"    ... and {len(high_complexity_files) - 5} more")
        result.append("")
        
        # Function Statistics
        result.append("⚙️  **FUNCTION STATISTICS**")
        result.append(f"  Total Functions: {total_functions:,}")
        result.append(f"  Total Classes:   {total_classes:,}")
        if function_lengths:
            avg_length = sum(function_lengths) / len(function_lengths)
            result.append(f"  Avg Length:      {avg_length:.1f} lines")
            result.append(f"  Median Length:   {sorted(function_lengths)[len(function_lengths)//2]} lines")
        
        if long_functions:
            result.append(f"\n  📏 Long Functions ({len(long_functions)}):")
            for lf in sorted(long_functions, key=lambda x: x["lines"], reverse=True)[:5]:
                result.append(f"    • {lf['file']}::{lf['function']} ({lf['lines']} lines)")
            if len(long_functions) > 5:
                result.append(f"    ... and {len(long_functions) - 5} more")
        result.append("")
        
        # Documentation
        result.append("📚 **DOCUMENTATION**")
        doc_coverage = (100 * files_with_docstrings / max(1, total_files))
        result.append(f"  Files with Docstrings: {files_with_docstrings}/{total_files} ({doc_coverage:.1f}%)")
        result.append(f"  Comment Ratio:         {100*comment_lines/max(1,code_lines):.1f}%")
        
        if doc_coverage < 60:
            result.append(f"  ⚠️  Low documentation coverage")
        elif doc_coverage >= 80:
            result.append(f"  ✅ Good documentation coverage")
        result.append("")
        
        # Code Smells
        result.append("🔍 **CODE SMELLS**")
        result.append(f"  Magic Numbers:        {code_smells['magic_numbers']}")
        result.append(f"  Long Parameter Lists: {code_smells['long_parameter_lists']} (>5 params)")
        result.append(f"  Deep Nesting:         {code_smells['deep_nesting']} (>4 levels)")
        result.append(f"  Dead Imports:         {code_smells['dead_imports']}")
        result.append(f"  Long Lines:           {code_smells['long_lines']} (>120 chars)")
        
        total_smells = sum(code_smells.values())
        if total_smells == 0:
            result.append(f"  ✅ No major code smells detected!")
        elif total_smells < 50:
            result.append(f"  ✓  Few code smells - good quality")
        elif total_smells < 200:
            result.append(f"  ⚠️  Moderate code smells - review recommended")
        else:
            result.append(f"  ❌ Many code smells - refactoring needed")
        result.append("")
        
        # Maintainability Index
        result.append("💯 **MAINTAINABILITY INDEX**")
        result.append(f"  Score: {maintainability:.1f}/100")
        if maintainability >= 80:
            result.append(f"  ✅ Excellent - Easy to maintain")
        elif maintainability >= 60:
            result.append(f"  ✓  Good - Reasonably maintainable")
        elif maintainability >= 40:
            result.append(f"  ⚠️  Fair - Maintenance challenges ahead")
        else:
            result.append(f"  ❌ Poor - Significant refactoring recommended")
        result.append("")
        
        # Recommendations
        result.append("💡 **RECOMMENDATIONS**")
        recommendations = []
        
        if avg_complexity > 15:
            recommendations.append(f"  • Reduce complexity: Average {avg_complexity:.1f} is high (target: <10)")
        if long_functions:
            recommendations.append(f"  • Refactor {len(long_functions)} long functions (target: <50 lines)")
        if doc_coverage < 70:
            recommendations.append(f"  • Improve documentation: {doc_coverage:.0f}% coverage (target: >70%)")
        if code_smells["magic_numbers"] > 50:
            recommendations.append(f"  • Replace {code_smells['magic_numbers']} magic numbers with named constants")
        if code_smells["dead_imports"] > 20:
            recommendations.append(f"  • Remove {code_smells['dead_imports']} unused imports")
        if code_smells["long_parameter_lists"] > 10:
            recommendations.append(f"  • Refactor {code_smells['long_parameter_lists']} functions with >5 parameters")
        
        if recommendations:
            result.extend(recommendations)
        else:
            result.append(f"  ✅ Code quality is excellent - keep it up!")
        
        result.append("")
        result.append("=" * 70)
        
        # Detailed breakdown
        if detailed and file_metrics:
            result.append("")
            result.append("📋 **DETAILED FILE BREAKDOWN**")
            result.append("")
            result.append(f"{'File':<50} {'Lines':>8} {'Code':>8} {'Funcs':>6} {'Cmplx':>6}")
            result.append("-" * 80)
            for fm in sorted(file_metrics, key=lambda x: x["complexity"], reverse=True)[:20]:
                result.append(f"{fm['file']:<50} {fm['lines']:>8} {fm['code']:>8} {fm['functions']:>6} {fm['complexity']:>6}")
            if len(file_metrics) > 20:
                result.append(f"... and {len(file_metrics) - 20} more files")
        
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error in get_code_metrics_summary: {e}", exc_info=True)
        return f"❌ Error analyzing code metrics: {str(e)}"

@mcp.tool()
def get_import_graph(include_external: bool = False) -> str:
    """
    Visual dependency graph showing all imports/exports across codebase.
    
    Analyzes import relationships to provide:
    - Module count and total import connections
    - Circular dependencies (import cycles)
    - Most imported modules (high coupling)
    - Least connected modules (potential orphans)
    - Import depth (dependency layers)
    - Orphaned files (no imports, not imported)
    - Full graph structure (who imports what)
    
    Args:
        include_external: Include external library imports (default: False, internal only)
    
    Use this for:
    - Architecture visualization
    - Circular dependency detection
    - Refactoring planning (understand impact)
    - Dead code identification (orphans)
    - Module coupling analysis
    - Onboarding (understand structure)
    
    Returns dependency graph with actionable insights.
    Zero LLM calls - pure graph analysis.
    """
    try:
        project_root = Path(CONFIG["project_root"]).resolve()
        
        # Build import graph
        graph = {}  # {file: {"imports": [...], "imported_by": [...]}}
        all_files = set()
        external_imports = set()
        
        # Scan all files for imports
        for ext in CONFIG["watched_extensions"]:
            for fp in project_root.rglob(f"*{ext}"):
                if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                    try:
                        if fp.stat().st_size // 1024 > CONFIG["max_file_size_kb"]:
                            continue
                        
                        file_key = str(fp.relative_to(project_root))
                        all_files.add(file_key)
                        
                        if file_key not in graph:
                            graph[file_key] = {"imports": [], "imported_by": []}
                        
                        with open(fp, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Extract imports based on file type
                        if fp.suffix == '.py':
                            # Python: Use AST for production-quality import extraction
                            modules = parse_imports_ast(content)
                            for module in modules:
                                if module:
                                    # Check if internal or external
                                    potential_file = module.replace('.', os.sep) + '.py'
                                    is_internal = False
                                    
                                    # Try to find matching internal file
                                    for search_path in [potential_file, module + '.py', module + '/__init__.py']:
                                        full_path = project_root / search_path
                                        if full_path.exists():
                                            imported_file = str(full_path.relative_to(project_root))
                                            if imported_file in all_files or (project_root / imported_file).exists():
                                                graph[file_key]["imports"].append(imported_file)
                                                if imported_file not in graph:
                                                    graph[imported_file] = {"imports": [], "imported_by": []}
                                                graph[imported_file]["imported_by"].append(file_key)
                                                is_internal = True
                                                break
                                    
                                    if not is_internal and include_external:
                                        external_imports.add(module.split('.')[0])
                        
                        elif fp.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                            # JavaScript/TypeScript: import X from 'Y', require('Y')
                            for match in re.finditer(r'(?:import\s+.*?\s+from\s+["\']([^"\']+)["\']|require\(["\']([^"\']+)["\']\))', content):
                                module = match.group(1) or match.group(2)
                                if module and not module.startswith('.'):
                                    if include_external:
                                        external_imports.add(module.split('/')[0])
                                elif module:
                                    # Relative import - resolve it
                                    import_path = (fp.parent / module).resolve()
                                    # Try with extensions
                                    for try_ext in ['', '.js', '.ts', '.jsx', '.tsx', '/index.js', '/index.ts']:
                                        try_path = Path(str(import_path) + try_ext)
                                        if try_path.exists() and try_path.is_file():
                                            try:
                                                imported_file = str(try_path.relative_to(project_root))
                                                if imported_file in all_files or (project_root / imported_file).exists():
                                                    graph[file_key]["imports"].append(imported_file)
                                                    if imported_file not in graph:
                                                        graph[imported_file] = {"imports": [], "imported_by": []}
                                                    graph[imported_file]["imported_by"].append(file_key)
                                                    break
                                            except ValueError:
                                                pass
                        
                    except Exception as e:
                        logger.debug(f"Error analyzing imports in {fp}: {e}")
        
        # Calculate metrics
        total_modules = len(graph)
        total_imports = sum(len(data["imports"]) for data in graph.values())
        
        # Find circular dependencies using DFS
        def find_cycles(graph_dict):
            cycles = []
            visited = set()
            rec_stack = []
            
            def dfs(node, path):
                if node in rec_stack:
                    # Found cycle
                    cycle_start = rec_stack.index(node)
                    cycle = rec_stack[cycle_start:] + [node]
                    if cycle not in cycles and list(reversed(cycle)) not in cycles:
                        cycles.append(cycle)
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.append(node)
                
                for neighbor in graph_dict.get(node, {}).get("imports", []):
                    dfs(neighbor, path + [neighbor])
                
                rec_stack.pop()
            
            for node in graph_dict:
                if node not in visited:
                    dfs(node, [node])
            
            return cycles
        
        circular_deps = find_cycles(graph)
        
        # Find most/least imported
        import_counts = [(file, len(data["imported_by"])) for file, data in graph.items()]
        most_imported = sorted(import_counts, key=lambda x: x[1], reverse=True)[:10]
        least_connected = [(file, len(data["imports"]) + len(data["imported_by"])) 
                          for file, data in graph.items()]
        least_connected = sorted(least_connected, key=lambda x: x[1])[:10]
        
        # Find orphans (no imports, not imported)
        orphans = [file for file, data in graph.items() 
                  if len(data["imports"]) == 0 and len(data["imported_by"]) == 0]
        
        # Calculate import depth (max chain length)
        def calculate_depth(file, visited=None):
            if visited is None:
                visited = set()
            if file in visited:
                return 0
            visited.add(file)
            
            imports = graph.get(file, {}).get("imports", [])
            if not imports:
                return 0
            return 1 + max((calculate_depth(imp, visited.copy()) for imp in imports), default=0)
        
        depths = [(file, calculate_depth(file)) for file in graph]
        max_depth = max((d for _, d in depths), default=0)
        deepest_files = [f for f, d in depths if d == max_depth]
        
        # Build result
        result = [""]
        result.append("=" * 70)
        result.append("📊 IMPORT DEPENDENCY GRAPH")
        result.append("=" * 70)
        result.append("")
        
        # Overview
        result.append("📈 **OVERVIEW**")
        result.append(f"  Total Modules:    {total_modules}")
        result.append(f"  Total Imports:    {total_imports}")
        result.append(f"  Avg Imports/File: {total_imports/max(1,total_modules):.1f}")
        if include_external:
            result.append(f"  External Libs:    {len(external_imports)}")
        result.append("")
        
        # Circular Dependencies
        result.append("🔄 **CIRCULAR DEPENDENCIES**")
        if circular_deps:
            result.append(f"  Found: {len(circular_deps)} cycles")
            result.append("")
            for i, cycle in enumerate(circular_deps[:5], 1):
                result.append(f"  Cycle {i}:")
                for j, file in enumerate(cycle):
                    if j < len(cycle) - 1:
                        result.append(f"    {file} →")
                    else:
                        result.append(f"    {file}")
            if len(circular_deps) > 5:
                result.append(f"  ... and {len(circular_deps) - 5} more cycles")
            result.append("")
            result.append(f"  ⚠️  Circular dependencies can cause:")
            result.append(f"    • Import errors and crashes")
            result.append(f"    • Difficult refactoring")
            result.append(f"    • Tight coupling")
            result.append(f"  Action: Break cycles by extracting shared code")
        else:
            result.append(f"  ✅ No circular dependencies detected!")
        result.append("")
        
        # Most Imported
        result.append("⭐ **MOST IMPORTED MODULES** (High Coupling)")
        if most_imported:
            for file, count in most_imported[:10]:
                if count > 0:
                    result.append(f"  • {file}: imported by {count} modules")
            result.append("")
            if most_imported[0][1] > 10:
                result.append(f"  ⚠️  High coupling detected")
                result.append(f"    • Changes to these files impact many modules")
                result.append(f"    • Consider breaking into smaller pieces")
        else:
            result.append(f"  No heavily imported modules")
        result.append("")
        
        # Least Connected
        result.append("🔗 **LEAST CONNECTED MODULES**")
        isolated = [f for f, c in least_connected if c == 0]
        if isolated:
            result.append(f"  Orphans ({len(isolated)} files):")
            for file in isolated[:10]:
                result.append(f"  • {file}: No imports, not imported")
            if len(isolated) > 10:
                result.append(f"  ... and {len(isolated) - 10} more")
            result.append("")
            result.append(f"  💡 Consider:")
            result.append(f"    • Are these files still needed?")
            result.append(f"    • Move to archive or delete")
        else:
            result.append(f"  ✅ All modules connected")
        result.append("")
        
        # Import Depth
        result.append("📏 **IMPORT DEPTH** (Dependency Layers)")
        result.append(f"  Maximum Depth: {max_depth}")
        if max_depth > 0:
            result.append(f"  Deepest Files:")
            for file in deepest_files[:5]:
                result.append(f"  • {file} (depth: {max_depth})")
            if len(deepest_files) > 5:
                result.append(f"  ... and {len(deepest_files) - 5} more")
            result.append("")
            if max_depth > 5:
                result.append(f"  ⚠️  Deep dependency chains")
                result.append(f"    • Long chains = fragile architecture")
                result.append(f"    • Consider flattening structure")
        result.append("")
        
        # External Dependencies
        if include_external and external_imports:
            result.append("📦 **EXTERNAL DEPENDENCIES**")
            for lib in sorted(external_imports)[:20]:
                result.append(f"  • {lib}")
            if len(external_imports) > 20:
                result.append(f"  ... and {len(external_imports) - 20} more")
            result.append("")
        
        # Sample Graph Structure
        result.append("🗺️  **SAMPLE GRAPH STRUCTURE** (Top 5 modules)")
        sample_files = sorted(graph.items(), key=lambda x: len(x[1]["imported_by"]), reverse=True)[:5]
        for file, data in sample_files:
            result.append(f"\n  📄 {file}")
            if data["imports"]:
                result.append(f"    Imports: {', '.join(data['imports'][:3])}")
                if len(data["imports"]) > 3:
                    result.append(f"             ... and {len(data['imports']) - 3} more")
            if data["imported_by"]:
                result.append(f"    Imported by: {', '.join(data['imported_by'][:3])}")
                if len(data["imported_by"]) > 3:
                    result.append(f"                 ... and {len(data['imported_by']) - 3} more")
        
        result.append("")
        result.append("=" * 70)
        
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error in get_import_graph: {e}", exc_info=True)
        return f"❌ Error analyzing import graph: {str(e)}"

@mcp.tool()
def find_configuration_inconsistencies(include_examples: bool = True) -> str:
    """
    Compare configuration across different environments and files.
    
    Analyzes configuration files to identify:
    - Missing variables across environments
    - Hardcoded secrets (API_KEY, SECRET, PASSWORD patterns)
    - Security risks (DEBUG=true in production)
    - Inconsistent values between environments
    - Configuration files inventory
    - Environment variable usage in code
    
    Args:
        include_examples: Show example values (default: True, masked for secrets)
    
    Use this for:
    - Deployment safety (prevent missing config crashes)
    - Security audits (find hardcoded secrets)
    - Environment consistency checks
    - "Works in dev, breaks in prod" prevention
    - Configuration documentation
    
    Returns comprehensive configuration analysis with security recommendations.
    Zero LLM calls - pure file parsing and comparison.
    """
    try:
        project_root = Path(CONFIG["project_root"]).resolve()
        
        # Configuration file patterns
        config_patterns = {
            'json': ['*.json', 'config/*.json', '.vscode/*.json'],
            'yaml': ['*.yml', '*.yaml', 'config/*.yml', 'config/*.yaml'],
            'env': ['.env', '.env.*', '*.env'],
            'ini': ['*.ini', '*.cfg', 'setup.cfg'],
            'py': ['config.py', 'settings.py', '**/config.py', '**/settings.py']
        }
        
        # Find all config files
        config_files = {}
        for file_type, patterns in config_patterns.items():
            config_files[file_type] = []
            for pattern in patterns:
                for fp in project_root.glob(pattern):
                    if fp.is_file() and not any(p.startswith('.git') for p in fp.parts):
                        try:
                            config_files[file_type].append(str(fp.relative_to(project_root)))
                        except ValueError:
                            pass
        
        # Parse configuration values
        all_configs = {}  # {filename: {key: value}}
        secret_patterns = re.compile(r'(api[_-]?key|secret|password|token|auth|credential|private[_-]?key)', re.IGNORECASE)
        
        for file_type, files in config_files.items():
            for config_file in files:
                full_path = project_root / config_file
                try:
                    with open(full_path, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    config_data = {}
                    
                    if file_type == 'json':
                        try:
                            data = json.loads(content)
                            if isinstance(data, dict):
                                config_data = {k: str(v) for k, v in data.items() if not isinstance(v, (dict, list))}
                        except json.JSONDecodeError:
                            pass
                    
                    elif file_type in ['yaml', 'yml']:
                        # Simple YAML parsing (key: value)
                        for line in content.split('\n'):
                            match = re.match(r'^\s*([a-zA-Z_][\w_]*)\s*:\s*(.+?)(?:\s*#.*)?$', line)
                            if match:
                                key, value = match.groups()
                                config_data[key.strip()] = value.strip().strip('"\'')
                    
                    elif file_type == 'env':
                        # ENV file parsing (KEY=value)
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)
                                if match:
                                    key, value = match.groups()
                                    config_data[key] = value.strip().strip('"\'')
                    
                    elif file_type == 'ini':
                        # INI file parsing (key = value)
                        current_section = 'default'
                        for line in content.split('\n'):
                            line = line.strip()
                            if line.startswith('[') and line.endswith(']'):
                                current_section = line[1:-1]
                            elif '=' in line and not line.startswith('#'):
                                key, value = line.split('=', 1)
                                full_key = f"{current_section}.{key.strip()}" if current_section != 'default' else key.strip()
                                config_data[full_key] = value.strip().strip('"\'')
                    
                    elif file_type == 'py':
                        # Python config parsing (VARIABLE = value)
                        for line in content.split('\n'):
                            match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)(?:\s*#.*)?$', line)
                            if match:
                                key, value = match.groups()
                                config_data[key] = value.strip().strip('"\'')
                    
                    if config_data:
                        all_configs[config_file] = config_data
                
                except Exception as e:
                    logger.debug(f"Error parsing {config_file}: {e}")
        
        # Detect environment types from filenames
        env_mapping = {}
        for filename in all_configs.keys():
            if 'dev' in filename.lower() or 'local' in filename.lower():
                env_mapping[filename] = 'development'
            elif 'stag' in filename.lower():
                env_mapping[filename] = 'staging'
            elif 'prod' in filename.lower():
                env_mapping[filename] = 'production'
            elif 'test' in filename.lower():
                env_mapping[filename] = 'testing'
            else:
                env_mapping[filename] = 'unknown'
        
        # Collect all unique keys
        all_keys = set()
        for config_data in all_configs.values():
            all_keys.update(config_data.keys())
        
        # Find inconsistencies
        missing_vars = {}  # {env: [keys]}
        hardcoded_secrets = []
        security_risks = []
        variable_comparison = {}  # {key: {file: value}}
        
        for key in all_keys:
            variable_comparison[key] = {}
            for filename, config_data in all_configs.items():
                if key in config_data:
                    value = config_data[key]
                    variable_comparison[key][filename] = value
                    
                    # Check for hardcoded secrets
                    if secret_patterns.search(key) and value and not value.startswith('$') and not value.upper().startswith('ENV:'):
                        if len(value) > 5 and not value.lower() in ['none', 'null', 'false', 'true']:
                            masked_value = value[:3] + '***' if len(value) > 6 else '***'
                            hardcoded_secrets.append({
                                'file': filename,
                                'key': key,
                                'value': masked_value,
                                'risk': 'HIGH' if 'prod' in filename.lower() else 'MEDIUM'
                            })
                    
                    # Check for security risks
                    if key.upper() == 'DEBUG' and value.lower() in ['true', '1', 'yes']:
                        env_type = env_mapping.get(filename, 'unknown')
                        if env_type in ['production', 'staging']:
                            security_risks.append({
                                'file': filename,
                                'issue': f'DEBUG=true in {env_type}',
                                'risk': 'HIGH' if env_type == 'production' else 'MEDIUM',
                                'recommendation': 'Set DEBUG=false in production/staging'
                            })
                else:
                    # Missing variable
                    env_type = env_mapping.get(filename, 'unknown')
                    if env_type not in missing_vars:
                        missing_vars[env_type] = []
                    if key not in missing_vars[env_type]:
                        missing_vars[env_type].append(key)
        
        # Scan code for environment variable usage
        env_var_usage = {}  # {VAR_NAME: [files_using_it]}
        for ext in CONFIG["watched_extensions"]:
            for fp in project_root.rglob(f"*{ext}"):
                if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                    try:
                        if fp.stat().st_size // 1024 > CONFIG["max_file_size_kb"]:
                            continue
                        
                        with open(fp, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Find environment variable access patterns
                        for match in re.finditer(r'(?:os\.environ|process\.env|ENV)\[?["\']([A-Z_][A-Z0-9_]*)["\']?\]?', content):
                            var_name = match.group(1)
                            if var_name not in env_var_usage:
                                env_var_usage[var_name] = []
                            file_rel = str(fp.relative_to(project_root))
                            if file_rel not in env_var_usage[var_name]:
                                env_var_usage[var_name].append(file_rel)
                    
                    except Exception as e:
                        logger.debug(f"Error scanning {fp}: {e}")
        
        # Build result
        result = [""]
        result.append("=" * 70)
        result.append("🔧 CONFIGURATION ANALYSIS")
        result.append("=" * 70)
        result.append("")
        
        # Overview
        result.append("📁 **CONFIGURATION FILES**")
        total_files = sum(len(files) for files in config_files.values())
        result.append(f"  Total Files: {total_files}")
        for file_type, files in config_files.items():
            if files:
                result.append(f"  {file_type.upper()}: {len(files)} files")
                for f in files[:3]:
                    result.append(f"    • {f}")
                if len(files) > 3:
                    result.append(f"    ... and {len(files) - 3} more")
        result.append("")
        
        # Environment mapping
        result.append("🌍 **ENVIRONMENTS DETECTED**")
        env_counts = {}
        for env in env_mapping.values():
            env_counts[env] = env_counts.get(env, 0) + 1
        for env, count in sorted(env_counts.items()):
            result.append(f"  {env.title()}: {count} config files")
        result.append("")
        
        # Security Risks
        result.append("🚨 **SECURITY RISKS**")
        if security_risks:
            result.append(f"  Found: {len(security_risks)} issues")
            result.append("")
            for risk in security_risks:
                result.append(f"  ⚠️  {risk['file']}")
                result.append(f"    Issue: {risk['issue']}")
                result.append(f"    Risk: {risk['risk']}")
                result.append(f"    Action: {risk['recommendation']}")
                result.append("")
        else:
            result.append(f"  ✅ No security risks detected")
        result.append("")
        
        # Hardcoded Secrets
        result.append("🔐 **HARDCODED SECRETS**")
        if hardcoded_secrets:
            result.append(f"  Found: {len(hardcoded_secrets)} potential secrets")
            result.append("")
            for secret in hardcoded_secrets[:10]:
                result.append(f"  {secret['risk']} RISK: {secret['file']}")
                result.append(f"    Key: {secret['key']}")
                if include_examples:
                    result.append(f"    Value: {secret['value']}")
                result.append(f"    Action: Move to environment variable")
                result.append("")
            if len(hardcoded_secrets) > 10:
                result.append(f"  ... and {len(hardcoded_secrets) - 10} more")
            result.append("")
            result.append(f"  💡 Best Practice:")
            result.append(f"    • Store secrets in .env files (not in git)")
            result.append(f"    • Use environment variables")
            result.append(f"    • Add .env to .gitignore")
        else:
            result.append(f"  ✅ No hardcoded secrets detected")
        result.append("")
        
        # Missing Variables
        result.append("❓ **MISSING VARIABLES**")
        if missing_vars:
            for env, keys in sorted(missing_vars.items()):
                if keys:
                    result.append(f"  {env.title()}: {len(keys)} missing")
                    for key in keys[:5]:
                        result.append(f"    • {key}")
                    if len(keys) > 5:
                        result.append(f"    ... and {len(keys) - 5} more")
                    result.append("")
        else:
            result.append(f"  ✅ All variables present in all environments")
        result.append("")
        
        # Variable Comparison
        if include_examples and variable_comparison:
            result.append("📊 **VARIABLE COMPARISON** (Sample)")
            inconsistent = []
            for key, file_values in variable_comparison.items():
                if len(file_values) > 1:
                    values = set(file_values.values())
                    if len(values) > 1:  # Inconsistent values
                        inconsistent.append((key, file_values))
            
            if inconsistent:
                result.append(f"  Inconsistent: {len(inconsistent)} variables")
                result.append("")
                for key, file_values in inconsistent[:5]:
                    result.append(f"  Variable: {key}")
                    for file, value in file_values.items():
                        env = env_mapping.get(file, 'unknown')
                        # Mask secrets
                        if secret_patterns.search(key) and len(value) > 6:
                            value = value[:3] + '***'
                        result.append(f"    {env:12} ({file}): {value}")
                    result.append("")
                if len(inconsistent) > 5:
                    result.append(f"  ... and {len(inconsistent) - 5} more")
            else:
                result.append(f"  ✅ All variables have consistent values")
            result.append("")
        
        # Environment Variable Usage
        result.append("💻 **ENV VAR USAGE IN CODE**")
        if env_var_usage:
            result.append(f"  {len(env_var_usage)} environment variables referenced")
            result.append("")
            for var_name, files in sorted(env_var_usage.items())[:10]:
                result.append(f"  {var_name}")
                result.append(f"    Used in: {', '.join(files[:3])}")
                if len(files) > 3:
                    result.append(f"    ... and {len(files) - 3} more")
                # Check if defined in config
                defined = any(var_name in config_data for config_data in all_configs.values())
                if not defined:
                    result.append(f"    ⚠️  Not found in any config file!")
                result.append("")
            if len(env_var_usage) > 10:
                result.append(f"  ... and {len(env_var_usage) - 10} more")
        else:
            result.append(f"  No environment variable usage detected in code")
        result.append("")
        
        # Recommendations
        result.append("💡 **RECOMMENDATIONS**")
        recommendations = []
        
        if security_risks:
            recommendations.append(f"  • Fix {len(security_risks)} security risks (DEBUG settings)")
        if hardcoded_secrets:
            recommendations.append(f"  • Move {len(hardcoded_secrets)} secrets to environment variables")
        if any(missing_vars.values()):
            total_missing = sum(len(keys) for keys in missing_vars.values())
            recommendations.append(f"  • Define {total_missing} missing variables across environments")
        
        # Check for .env in .gitignore
        gitignore_path = project_root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                gitignore_content = f.read()
            if '.env' not in gitignore_content:
                recommendations.append(f"  • Add .env to .gitignore (prevent secret leaks)")
        else:
            recommendations.append(f"  • Create .gitignore and add .env")
        
        if not recommendations:
            result.append(f"  ✅ Configuration is well-managed!")
        else:
            result.extend(recommendations)
        
        result.append("")
        result.append("=" * 70)
        
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error in find_configuration_inconsistencies: {e}", exc_info=True)
        return f"❌ Error analyzing configuration: {str(e)}"

def init_server():
    """Quick initialization - defer heavy work"""
    global db_conn, embedding_model
    load_config()
    db_conn = init_database()
    if HAS_EMBEDDINGS:
        try:
            # Load model and suppress progress bars for clean MCP output
            embedding_model = SentenceTransformer(CONFIG['embedding_model'])
            # Monkey-patch the encode method to suppress progress bars
            original_encode = embedding_model.encode
            def encode_no_progress(*args, **kwargs):
                kwargs['show_progress_bar'] = False
                return original_encode(*args, **kwargs)
            embedding_model.encode = encode_no_progress
        except Exception as e:
            logger.warning(f"Model load error: {e}")

def lazy_scan():
    """Scan project on first tool call"""
    global db_conn
    cursor = db_conn.execute('SELECT COUNT(*) FROM files')
    if cursor.fetchone()[0] == 0:
        logger.info("🔍 First run - scanning project...")
        scan_project(db_conn)
        logger.info("✅ Scan complete!")

if __name__ == "__main__":
    init_server()
    mcp.run()
