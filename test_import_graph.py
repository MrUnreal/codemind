"""Test get_import_graph tool"""
import sys
sys.path.insert(0, '.')

# Import and patch for testing
import os
os.environ['__MCP_TEST_MODE__'] = '1'

# Import the module
with open('codemind.py', encoding='utf-8') as f:
    code = f.read()
    # Remove BOM if present
    if code.startswith('\ufeff'):
        code = code[1:]
    exec(code, globals())

# Initialize
init_server()

# Test the tool
print("Testing get_import_graph...")
result = get_import_graph(include_external=False)
print(result)

print("\n" + "="*70)
print("Testing with external imports...")
result2 = get_import_graph(include_external=True)
print(result2)
