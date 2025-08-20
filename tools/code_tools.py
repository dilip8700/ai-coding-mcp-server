#!/usr/bin/env python3
"""
Code tools for MCP Server
"""

import ast
import re
from typing import Dict, List, Any
from mcp.types import Tool

from config import Config

class CodeTools:
    """Code analysis tools for MCP Server."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_tools(self) -> List[Tool]:
        """Get all code-related tools."""
        return [
            Tool(
                name="code_analyze",
                description="Analyze code for issues and improvements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to analyze"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "default": "python"
                        }
                    },
                    "required": ["code"]
                }
            ),
            Tool(
                name="code_format",
                description="Format code",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to format"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "default": "python"
                        }
                    },
                    "required": ["code"]
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests."""
        if tool_name == "code_analyze":
            return await self._analyze_code(arguments)
        elif tool_name == "code_format":
            return await self._format_code(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _analyze_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for issues."""
        code = arguments["code"]
        language = arguments.get("language", "python")
        
        issues = []
        suggestions = []
        
        if language == "python":
            # Basic Python analysis
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "message": str(e),
                    "line": e.lineno
                })
            
            # Check for common issues
            lines = code.splitlines()
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    suggestions.append({
                        "type": "long_line",
                        "message": f"Line {i} is too long ({len(line)} characters)",
                        "line": i
                    })
                
                if "TODO" in line or "FIXME" in line:
                    issues.append({
                        "type": "todo_comment",
                        "message": f"TODO/FIXME comment on line {i}",
                        "line": i
                    })
        
        return {
            "success": True,
            "language": language,
            "lines": len(code.splitlines()),
            "characters": len(code),
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _format_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Format code."""
        code = arguments["code"]
        language = arguments.get("language", "python")
        
        # Simple formatting for now
        if language == "python":
            # Basic indentation fix
            lines = code.splitlines()
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.endswith(':'):
                    formatted_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith(('return', 'break', 'continue', 'pass')):
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append('    ' * indent_level + stripped)
                else:
                    formatted_lines.append('    ' * indent_level + stripped)
            
            formatted_code = '\n'.join(formatted_lines)
        else:
            formatted_code = code
        
        return {
            "success": True,
            "language": language,
            "formatted_code": formatted_code
        }