"""Standalone test for get_import_graph logic"""
import re
import os
from pathlib import Path
from collections import defaultdict

# Configuration
PROJECT_ROOT = Path(".").resolve()
WATCHED_EXTENSIONS = [".py", ".js", ".ts"]
MAX_FILE_SIZE_KB = 500

def get_import_graph_test(include_external=False):
    """Test the import graph logic"""
    try:
        # Build import graph
        graph = {}  # {file: {"imports": [...], "imported_by": [...]}}
        all_files = set()
        external_imports = set()
        
        # Scan all files for imports
        for ext in WATCHED_EXTENSIONS:
            for fp in PROJECT_ROOT.rglob(f"*{ext}"):
                if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                    try:
                        if fp.stat().st_size // 1024 > MAX_FILE_SIZE_KB:
                            continue
                        
                        file_key = str(fp.relative_to(PROJECT_ROOT))
                        all_files.add(file_key)
                        
                        if file_key not in graph:
                            graph[file_key] = {"imports": [], "imported_by": []}
                        
                        with open(fp, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Extract imports based on file type
                        if fp.suffix == '.py':
                            # Python: from X import Y, import X
                            for match in re.finditer(r'(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))', content):
                                module = match.group(1) or match.group(2)
                                if module:
                                    # Check if internal or external
                                    potential_file = module.replace('.', os.sep) + '.py'
                                    is_internal = False
                                    
                                    # Try to find matching internal file
                                    for search_path in [potential_file, module + '.py', module + '/__init__.py']:
                                        full_path = PROJECT_ROOT / search_path
                                        if full_path.exists():
                                            try:
                                                imported_file = str(full_path.relative_to(PROJECT_ROOT))
                                                if imported_file != file_key:  # Don't self-import
                                                    if imported_file not in graph[file_key]["imports"]:
                                                        graph[file_key]["imports"].append(imported_file)
                                                    if imported_file not in graph:
                                                        graph[imported_file] = {"imports": [], "imported_by": []}
                                                    if file_key not in graph[imported_file]["imported_by"]:
                                                        graph[imported_file]["imported_by"].append(file_key)
                                                    is_internal = True
                                                    break
                                            except ValueError:
                                                pass
                                    
                                    if not is_internal and include_external:
                                        external_imports.add(module.split('.')[0])
                        
                    except Exception as e:
                        print(f"Error analyzing {fp}: {e}")
        
        # Calculate metrics
        total_modules = len(graph)
        total_imports = sum(len(data["imports"]) for data in graph.values())
        
        # Find circular dependencies using DFS
        def find_cycles(graph_dict):
            cycles = []
            visited = set()
            rec_stack = []
            
            def dfs(node):
                if node in rec_stack:
                    # Found cycle
                    cycle_start = rec_stack.index(node)
                    cycle = rec_stack[cycle_start:] + [node]
                    # Normalize cycle (start with smallest string)
                    min_idx = cycle.index(min(cycle))
                    normalized = cycle[min_idx:] + cycle[:min_idx]
                    # Check if we've seen this cycle or its reverse
                    if normalized not in cycles and list(reversed(normalized)) not in cycles:
                        cycles.append(normalized)
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.append(node)
                
                for neighbor in graph_dict.get(node, {}).get("imports", []):
                    dfs(neighbor)
                
                rec_stack.pop()
            
            for node in graph_dict:
                if node not in visited:
                    dfs(node)
            
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
            if most_imported[0][1] > 5:
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
        return f"❌ Error: {e}"

if __name__ == "__main__":
    print("Testing get_import_graph (internal only)...")
    print(get_import_graph_test(include_external=False))
    
    print("\n\n" + "="*70)
    print("Testing get_import_graph (with external)...")
    print(get_import_graph_test(include_external=True))
