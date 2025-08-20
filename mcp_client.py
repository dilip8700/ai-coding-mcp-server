#!/usr/bin/env python3
"""
MCP Client for AI Coding Server
A client that can connect to both HTTP and stdio MCP servers.
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# HTTP client imports
try:
    import requests
    from requests.exceptions import RequestException
    HTTP_AVAILABLE = True
except ImportError:
    print("Warning: requests library not available. HTTP client will be disabled.")
    HTTP_AVAILABLE = False

@dataclass
class ToolInfo:
    """Tool information."""
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class ServerInfo:
    """Server information."""
    name: str
    version: str
    tools: List[ToolInfo]
    status: str

class MCPClient:
    """Base MCP client class."""
    
    def __init__(self):
        self.session_id = None
        self.connected = False
    
    async def connect(self):
        """Connect to the server."""
        raise NotImplementedError
    
    async def disconnect(self):
        """Disconnect from the server."""
        raise NotImplementedError
    
    async def list_tools(self) -> List[ToolInfo]:
        """List available tools."""
        raise NotImplementedError
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool."""
        raise NotImplementedError
    
    async def get_server_info(self) -> ServerInfo:
        """Get server information."""
        raise NotImplementedError

class HTTPMCPClient(MCPClient):
    """HTTP-based MCP client."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session() if HTTP_AVAILABLE else None
    
    async def connect(self):
        """Connect to the HTTP server."""
        if not HTTP_AVAILABLE:
            raise RuntimeError("HTTP client not available. Install requests library.")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            self.connected = True
            self.session_id = response.json().get("session_id")
            print(f"✅ Connected to HTTP server at {self.base_url}")
            return True
        except RequestException as e:
            print(f"❌ Failed to connect to HTTP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the HTTP server."""
        if self.session:
            self.session.close()
        self.connected = False
        print("👋 Disconnected from HTTP server")
    
    async def list_tools(self) -> List[ToolInfo]:
        """List available tools."""
        if not self.connected:
            await self.connect()
        
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            tools_data = response.json()
            
            tools = []
            for tool_data in tools_data:
                tools.append(ToolInfo(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    input_schema=tool_data["input_schema"]
                ))
            
            return tools
        except RequestException as e:
            print(f"❌ Failed to list tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool."""
        if not self.connected:
            await self.connect()
        
        try:
            payload = {
                "name": tool_name,
                "arguments": arguments
            }
            
            response = self.session.post(f"{self.base_url}/tools/call", json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("result")
            else:
                raise Exception(result.get("error", "Unknown error"))
                
        except RequestException as e:
            print(f"❌ Failed to call tool {tool_name}: {e}")
            raise
    
    async def get_server_info(self) -> ServerInfo:
        """Get server information."""
        if not self.connected:
            await self.connect()
        
        try:
            response = self.session.get(f"{self.base_url}/info")
            response.raise_for_status()
            info_data = response.json()
            
            tools = []
            for tool_data in info_data.get("tools", []):
                tools.append(ToolInfo(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    input_schema=tool_data["input_schema"]
                ))
            
            return ServerInfo(
                name=info_data.get("name", "Unknown"),
                version=info_data.get("version", "Unknown"),
                tools=tools,
                status=info_data.get("status", "Unknown")
            )
        except RequestException as e:
            print(f"❌ Failed to get server info: {e}")
            return ServerInfo("Unknown", "Unknown", [], "Error")

class StdioMCPClient(MCPClient):
    """Stdio-based MCP client."""
    
    def __init__(self, server_command: List[str] = None):
        super().__init__()
        self.server_command = server_command or ["python", "server.py"]
        self.process = None
        self.request_id = 0
    
    async def connect(self):
        """Connect to the stdio server."""
        try:
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Send initialize message
            init_message = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "initialize",
                "params": {}
            }
            
            response = await self._send_message(init_message)
            if "error" not in response:
                self.connected = True
                print("✅ Connected to stdio server")
                return True
            else:
                print(f"❌ Failed to initialize stdio server: {response.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to connect to stdio server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the stdio server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        self.connected = False
        print("👋 Disconnected from stdio server")
    
    async def list_tools(self) -> List[ToolInfo]:
        """List available tools."""
        if not self.connected:
            await self.connect()
        
        try:
            message = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/list",
                "params": {}
            }
            
            response = await self._send_message(message)
            
            if "error" in response:
                raise Exception(response["error"].get("message", "Unknown error"))
            
            tools_data = response.get("result", {}).get("tools", [])
            tools = []
            
            for tool_data in tools_data:
                tools.append(ToolInfo(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    input_schema=tool_data["inputSchema"]
                ))
            
            return tools
            
        except Exception as e:
            print(f"❌ Failed to list tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool."""
        if not self.connected:
            await self.connect()
        
        try:
            message = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self._send_message(message)
            
            if "error" in response:
                raise Exception(response["error"].get("message", "Unknown error"))
            
            result = response.get("result", {})
            content = result.get("content", [])
            
            # Extract text content
            if content and len(content) > 0:
                return content[0].get("text", "")
            else:
                return result
            
        except Exception as e:
            print(f"❌ Failed to call tool {tool_name}: {e}")
            raise
    
    async def get_server_info(self) -> ServerInfo:
        """Get server information."""
        tools = await self.list_tools()
        return ServerInfo(
            name="AI Coding MCP Server",
            version="1.0.0",
            tools=tools,
            status="connected" if self.connected else "disconnected"
        )
    
    def _get_next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def _send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the server and get response."""
        if not self.process:
            raise RuntimeError("Server process not running")
        
        # Send message
        message_str = json.dumps(message) + "\n"
        self.process.stdin.write(message_str)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")
        
        return json.loads(response_line.strip())

class MCPClientManager:
    """Manager for MCP clients."""
    
    def __init__(self):
        self.http_client = None
        self.stdio_client = None
        self.current_client = None
    
    async def connect_http(self, base_url: str = "http://localhost:8000") -> bool:
        """Connect to HTTP server."""
        self.http_client = HTTPMCPClient(base_url)
        success = await self.http_client.connect()
        if success:
            self.current_client = self.http_client
        return success
    
    async def connect_stdio(self, server_command: List[str] = None) -> bool:
        """Connect to stdio server."""
        self.stdio_client = StdioMCPClient(server_command)
        success = await self.stdio_client.connect()
        if success:
            self.current_client = self.stdio_client
        return success
    
    async def disconnect(self):
        """Disconnect current client."""
        if self.current_client:
            await self.current_client.disconnect()
            self.current_client = None
    
    async def list_tools(self) -> List[ToolInfo]:
        """List available tools."""
        if not self.current_client:
            raise RuntimeError("No client connected")
        return await self.current_client.list_tools()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool."""
        if not self.current_client:
            raise RuntimeError("No client connected")
        return await self.current_client.call_tool(tool_name, arguments)
    
    async def get_server_info(self) -> ServerInfo:
        """Get server information."""
        if not self.current_client:
            raise RuntimeError("No client connected")
        return await self.current_client.get_server_info()

# Interactive CLI
async def interactive_cli():
    """Interactive command-line interface."""
    manager = MCPClientManager()
    
    print("🤖 MCP Client - AI Coding Server")
    print("=" * 40)
    
    # Try to connect to HTTP server first
    print("🔗 Attempting to connect to HTTP server...")
    if await manager.connect_http():
        print("✅ Connected to HTTP server")
    else:
        print("❌ HTTP server not available")
        print("🔗 Attempting to connect to stdio server...")
        if await manager.connect_stdio():
            print("✅ Connected to stdio server")
        else:
            print("❌ No servers available")
            return
    
    print("\n📋 Available commands:")
    print("  list-tools     - List all available tools")
    print("  call <tool>    - Call a specific tool")
    print("  info           - Get server information")
    print("  help           - Show this help")
    print("  quit           - Exit")
    print()
    
    while True:
        try:
            command = input("mcp> ").strip()
            
            if command == "quit" or command == "exit":
                break
            elif command == "help":
                print("📋 Available commands:")
                print("  list-tools     - List all available tools")
                print("  call <tool>    - Call a specific tool")
                print("  info           - Get server information")
                print("  help           - Show this help")
                print("  quit           - Exit")
            elif command == "list-tools":
                tools = await manager.list_tools()
                print(f"\n🔧 Available tools ({len(tools)}):")
                for i, tool in enumerate(tools, 1):
                    print(f"  {i}. {tool.name} - {tool.description}")
                print()
            elif command == "info":
                info = await manager.get_server_info()
                print(f"\n📊 Server Information:")
                print(f"  Name: {info.name}")
                print(f"  Version: {info.version}")
                print(f"  Status: {info.status}")
                print(f"  Tools: {len(info.tools)}")
                print()
            elif command.startswith("call "):
                parts = command.split(" ", 2)
                if len(parts) < 2:
                    print("❌ Usage: call <tool_name> [arguments_json]")
                    continue
                
                tool_name = parts[1]
                arguments = {}
                
                if len(parts) > 2:
                    try:
                        arguments = json.loads(parts[2])
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON arguments")
                        continue
                
                try:
                    result = await manager.call_tool(tool_name, arguments)
                    print(f"\n✅ Result for {tool_name}:")
                    print(json.dumps(result, indent=2))
                    print()
                except Exception as e:
                    print(f"❌ Error calling {tool_name}: {e}")
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await manager.disconnect()

# Example usage functions
async def example_usage():
    """Example usage of the MCP client."""
    manager = MCPClientManager()
    
    # Connect to HTTP server
    if await manager.connect_http():
        print("✅ Connected to HTTP server")
        
        # Get server info
        info = await manager.get_server_info()
        print(f"Server: {info.name} v{info.version}")
        
        # List tools
        tools = await manager.list_tools()
        print(f"Available tools: {len(tools)}")
        for tool in tools[:5]:  # Show first 5 tools
            print(f"  - {tool.name}: {tool.description}")
        
        # Call a simple tool
        try:
            result = await manager.call_tool("echo", {"message": "Hello from MCP client!"})
            print(f"Echo result: {result}")
        except Exception as e:
            print(f"Error calling echo: {e}")
        
        # Call system info
        try:
            result = await manager.call_tool("system_info", {})
            print(f"System info: {result}")
        except Exception as e:
            print(f"Error calling system_info: {e}")
        
        await manager.disconnect()
    else:
        print("❌ Could not connect to HTTP server")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "example":
            asyncio.run(example_usage())
        else:
            print("Usage: python mcp_client.py [example]")
            print("  example  - Run example usage")
            print("  (no args) - Start interactive CLI")
    else:
        asyncio.run(interactive_cli())

if __name__ == "__main__":
    main()