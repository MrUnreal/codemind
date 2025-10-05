#!/usr/bin/env python3
"""CodeMind - MCP Memory Server using FastMCP"""
import json, logging, os, sqlite3, hashlib, re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from fastmcp import FastMCP

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    if not results: return f"? '{export_name}' not found in any exports"
    lines = [f"? Found '{export_name}' in {len(results)} file(s):\n"]
    for i, p in enumerate(results[:limit], 1):
        lines.append(f"{i}. {p}\n")
    return "\n".join(lines)

@mcp.tool()
def find_dependencies(file_path: str) -> str:
    """Show what this file imports and what imports this file."""
    lazy_scan()
    if not os.path.exists(file_path):
        return f"? File not found: {file_path}"
    
    # Parse imports from this file
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return f"? Error reading file: {e}"
    
    # Extract imports (simple regex - covers most cases)
    imports = set()
    import_patterns = [
        r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
    ]
    for pattern in import_patterns:
        imports.update(re.findall(pattern, content, re.MULTILINE))
    
    # Find files that import this file
    file_name = os.path.basename(file_path).replace('.py', '')
    importers = []
    for path in db_conn.execute('SELECT path FROM files').fetchall():
        if path[0] == file_path: continue
        try:
            with open(path[0], 'r', encoding='utf-8', errors='ignore') as f:
                other_content = f.read()
                if re.search(rf'\bimport\s+{file_name}\b', other_content) or \
                   re.search(rf'\bfrom\s+.*{file_name}\b', other_content):
                    importers.append(path[0])
        except: pass
    
    lines = [f"?? Dependencies for: {file_path}\n"]
    lines.append(f"\n?? This file imports ({len(imports)}):")
    if imports:
        for imp in sorted(imports)[:20]:
            lines.append(f"  • {imp}")
        if len(imports) > 20:
            lines.append(f"  ... and {len(imports) - 20} more")
    else:
        lines.append("  (none)")
    
    lines.append(f"\n?? Files that import this ({len(importers)}):")
    if importers:
        for imp in importers[:20]:
            lines.append(f"  • {imp}")
        if len(importers) > 20:
            lines.append(f"  ... and {len(importers) - 20} more")
    else:
        lines.append("  (none)")
    
    return "\n".join(lines)

@mcp.tool()
def get_similar_files(file_path: str, limit: int = 5) -> str:
    """Find files similar to the given file (based on purpose/content)."""
    lazy_scan()
    if not HAS_EMBEDDINGS or not embedding_model:
        return "? Similarity search not available (embeddings disabled)"
    
    row = db_conn.execute('SELECT embedding, purpose FROM files WHERE path = ? AND embedding IS NOT NULL', (file_path,)).fetchone()
    if not row:
        return f"? File not found or not indexed: {file_path}"
    
    target_embedding, target_purpose = row
    results = []
    
    for p, pu, e in db_conn.execute('SELECT path, purpose, embedding FROM files WHERE path != ? AND embedding IS NOT NULL', (file_path,)).fetchall():
        if e:
            sim = cosine_similarity(target_embedding, e)
            results.append((p, pu, sim))
    
    results.sort(key=lambda x: x[2], reverse=True)
    
    if not results[:limit]:
        return f"? No similar files found for: {file_path}"
    
    lines = [f"?? Files similar to: {file_path}\n"]
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
        return f"? No decisions found" + (f" matching '{keyword}'" if keyword else "")
    
    lines = [f"?? Architectural Decisions" + (f" (matching '{keyword}')" if keyword else "") + f":\n"]
    for id, desc, reason, ts, files in decisions:
        affected = json.loads(files) if files else []
        lines.append(f"\n#{id} - {desc}")
        lines.append(f"  ?? {ts}")
        lines.append(f"  ?? {reason}")
        if affected:
            lines.append(f"  ?? Affects: {', '.join(affected[:5])}")
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
    
    return f"? Re-indexed {file_count} files in {elapsed:.1f} seconds\n" + \
           f"?? Database refreshed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

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
        return f"? File not found: {file_path}"
    
    if not full_path.is_file():
        return f"? Not a file: {file_path}"
    
    # Check if it's a supported file type
    if full_path.suffix.lower() not in CONFIG['watched_extensions']:
        return f"?? File type {full_path.suffix} not in supported extensions\n" + \
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
            
            return f"? Indexed: {file_path}\n" + \
                   f"?? Purpose: {purpose or 'Not determined'}\n" + \
                   f"?? Exports: {', '.join(exports_list[:5])}\n" + \
                   f"?? Size: {size:.1f} KB\n" + \
                   f"?? Scanned: {scanned}"
        else:
            return f"? File indexed but details not available: {file_path}"
            
    except Exception as e:
        return f"? Error indexing file: {str(e)}"

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
        return f"? Function '{function_name}' not found in any indexed file\n" + \
               f"Try: search_by_export('{function_name}') or index_file() first"
    
    result = [f"?? Call Tree for '{function_name}':\n"]
    
    # For each file that might contain the function
    for fpath in search_files[:3]:  # Limit to first 3 files
        if not fpath.exists():
            continue
            
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            
            # Find function calls within the function
            # Simple regex approach - matches function_name(
            import re
            
            # Find the function definition
            func_pattern = rf'def {re.escape(function_name)}\s*\('
            func_match = re.search(func_pattern, content)
            
            if not func_match:
                continue
            
            result.append(f"\n?? Found in: {fpath.relative_to(CONFIG['project_root'])}")
            
            # Extract function body (simplified - up to next def or end)
            start = func_match.start()
            # Find next function def or end of file
            next_def = re.search(r'\ndef \w+\s*\(', content[start + 1:])
            end = start + next_def.start() if next_def else len(content)
            func_body = content[start:end]
            
            # Find function calls within the body
            # Pattern: word followed by (
            call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            calls = re.findall(call_pattern, func_body)
            
            # Filter out common keywords and the function itself
            keywords = {'if', 'for', 'while', 'return', 'yield', 'def', 'class', 'with', 'try', 'except', 'print'}
            calls = [c for c in calls if c not in keywords and c != function_name]
            unique_calls = sorted(set(calls))[:10]  # Top 10 unique calls
            
            if unique_calls:
                result.append(f"\n  ??  CALLS (what {function_name} calls):")
                for call in unique_calls:
                    result.append(f"    • {call}()")
            
            # Find what calls this function (search all files)
            result.append(f"\n  ??  CALLED BY (what calls {function_name}):")
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
                            callers.append(f"{path} ? {', '.join(caller_funcs[:3])}")
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
            result.append(f"  ?? Error analyzing: {str(e)}")
    
    if len(result) == 1:  # Only header
        return f"? Could not analyze '{function_name}'\n" + \
               f"Make sure the file is indexed and function exists"
    
    result.append(f"\n?? Tip: Use find_dependencies() to see module-level imports")
    
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
def init_server():
    """Quick initialization - defer heavy work"""
    global db_conn, embedding_model
    load_config()
    db_conn = init_database()
    if HAS_EMBEDDINGS:
        try:
            embedding_model = SentenceTransformer(CONFIG['embedding_model'])
        except Exception as e:
            logger.warning(f"Model load error: {e}")

def lazy_scan():
    """Scan project on first tool call"""
    global db_conn
    cursor = db_conn.execute('SELECT COUNT(*) FROM files')
    if cursor.fetchone()[0] == 0:
        logger.info("?? First run - scanning project...")
        scan_project(db_conn)
        logger.info("? Scan complete!")

if __name__ == "__main__":
    init_server()
    mcp.run()
