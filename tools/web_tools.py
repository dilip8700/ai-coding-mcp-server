#!/usr/bin/env python3
"""
Web tools for MCP Server
"""

import aiohttp
import asyncio
from typing import Dict, List, Any
from mcp.types import Tool

from config import Config

class WebTools:
    """Web operation tools for MCP Server."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_tools(self) -> List[Tool]:
        """Get all web-related tools."""
        return [
            Tool(
                name="web_scrape",
                description="Scrape content from a webpage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to scrape"
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="web_api",
                description="Make an API call",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "API URL"
                        },
                        "method": {
                            "type": "string",
                            "description": "HTTP method",
                            "default": "GET"
                        },
                        "data": {
                            "type": "object",
                            "description": "Request data"
                        }
                    },
                    "required": ["url"]
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests."""
        if tool_name == "web_scrape":
            return await self._scrape_webpage(arguments)
        elif tool_name == "web_api":
            return await self._make_api_call(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _scrape_webpage(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape a webpage."""
        url = arguments["url"]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    content = await response.text()
                    
                    return {
                        "success": True,
                        "url": url,
                        "status_code": response.status,
                        "content": content[:1000] + "..." if len(content) > 1000 else content
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _make_api_call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API call."""
        url = arguments["url"]
        method = arguments.get("method", "GET")
        data = arguments.get("data")
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, timeout=10) as response:
                        content = await response.text()
                elif method.upper() == "POST":
                    async with session.post(url, json=data, timeout=10) as response:
                        content = await response.text()
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported method: {method}"
                    }
                
                return {
                    "success": True,
                    "url": url,
                    "method": method,
                    "status_code": response.status,
                    "content": content
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }