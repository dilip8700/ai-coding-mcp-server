#!/usr/bin/env python3
"""
Test All MCP Tools
A comprehensive test script for all available tools in the AI Coding MCP Server.
"""

import asyncio
import json
import sys
from mcp_client import MCPClientManager

async def test_all_tools():
    """Test all available tools."""
    manager = MCPClientManager()
    
    print("🚀 STARTING COMPREHENSIVE MCP TOOL TESTS")
    print("="*60)
    
    # Connect to server
    print("🔗 Connecting to MCP server...")
    if await manager.connect_http():
        print("✅ Connected to HTTP server")
    else:
        print("❌ Cannot connect to MCP server")
        return
    
    # Get server info
    try:
        info = await manager.get_server_info()
        print(f"📊 Server: {info.name} v{info.version}")
        print(f"📊 Available tools: {len(info.tools)}")
    except Exception as e:
        print(f"⚠️  Could not get server info: {e}")
    
    # Test results
    passed = 0
    failed = 0
    results = {}
    
    # Test basic tools
    print("\n" + "="*50)
    print("🔧 TESTING BASIC TOOLS")
    print("="*50)
    
    # Echo tool
    try:
        result = await manager.call_tool("echo", {"message": "Hello from MCP test!"})
        print("✅ echo - PASSED")
        results["echo"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ echo - FAILED: {e}")
        results["echo"] = f"FAILED: {e}"
        failed += 1
    
    # System info
    try:
        result = await manager.call_tool("system_info", {})
        print("✅ system_info - PASSED")
        results["system_info"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ system_info - FAILED: {e}")
        results["system_info"] = f"FAILED: {e}"
        failed += 1
    
    # Test file tools
    print("\n" + "="*50)
    print("📁 TESTING FILE TOOLS")
    print("="*50)
    
    # File list
    try:
        result = await manager.call_tool("file_list", {"path": "."})
        print("✅ file_list - PASSED")
        results["file_list"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ file_list - FAILED: {e}")
        results["file_list"] = f"FAILED: {e}"
        failed += 1
    
    # File read
    try:
        result = await manager.call_tool("file_read", {"path": "README.md"})
        print("✅ file_read - PASSED")
        results["file_read"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ file_read - FAILED: {e}")
        results["file_read"] = f"FAILED: {e}"
        failed += 1
    
    # File write
    try:
        test_content = "# Test file created by MCP client\nprint('Hello from test file!')"
        result = await manager.call_tool("file_write", {
            "path": "test_file.py", 
            "content": test_content
        })
        print("✅ file_write - PASSED")
        results["file_write"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ file_write - FAILED: {e}")
        results["file_write"] = f"FAILED: {e}"
        failed += 1
    
    # File search
    try:
        result = await manager.call_tool("file_search", {"pattern": "*.py"})
        print("✅ file_search - PASSED")
        results["file_search"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ file_search - FAILED: {e}")
        results["file_search"] = f"FAILED: {e}"
        failed += 1
    
    # Test system tools
    print("\n" + "="*50)
    print("💻 TESTING SYSTEM TOOLS")
    print("="*50)
    
    # System command
    try:
        result = await manager.call_tool("system_command", {
            "command": "echo 'Hello from system command'",
            "timeout": 10
        })
        print("✅ system_command - PASSED")
        results["system_command"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ system_command - FAILED: {e}")
        results["system_command"] = f"FAILED: {e}"
        failed += 1
    
    # Test web tools
    print("\n" + "="*50)
    print("🌐 TESTING WEB TOOLS")
    print("="*50)
    
    # Web scrape
    try:
        result = await manager.call_tool("web_scrape", {
            "url": "https://httpbin.org/html"
        })
        print("✅ web_scrape - PASSED")
        results["web_scrape"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ web_scrape - FAILED: {e}")
        results["web_scrape"] = f"FAILED: {e}"
        failed += 1
    
    # Web API
    try:
        result = await manager.call_tool("web_api", {
            "url": "https://httpbin.org/json",
            "method": "GET"
        })
        print("✅ web_api - PASSED")
        results["web_api"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ web_api - FAILED: {e}")
        results["web_api"] = f"FAILED: {e}"
        failed += 1
    
    # Test code tools
    print("\n" + "="*50)
    print("📝 TESTING CODE TOOLS")
    print("="*50)
    
    # Code analyze
    try:
        test_code = """
def hello_world():
    print("Hello, World!")
    return "success"

hello_world()
"""
        result = await manager.call_tool("code_analyze", {
            "code": test_code,
            "language": "python"
        })
        print("✅ code_analyze - PASSED")
        results["code_analyze"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ code_analyze - FAILED: {e}")
        results["code_analyze"] = f"FAILED: {e}"
        failed += 1
    
    # Code format
    try:
        unformatted_code = "def test():print('hello');return True"
        result = await manager.call_tool("code_format", {
            "code": unformatted_code,
            "language": "python"
        })
        print("✅ code_format - PASSED")
        results["code_format"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ code_format - FAILED: {e}")
        results["code_format"] = f"FAILED: {e}"
        failed += 1
    
    # Test git tools
    print("\n" + "="*50)
    print("📚 TESTING GIT TOOLS")
    print("="*50)
    
    # Git status
    try:
        result = await manager.call_tool("git_status", {})
        print("✅ git_status - PASSED")
        results["git_status"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ git_status - FAILED: {e}")
        results["git_status"] = f"FAILED: {e}"
        failed += 1
    
    # Test database tools
    print("\n" + "="*50)
    print("🗄️ TESTING DATABASE TOOLS")
    print("="*50)
    
    # Database query
    try:
        result = await manager.call_tool("db_query", {
            "query": "SELECT 1 as test",
            "connection_string": "sqlite:///test.db"
        })
        print("✅ db_query - PASSED")
        results["db_query"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ db_query - FAILED: {e}")
        results["db_query"] = f"FAILED: {e}"
        failed += 1
    
    # Test AI tools
    print("\n" + "="*50)
    print("🤖 TESTING AI TOOLS")
    print("="*50)
    
    # AI generate
    try:
        result = await manager.call_tool("ai_generate", {
            "prompt": "Write a simple Python function to add two numbers",
            "model": "gpt-3.5-turbo"
        })
        print("✅ ai_generate - PASSED")
        results["ai_generate"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ ai_generate - FAILED: {e}")
        results["ai_generate"] = f"FAILED: {e}"
        failed += 1
    
    # AI analyze
    try:
        result = await manager.call_tool("ai_analyze", {
            "content": "def add(a, b): return a + b",
            "analysis_type": "code_review"
        })
        print("✅ ai_analyze - PASSED")
        results["ai_analyze"] = "PASSED"
        passed += 1
    except Exception as e:
        print(f"❌ ai_analyze - FAILED: {e}")
        results["ai_analyze"] = f"FAILED: {e}"
        failed += 1
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    total = passed + failed
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print("\n📋 DETAILED RESULTS:")
    for tool_name, result in results.items():
        if result.startswith("PASSED"):
            print(f"  ✅ {tool_name}")
        else:
            print(f"  ❌ {tool_name}: {result}")
    
    # Clean up test file
    try:
        import os
        if os.path.exists("test_file.py"):
            os.remove("test_file.py")
            print("\n🧹 Cleaned up test file")
    except:
        pass
    
    # Disconnect
    await manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_all_tools())
