#!/usr/bin/env python3
"""
CodeMind Test Script
Simple test to verify CodeMind is working correctly.
"""

import os
import sys

def test_imports():
    """Test that all required dependencies can be imported."""
    print("🧪 Testing CodeMind...\n")
    print("=" * 50)
    
    # Test required imports
    try:
        from fastmcp import FastMCP
        print("✅ fastmcp imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import fastmcp: {e}")
        print("   Install: pip install fastmcp")
        return False
    
    # Test optional imports
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        print("✅ sentence-transformers and numpy available")
        embeddings_available = True
    except ImportError:
        print("⚠️  sentence-transformers not available (optional)")
        embeddings_available = False
    
    # Test codemind imports
    try:
        import codemind
        print("✅ codemind module loaded")
    except ImportError as e:
        print(f"❌ Failed to import codemind: {e}")
        return False
    
    print("\n" + "=" * 50)
    if embeddings_available:
        print("🎉 All tests passed! Full functionality available.")
    else:
        print("✅ Basic tests passed! (Semantic search disabled without sentence-transformers)")
    
    print("\n📋 Next steps:")
    print("1. Run: python codemind.py")
    print("2. Add to VS Code settings (see below)")
    print("\n💡 VS Code MCP Configuration:")
    print("""
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["path/to/codemind.py"],
      "cwd": "path/to/your/project"
    }
  }
}
    """)
    
    return True

if __name__ == "__main__":
    if not test_imports():
        sys.exit(1)