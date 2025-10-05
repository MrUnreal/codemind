"""Quick test for Phase 5 tools"""
import subprocess
import json
import sys
from datetime import datetime

def test_tool(tool_name, params=None):
    """Test a single MCP tool via stdio"""
    print(f"\n{'='*70}")
    print(f"Testing: {tool_name}")
    print(f"{'='*70}")
    start = datetime.now()
    
    # Build MCP request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params or {}
        }
    }
    
    # Start server and send request
    try:
        proc = subprocess.Popen(
            [sys.executable, "codemind.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        
        # Read response (skip initialization messages)
        response = None
        for _ in range(10):  # Try reading up to 10 lines
            line = proc.stdout.readline()
            if not line:
                break
            try:
                data = json.loads(line)
                if data.get("id") == 1:  # Our response
                    response = data
                    break
            except json.JSONDecodeError:
                continue
        
        proc.terminate()
        proc.wait(timeout=2)
        
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        if response and "result" in response:
            content = response["result"][0]["content"][0]["text"]
            print(f"\n{content}")
            print(f"\n✅ Success ({elapsed:.0f}ms)")
            return True
        else:
            print(f"❌ Failed: No valid response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PHASE 5 TOOL TEST")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Test the new tool
    tests = [
        ("get_code_metrics_summary", {}),
        ("get_code_metrics_summary", {"detailed": True}),
    ]
    
    passed = 0
    for tool_name, params in tests:
        if test_tool(tool_name, params):
            passed += 1
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{len(tests)} passed")
    print(f"{'='*70}")
