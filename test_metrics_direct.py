"""Direct test of get_code_metrics_summary"""
import sys
sys.path.insert(0, '.')

# Import and patch for testing
import os
os.environ['__MCP_TEST_MODE__'] = '1'

# Import the module to get the function
with open('codemind.py', encoding='utf-8') as f:
    exec(f.read(), globals())

# Initialize
init_server()

# Call the tool directly  (the decorated function is in globals now)
print("Testing get_code_metrics_summary...")
result = get_code_metrics_summary(detailed=False)
print(result)
