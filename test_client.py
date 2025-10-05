#!/usr/bin/env python3
"""Test client for CodeMind MCP server"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_codemind():
    """Test CodeMind server with various tool calls"""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="D:/Projects/Python/CodeMind/.venv/Scripts/python.exe",
        args=["D:/Projects/Python/CodeMind/codemind.py"],
        env=None
    )
    
    print("🚀 Starting CodeMind MCP server test...")
    print("=" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("✅ Server initialized successfully!\n")
            
            # List available tools
            tools_response = await session.list_tools()
            print(f"📋 Available tools ({len(tools_response.tools)}):")
            for tool in tools_response.tools:
                print(f"   - {tool.name}: {tool.description}")
            print()
            
            # Test 1: Search for existing code
            print("🔍 Test 1: Searching for existing code...")
            try:
                result = await session.call_tool(
                    "search_existing_code",
                    arguments={"query": "database initialization"}
                )
                print(f"✅ Result: {result.content[0].text[:200]}...")
                print()
            except Exception as e:
                print(f"❌ Error: {e}\n")
            
            # Test 2: Get file context
            print("📄 Test 2: Getting file context...")
            try:
                result = await session.call_tool(
                    "get_file_context",
                    arguments={"file_path": "D:\\Projects\\Python\\CodeMind\\codemind.py"}
                )
                print(f"✅ Result: {result.content[0].text[:300]}...")
                print()
            except Exception as e:
                print(f"❌ Error: {e}\n")
            
            # Test 3: Check functionality exists
            print("🔎 Test 3: Checking if functionality exists...")
            try:
                result = await session.call_tool(
                    "check_functionality_exists",
                    arguments={"feature_description": "semantic search with embeddings"}
                )
                print(f"✅ Result: {result.content[0].text[:300]}...")
                print()
            except Exception as e:
                print(f"❌ Error: {e}\n")
            
            # Test 4: Record a decision
            print("📝 Test 4: Recording a decision...")
            try:
                result = await session.call_tool(
                    "record_decision",
                    arguments={
                        "description": "Test decision: Using FastMCP for simplicity",
                        "reasoning": "FastMCP reduces complexity compared to raw MCP SDK"
                    }
                )
                print(f"✅ Result: {result.content[0].text}")
                print()
            except Exception as e:
                print(f"❌ Error: {e}\n")
            
            # Test 5: Query recent changes
            print("📅 Test 5: Querying recent changes...")
            try:
                result = await session.call_tool(
                    "query_recent_changes",
                    arguments={"hours": 24}
                )
                print(f"✅ Result: {result.content[0].text[:200]}...")
                print()
            except Exception as e:
                print(f"❌ Error: {e}\n")
            
            print("=" * 60)
            print("🎉 All tests completed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_codemind())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
