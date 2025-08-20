#!/usr/bin/env python3
"""
Database tools for MCP Server
"""

import sqlite3
from typing import Dict, List, Any
from mcp.types import Tool

from config import Config

class DatabaseTools:
    """Database operation tools for MCP Server."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_tools(self) -> List[Tool]:
        """Get all database-related tools."""
        return [
            Tool(
                name="db_query",
                description="Execute a database query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="db_execute",
                description="Execute a database command",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "SQL command to execute"
                        }
                    },
                    "required": ["command"]
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests."""
        if tool_name == "db_query":
            return await self._execute_query(arguments)
        elif tool_name == "db_execute":
            return await self._execute_command(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _execute_query(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a database query."""
        query = arguments["query"]
        
        try:
            conn = sqlite3.connect("mcp_server.db")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            conn.close()
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "columns": columns,
                "row_count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_command(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a database command."""
        command = arguments["command"]
        
        try:
            conn = sqlite3.connect("mcp_server.db")
            cursor = conn.cursor()
            cursor.execute(command)
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            
            return {
                "success": True,
                "command": command,
                "affected_rows": affected_rows
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }