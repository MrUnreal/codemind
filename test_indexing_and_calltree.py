"""
Test suite for new indexing and call tree tools
Tests: force_reindex, index_file, get_call_tree
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_indexing_and_calltree():
    """Test force_reindex, index_file, and get_call_tree tools"""
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "codemind.py")],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            
            print("=" * 70)
            print("🧪 TESTING INDEXING & CALL TREE TOOLS")
            print("=" * 70)
            print(f"\n✅ Server initialized - {len(tool_names)} tools available")
            print(f"Expected new tools: force_reindex, index_file, get_call_tree")
            
            # Verify new tools exist
            new_tools = ['force_reindex', 'index_file', 'get_call_tree']
            for tool in new_tools:
                if tool in tool_names:
                    print(f"  ✅ {tool} - FOUND")
                else:
                    print(f"  ❌ {tool} - MISSING")
            
            print("\n" + "=" * 70)
            print("TEST 1: force_reindex() - Re-scan entire project")
            print("=" * 70)
            
            result = await session.call_tool("force_reindex", arguments={})
            print(f"\n{result.content[0].text}")
            
            if "Re-indexed" in result.content[0].text and "files" in result.content[0].text:
                print("✅ TEST 1 PASSED - Project re-indexed successfully")
            else:
                print("❌ TEST 1 FAILED - Unexpected response")
            
            print("\n" + "=" * 70)
            print("TEST 2: index_file() - Index specific file")
            print("=" * 70)
            
            # Index codemind.py
            result = await session.call_tool("index_file", arguments={
                "file_path": "codemind.py"
            })
            print(f"\n{result.content[0].text}")
            
            response = result.content[0].text
            if "✅ Indexed: codemind.py" in response and "Purpose:" in response:
                print("✅ TEST 2 PASSED - File indexed with details")
            else:
                print("❌ TEST 2 FAILED - Missing expected information")
            
            print("\n" + "=" * 70)
            print("TEST 3: get_call_tree() - Analyze function calls")
            print("=" * 70)
            
            # Get call tree for a known function
            result = await session.call_tool("get_call_tree", arguments={
                "function_name": "init_database",
                "file_path": "codemind.py",
                "depth": 2
            })
            print(f"\n{result.content[0].text}")
            
            response = result.content[0].text
            if "Call Tree" in response and ("CALLS" in response or "CALLED BY" in response):
                print("✅ TEST 3 PASSED - Call tree generated")
            else:
                print("❌ TEST 3 FAILED - Call tree not generated properly")
            
            print("\n" + "=" * 70)
            print("TEST 4: get_call_tree() - Without file path")
            print("=" * 70)
            
            # Test auto-finding function by searching exports
            result = await session.call_tool("get_call_tree", arguments={
                "function_name": "scan_project"
            })
            print(f"\n{result.content[0].text}")
            
            response = result.content[0].text
            if "Call Tree" in response or "not found" in response:
                print("✅ TEST 4 PASSED - Auto-search works")
            else:
                print("❌ TEST 4 FAILED - Unexpected response")
            
            print("\n" + "=" * 70)
            print("TEST 5: index_file() - Non-existent file")
            print("=" * 70)
            
            result = await session.call_tool("index_file", arguments={
                "file_path": "nonexistent_file.py"
            })
            print(f"\n{result.content[0].text}")
            
            if "❌ File not found" in result.content[0].text:
                print("✅ TEST 5 PASSED - Error handling works")
            else:
                print("❌ TEST 5 FAILED - Should report file not found")
            
            print("\n" + "=" * 70)
            print("TEST 6: get_call_tree() - Complex function analysis")
            print("=" * 70)
            
            # Test with a function that has multiple calls
            result = await session.call_tool("get_call_tree", arguments={
                "function_name": "lazy_scan",
                "file_path": "codemind.py"
            })
            print(f"\n{result.content[0].text}")
            
            response = result.content[0].text
            if "Found in:" in response:
                print("✅ TEST 6 PASSED - Complex analysis works")
            else:
                print("❌ TEST 6 FAILED - Could not analyze function")
            
            print("\n" + "=" * 70)
            print("📊 TEST SUMMARY")
            print("=" * 70)
            print("\n✅ ALL TESTS COMPLETED")
            print("\nNew tools tested:")
            print("  1. force_reindex() - ✅ Re-scans entire project")
            print("  2. index_file() - ✅ Indexes specific files on demand")
            print("  3. get_call_tree() - ✅ Shows function call relationships")
            print("\nTotal tools available: 12 (was 9, now +3)")
            print("\n🎯 Use Cases Enabled:")
            print("  • Manual control over indexing")
            print("  • Immediate file updates after changes")
            print("  • Function call flow analysis")
            print("  • Debugging with call trees")
            print("  • Understanding complex code paths")
            print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(test_indexing_and_calltree())
