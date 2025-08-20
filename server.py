#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for AI Coding Assistant
A production-ready server that provides tools for AI models to interact with the system.
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

# Third-party imports
try:
    import mcp
    from mcp import ServerSession, StdioServerParameters
    from mcp.server import NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    
    # Import MCP types with fallback for missing ones
    try:
        from mcp.types import (
            CallToolRequest,
            CallToolResult,
            ListToolsRequest,
            ListToolsResult,
            Tool,
            TextContent,
            ImageContent,
            EmbeddedResource,
            LoggingLevel,
            Resource,
            ReadResourceRequest,
            ReadResourceResult,
            ListResourcesRequest,
            ListResourcesResult,
        )
        # Define missing types as aliases or simple classes
        WriteResourceRequest = ReadResourceRequest  # Use as placeholder
        WriteResourceResult = ReadResourceResult    # Use as placeholder
        TextDiff = dict  # Use as placeholder
        TextEdit = dict  # Use as placeholder
        Range = dict     # Use as placeholder
        Position = dict  # Use as placeholder
        ResourceUri = str  # Use as placeholder
        WatchResourcesRequest = dict  # Use as placeholder
        WatchResourcesResult = dict   # Use as placeholder
        ResourceChangeNotification = dict  # Use as placeholder
        ResourceChange = dict  # Use as placeholder
        ResourceChangeKind = str  # Use as placeholder
    except ImportError as type_error:
        print(f"Some MCP types not available: {type_error}")
        # Import what's available
        from mcp.types import *
        
except ImportError:
    print("MCP library not found. Installing...")
    os.system("pip install mcp")
    import mcp
    from mcp import ServerSession, StdioServerParameters
    from mcp.server import NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import *

# Local imports
from tools.file_tools import FileTools
from tools.system_tools import SystemTools
from tools.web_tools import WebTools
from tools.code_tools import CodeTools
from tools.git_tools import GitTools
from tools.database_tools import DatabaseTools
from tools.ai_tools import AITools
from config import Config
from utils.logger import setup_logger
from utils.security import SecurityManager
from utils.metrics import MetricsCollector

# Setup logging
logger = setup_logger(__name__)

@dataclass
class MCPServerState:
    """Server state management."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.now)
    tools_registered: bool = False
    metrics: MetricsCollector = field(default_factory=MetricsCollector)
    security: SecurityManager = field(default_factory=SecurityManager)
    
    # Tool instances
    file_tools: FileTools = None
    system_tools: SystemTools = None
    web_tools: WebTools = None
    code_tools: CodeTools = None
    git_tools: GitTools = None
    database_tools: DatabaseTools = None
    ai_tools: AITools = None

class MCPServer:
    """Main MCP Server implementation."""
    
    def __init__(self, config: Config):
        self.config = config
        self.state = MCPServerState()
        self._initialize_tools()
        
    def _initialize_tools(self):
        """Initialize all tool instances."""
        try:
            self.state.file_tools = FileTools(self.config)
            self.state.system_tools = SystemTools(self.config)
            self.state.web_tools = WebTools(self.config)
            self.state.code_tools = CodeTools(self.config)
            self.state.git_tools = GitTools(self.config)
            self.state.database_tools = DatabaseTools(self.config)
            self.state.ai_tools = AITools(self.config)
            logger.info("All tools initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing tools: {e}")
            raise
    
    def get_tools(self) -> List[Tool]:
        """Get all available tools."""
        tools = []
        
        # File tools
        tools.extend(self.state.file_tools.get_tools())
        
        # System tools
        tools.extend(self.state.system_tools.get_tools())
        
        # Web tools
        tools.extend(self.state.web_tools.get_tools())
        
        # Code tools
        tools.extend(self.state.code_tools.get_tools())
        
        # Git tools
        tools.extend(self.state.git_tools.get_tools())
        
        # Database tools
        tools.extend(self.state.database_tools.get_tools())
        
        # AI tools
        tools.extend(self.state.ai_tools.get_tools())
        
        logger.info(f"Registered {len(tools)} tools")
        return tools
    
    async def handle_list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """Handle list tools request."""
        try:
            self.state.metrics.record_request("list_tools")
            tools = self.get_tools()
            return ListToolsResult(tools=tools)
        except Exception as e:
            logger.error(f"Error in list_tools: {e}")
            self.state.metrics.record_error("list_tools", str(e))
            raise
    
    async def handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool call request."""
        start_time = time.time()
        tool_name = request.name
        arguments = request.arguments
        
        try:
            # Security check
            if not self.state.security.is_tool_allowed(tool_name):
                raise Exception(f"Tool '{tool_name}' is not allowed")
            
            # Rate limiting
            if not self.state.security.check_rate_limit(tool_name):
                raise Exception(f"Rate limit exceeded for tool '{tool_name}'")
            
            # Record metrics
            self.state.metrics.record_request("call_tool", tool_name)
            
            # Route to appropriate tool handler
            result = await self._route_tool_call(tool_name, arguments)
            
            # Record success
            execution_time = time.time() - start_time
            self.state.metrics.record_success("call_tool", tool_name, execution_time)
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        except Exception as e:
            # Record error
            execution_time = time.time() - start_time
            self.state.metrics.record_error("call_tool", tool_name, str(e), execution_time)
            
            logger.error(f"Error in call_tool '{tool_name}': {e}")
            logger.error(traceback.format_exc())
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True
            )
    
    async def _route_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool call to appropriate handler."""
        
        # File tools
        if tool_name.startswith("file_"):
            return await self.state.file_tools.handle_tool_call(tool_name, arguments)
        
        # System tools
        elif tool_name.startswith("system_"):
            return await self.state.system_tools.handle_tool_call(tool_name, arguments)
        
        # Web tools
        elif tool_name.startswith("web_"):
            return await self.state.web_tools.handle_tool_call(tool_name, arguments)
        
        # Code tools
        elif tool_name.startswith("code_"):
            return await self.state.code_tools.handle_tool_call(tool_name, arguments)
        
        # Git tools
        elif tool_name.startswith("git_"):
            return await self.state.git_tools.handle_tool_call(tool_name, arguments)
        
        # Database tools
        elif tool_name.startswith("db_"):
            return await self.state.database_tools.handle_tool_call(tool_name, arguments)
        
        # AI tools
        elif tool_name.startswith("ai_"):
            return await self.state.ai_tools.handle_tool_call(tool_name, arguments)
        
        else:
            raise Exception(f"Unknown tool: {tool_name}")
    
    async def handle_read_resource(self, request: ReadResourceRequest) -> ReadResourceResult:
        """Handle resource read request."""
        try:
            self.state.metrics.record_request("read_resource")
            uri = request.uri
            
            # Route to file tools for file resources
            if uri.startswith("file://"):
                result = await self.state.file_tools.read_resource(uri)
                return ReadResourceResult(
                    contents=[TextContent(type="text", text=result)]
                )
            else:
                raise Exception(f"Unsupported resource URI: {uri}")
                
        except Exception as e:
            logger.error(f"Error in read_resource: {e}")
            self.state.metrics.record_error("read_resource", str(e))
            raise
    
    async def handle_write_resource(self, request: WriteResourceRequest) -> WriteResourceResult:
        """Handle resource write request."""
        try:
            self.state.metrics.record_request("write_resource")
            uri = request.uri
            contents = request.contents
            
            # Route to file tools for file resources
            if uri.startswith("file://"):
                content_text = contents[0].text if contents else ""
                await self.state.file_tools.write_resource(uri, content_text)
                return WriteResourceResult()
            else:
                raise Exception(f"Unsupported resource URI: {uri}")
                
        except Exception as e:
            logger.error(f"Error in write_resource: {e}")
            self.state.metrics.record_error("write_resource", str(e))
            raise
    
    async def handle_list_resources(self, request: ListResourcesRequest) -> ListResourcesResult:
        """Handle resource list request."""
        try:
            self.state.metrics.record_request("list_resources")
            uri = request.uri
            
            # Route to file tools for file resources
            if uri.startswith("file://"):
                resources = await self.state.file_tools.list_resources(uri)
                return ListResourcesResult(resources=resources)
            else:
                raise Exception(f"Unsupported resource URI: {uri}")
                
        except Exception as e:
            logger.error(f"Error in list_resources: {e}")
            self.state.metrics.record_error("list_resources", str(e))
            raise

async def main():
    """Main entry point."""
    try:
        # Load configuration
        config = Config()
        
        # Create server instance
        server = MCPServer(config)
        
        # Server is now using simple stdio communication
        # No need for complex MCP server parameters
        
        logger.info("Starting MCP Server...")
        logger.info(f"Session ID: {server.state.session_id}")
        logger.info(f"Configuration: {config}")
        
        # Start the server using a simpler approach
        logger.info("Starting MCP Server in stdio mode...")
        
        # For now, let's create a simple stdio-based server
        import sys
        import json
        
        # Read from stdin, write to stdout
        while True:
            try:
                line = input()
                if not line:
                    continue
                    
                # Parse the JSON message
                message = json.loads(line)
                method = message.get("method")
                params = message.get("params", {})
                
                # Handle different methods
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {},
                                "resources": {
                                    "read": True,
                                    "write": True,
                                    "list": True
                                }
                            },
                            "serverInfo": {
                                "name": "ai-coding-mcp-server",
                                "version": "1.0.0"
                            }
                        }
                    }
                elif method == "tools/list":
                    tools = server.get_tools()
                    response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "result": {
                            "tools": [{"name": t.name, "description": t.description, "inputSchema": t.inputSchema} for t in tools]
                        }
                    }
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    try:
                        result = await server.handle_call_tool(tool_name, arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "result": {
                                "content": [{"type": "text", "text": str(result)}]
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "error": {
                                "code": -32603,
                                "message": str(e)
                            }
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                # Send response
                print(json.dumps(response))
                sys.stdout.flush()
                
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id") if 'message' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
