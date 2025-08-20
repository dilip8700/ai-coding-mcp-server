#!/usr/bin/env python3
"""
System tools for MCP Server
"""

import asyncio
import subprocess
import sys
import os
import platform
from typing import Dict, List, Any
from mcp.types import Tool

from config import Config

class SystemTools:
    """System operation tools for MCP Server."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_tools(self) -> List[Tool]:
        """Get all system-related tools."""
        return [
            Tool(
                name="system_info",
                description="Get system information",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="system_command",
                description="Execute a system command",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Command timeout in seconds",
                            "default": 30
                        }
                    },
                    "required": ["command"]
                }
            ),
            Tool(
                name="system_package",
                description="Install a Python package",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "Package name to install"
                        }
                    },
                    "required": ["package"]
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests."""
        if tool_name == "system_info":
            return await self._get_system_info()
        elif tool_name == "system_command":
            return await self._execute_command(arguments)
        elif tool_name == "system_package":
            return await self._install_package(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "success": True,
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "current_working_directory": os.getcwd(),
            "environment_variables": dict(os.environ)
        }
    
    async def _execute_command(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a system command."""
        command = arguments["command"]
        timeout = arguments.get("timeout", 30)
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "success": True,
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _install_package(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Install a Python package."""
        package = arguments["package"]
        
        try:
            # Execute pip install
            process = await asyncio.create_subprocess_shell(
                f"pip install {package}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60
            )
            
            return {
                "success": process.returncode == 0,
                "package": package,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }