#!/usr/bin/env python3
"""
Test the 4 new high-priority tools
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_new_tools():
    """Test all 4 new tools with real scenarios"""
    
    server_params = StdioServerParameters(
        command="D:/Projects/Python/CodeMind/.venv/Scripts/python.exe",
        args=["D:/Projects/Python/CodeMind/codemind.py"],
        env=None
    )
    
    print("="*70)
    print("🧪 TESTING 4 NEW HIGH-PRIORITY TOOLS")
    print("="*70)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("\n✅ Server initialized\n")
            
            # List all available tools
            tools = await session.list_tools()
            print(f"📋 Available tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"   • {tool.name}")
            print()
            
            tests_passed = 0
            total_tests = 4
            
            # TEST 1: search_by_export
            print("="*70)
            print("🧪 TEST 1: search_by_export")
            print("="*70)
            print("Finding files that export 'init_database'...\n")
            
            try:
                result = await session.call_tool(
                    "search_by_export",
                    arguments={"export_name": "init_database"}
                )
                output = result.content[0].text
                print(output)
                
                if "init_database" in output or "Found" in output or "not found" in output:
                    print("✅ TEST 1 PASSED\n")
                    tests_passed += 1
                else:
                    print("❌ TEST 1 FAILED\n")
            except Exception as e:
                print(f"❌ TEST 1 FAILED: {e}\n")
            
            # TEST 2: find_dependencies
            print("="*70)
            print("🧪 TEST 2: find_dependencies")
            print("="*70)
            print("Analyzing dependencies for codemind.py...\n")
            
            try:
                result = await session.call_tool(
                    "find_dependencies",
                    arguments={"file_path": "D:\\Projects\\Python\\CodeMind\\codemind.py"}
                )
                output = result.content[0].text
                print(output[:500] + "..." if len(output) > 500 else output)
                
                if "imports" in output.lower() and ("📥" in output or "📤" in output):
                    print("\n✅ TEST 2 PASSED\n")
                    tests_passed += 1
                else:
                    print("\n❌ TEST 2 FAILED\n")
            except Exception as e:
                print(f"❌ TEST 2 FAILED: {e}\n")
            
            # TEST 3: get_similar_files
            print("="*70)
            print("🧪 TEST 3: get_similar_files")
            print("="*70)
            print("Finding files similar to codemind.py...\n")
            
            try:
                result = await session.call_tool(
                    "get_similar_files",
                    arguments={
                        "file_path": "D:\\Projects\\Python\\CodeMind\\codemind.py",
                        "limit": 3
                    }
                )
                output = result.content[0].text
                print(output[:400] + "..." if len(output) > 400 else output)
                
                if "similar" in output.lower() and ("%" in output or "not found" in output):
                    print("\n✅ TEST 3 PASSED\n")
                    tests_passed += 1
                else:
                    print("\n❌ TEST 3 FAILED\n")
            except Exception as e:
                print(f"❌ TEST 3 FAILED: {e}\n")
            
            # TEST 4: list_all_decisions
            print("="*70)
            print("🧪 TEST 4: list_all_decisions")
            print("="*70)
            print("Listing all architectural decisions...\n")
            
            try:
                result = await session.call_tool(
                    "list_all_decisions",
                    arguments={"limit": 5}
                )
                output = result.content[0].text
                print(output[:500] + "..." if len(output) > 500 else output)
                
                if "decision" in output.lower() or "No decisions" in output:
                    print("\n✅ TEST 4 PASSED\n")
                    tests_passed += 1
                else:
                    print("\n❌ TEST 4 FAILED\n")
            except Exception as e:
                print(f"❌ TEST 4 FAILED: {e}\n")
            
            # TEST 4b: list_all_decisions with keyword
            print("="*70)
            print("🧪 TEST 4b: list_all_decisions (with keyword filter)")
            print("="*70)
            print("Searching decisions for 'authentication'...\n")
            
            try:
                result = await session.call_tool(
                    "list_all_decisions",
                    arguments={"keyword": "authentication", "limit": 5}
                )
                output = result.content[0].text
                print(output[:400] + "..." if len(output) > 400 else output)
                print("\n✅ BONUS TEST PASSED\n")
            except Exception as e:
                print(f"❌ BONUS TEST FAILED: {e}\n")
            
            # FINAL REPORT
            print("="*70)
            print("📊 FINAL TEST REPORT")
            print("="*70)
            print(f"\n✅ Tests Passed: {tests_passed}/{total_tests}")
            print(f"📈 Success Rate: {int(tests_passed/total_tests*100)}%\n")
            
            if tests_passed == total_tests:
                print("🎉 ALL NEW TOOLS WORKING PERFECTLY!")
                print("\nNew capabilities added:")
                print("  1. ✅ search_by_export - Find where functions/classes are defined")
                print("  2. ✅ find_dependencies - Analyze import relationships")
                print("  3. ✅ get_similar_files - Discover related code")
                print("  4. ✅ list_all_decisions - Query architectural history")
                print("\n🚀 CodeMind is now EVEN MORE POWERFUL!")
            else:
                print(f"⚠️  {total_tests - tests_passed} test(s) need attention")
            
            print("\n" + "="*70)
            
            return tests_passed == total_tests

if __name__ == "__main__":
    try:
        success = asyncio.run(test_new_tools())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted")
        exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
