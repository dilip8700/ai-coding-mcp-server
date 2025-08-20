#!/usr/bin/env python3
"""
Git tools for MCP Server
"""

import asyncio
import subprocess
from typing import Dict, List, Any
from mcp.types import Tool

from config import Config

class GitTools:
    """Git operation tools for MCP Server."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_tools(self) -> List[Tool]:
        """Get all git-related tools."""
        return [
            Tool(
                name="git_status",
                description="Get git status",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="git_commit",
                description="Commit changes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Commit message"
                        }
                    },
                    "required": ["message"]
                }
            ),
            Tool(
                name="git_push",
                description="Push changes",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests."""
        if tool_name == "git_status":
            return await self._git_status()
        elif tool_name == "git_commit":
            return await self._git_commit(arguments)
        elif tool_name == "git_push":
            return await self._git_push()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _git_status(self) -> Dict[str, Any]:
        """Get git status."""
        try:
            process = await asyncio.create_subprocess_shell(
                "git status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": True,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _git_commit(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Commit changes."""
        message = arguments["message"]
        
        try:
            process = await asyncio.create_subprocess_shell(
                f'git commit -m "{message}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": True,
                "message": message,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _git_push(self) -> Dict[str, Any]:
        """Push changes."""
        try:
            process = await asyncio.create_subprocess_shell(
                "git push",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": True,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }