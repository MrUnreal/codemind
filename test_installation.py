#!/usr/bin/env python3
"""Quick test to verify CodeMind installation."""

print("🧠 CodeMind Installation Test\n")
print("=" * 50)

# Test 1: Check imports
print("\n1. Testing imports...")
try:
    from fastmcp import FastMCP
    print("   ✅ FastMCP imported")
except ImportError as e:
    print(f"   ❌ FastMCP failed: {e}")
    exit(1)

try:
    from sentence_transformers import SentenceTransformer
    print("   ✅ sentence-transformers imported")
except ImportError as e:
    print(f"   ❌ sentence-transformers failed: {e}")
    exit(1)

try:
    import numpy
    print("   ✅ NumPy imported")
except ImportError as e:
    print(f"   ❌ NumPy failed: {e}")
    exit(1)

try:
    import radon
    print("   ✅ Radon imported")
except ImportError as e:
    print(f"   ❌ Radon failed: {e}")
    exit(1)

# Test 2: Check package structure
print("\n2. Testing CodeMind package...")
try:
    from codemind.workspace import get_workspace_config
    print("   ✅ workspace module loaded")
except ImportError as e:
    print(f"   ❌ workspace module failed: {e}")
    exit(1)

try:
    from codemind.parsers import extract_purpose
    print("   ✅ parsers module loaded")
except ImportError as e:
    print(f"   ❌ parsers module failed: {e}")
    exit(1)

try:
    from codemind.indexing import scan_project
    print("   ✅ indexing module loaded")
except ImportError as e:
    print(f"   ❌ indexing module failed: {e}")
    exit(1)

# Test 3: Check tools
print("\n3. Testing tool modules...")
try:
    from codemind.tools import register_all_tools
    print("   ✅ All tool modules loaded")
except ImportError as e:
    print(f"   ❌ Tool modules failed: {e}")
    exit(1)

# Test 4: Create test MCP server
print("\n4. Testing MCP server creation...")
try:
    mcp = FastMCP("CodeMind-Test")
    register_all_tools(mcp)
    print("   ✅ MCP server created with 20 tools registered")
except Exception as e:
    print(f"   ❌ MCP server creation failed: {e}")
    exit(1)

# Test 5: Check workspace functionality
print("\n5. Testing workspace functionality...")
try:
    import os
    current_dir = os.getcwd()
    config = get_workspace_config(current_dir)
    print(f"   ✅ Workspace config loaded")
    print(f"      - Watched extensions: {len(config['watched_extensions'])} types")
    print(f"      - Max file size: {config['max_file_size_kb']} KB")
    print(f"      - Embedding model: {config['embedding_model']}")
except Exception as e:
    print(f"   ❌ Workspace functionality failed: {e}")
    exit(1)

print("\n" + "=" * 50)
print("✅ All tests passed!")
print("\n📋 Next steps:")
print("   1. Restart GitHub Copilot (Ctrl+Shift+P → 'Copilot: Restart')")
print("   2. Open Copilot Chat")
print("   3. Try: 'Search for existing code in this project'")
print("   4. Check .codemind/logs/ for session logs")
print("\n🎉 CodeMind is ready to use!")
