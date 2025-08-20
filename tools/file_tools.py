#!/usr/bin/env python3
"""
File tools for MCP Server
Provides file operations like read, write, search, and list.
"""

import os
import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List, Any, Optional
from mcp.types import Tool, Resource

from config import Config

class FileTools:
    """File operation tools for MCP Server."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_path = Path(config.base_path).resolve()
        self.supported_extensions = set(config.security.allowed_file_extensions)
    
    def get_tools(self) -> List[Tool]:
        """Get all file-related tools."""
        return [
            Tool(
                name="file_read",
                description="Read the contents of a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        }
                    },
                    "required": ["path"]
                }
            ),
            Tool(
                name="file_write",
                description="Write content to a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        }
                    },
                    "required": ["path", "content"]
                }
            ),
            Tool(
                name="file_search",
                description="Search for files matching a pattern",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "File pattern to search for (e.g., *.py)"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Search recursively in subdirectories",
                            "default": True
                        },
                        "file_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File extensions to include"
                        }
                    },
                    "required": ["pattern"]
                }
            ),
            Tool(
                name="file_list",
                description="List files and directories in a path",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to list (default: current directory)",
                            "default": "."
                        },
                        "show_hidden": {
                            "type": "boolean",
                            "description": "Show hidden files",
                            "default": False
                        }
                    }
                }
            ),
            Tool(
                name="file_search_content",
                description="Search for content within files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Text to search for"
                        },
                        "file_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File extensions to search in"
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Case sensitive search",
                            "default": False
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Search recursively",
                            "default": True
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="file_info",
                description="Get information about a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file"
                        }
                    },
                    "required": ["path"]
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests."""
        if tool_name == "file_read":
            return await self._read_file(arguments)
        elif tool_name == "file_write":
            return await self._write_file(arguments)
        elif tool_name == "file_search":
            return await self._search_files(arguments)
        elif tool_name == "file_list":
            return await self._list_directory(arguments)
        elif tool_name == "file_search_content":
            return await self._search_content(arguments)
        elif tool_name == "file_info":
            return await self._get_file_info(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents."""
        path = arguments["path"]
        encoding = arguments.get("encoding", "utf-8")
        
        # Validate path
        full_path = self._validate_path(path)
        
        # Check file size
        file_size = full_path.stat().st_size
        if file_size > self.config.tools.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.config.tools.max_file_size})")
        
        # Read file
        try:
            async with aiofiles.open(full_path, 'r', encoding=encoding) as f:
                content = await f.read()
            
            return {
                "success": True,
                "path": str(full_path),
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines()),
                "encoding": encoding
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _write_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file."""
        path = arguments["path"]
        content = arguments["content"]
        encoding = arguments.get("encoding", "utf-8")
        
        # Validate path
        full_path = self._validate_path(path, create_parents=True)
        
        # Check content size
        if len(content) > self.config.tools.max_file_size:
            raise ValueError(f"Content too large: {len(content)} bytes (max: {self.config.tools.max_file_size})")
        
        # Write file
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(full_path, 'w', encoding=encoding) as f:
                await f.write(content)
            
            return {
                "success": True,
                "path": str(full_path),
                "size": len(content),
                "lines": len(content.splitlines()),
                "encoding": encoding
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_files(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files matching pattern."""
        pattern = arguments["pattern"]
        recursive = arguments.get("recursive", True)
        file_types = arguments.get("file_types", list(self.supported_extensions))
        
        try:
            matches = []
            search_path = self.base_path
            
            if recursive:
                search_pattern = search_path / "**" / pattern
            else:
                search_pattern = search_path / pattern
            
            for file_path in search_path.glob(str(search_pattern)):
                if file_path.is_file() and file_path.suffix in file_types:
                    matches.append({
                        "path": str(file_path.relative_to(self.base_path)),
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _list_directory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents."""
        path = arguments.get("path", ".")
        show_hidden = arguments.get("show_hidden", False)
        
        try:
            full_path = self._validate_path(path)
            
            if not full_path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            
            contents = {
                "directories": [],
                "files": []
            }
            
            for item in full_path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    contents["directories"].append({
                        "name": item.name,
                        "path": str(item.relative_to(self.base_path))
                    })
                else:
                    contents["files"].append({
                        "name": item.name,
                        "path": str(item.relative_to(self.base_path)),
                        "size": item.stat().st_size,
                        "extension": item.suffix
                    })
            
            return {
                "success": True,
                "path": str(full_path),
                "contents": contents
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search for content within files."""
        query = arguments["query"]
        file_types = arguments.get("file_types", list(self.supported_extensions))
        case_sensitive = arguments.get("case_sensitive", False)
        recursive = arguments.get("recursive", True)
        
        try:
            matches = []
            search_pattern = "**/*" if recursive else "*"
            
            for file_path in self.base_path.glob(search_pattern):
                if file_path.is_file() and file_path.suffix in file_types:
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            content = await f.read()
                        
                        search_text = content if case_sensitive else content.lower()
                        search_query = query if case_sensitive else query.lower()
                        
                        if search_query in search_text:
                            # Find line numbers
                            lines = content.splitlines()
                            matching_lines = []
                            for i, line in enumerate(lines, 1):
                                line_text = line if case_sensitive else line.lower()
                                if search_query in line_text:
                                    matching_lines.append(i)
                            
                            matches.append({
                                "file": str(file_path.relative_to(self.base_path)),
                                "lines": matching_lines,
                                "count": len(matching_lines)
                            })
                    except Exception:
                        continue
            
            return {
                "success": True,
                "query": query,
                "matches": matches,
                "total_files": len(matches)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_file_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get file information."""
        path = arguments["path"]
        
        try:
            full_path = self._validate_path(path)
            
            stat = full_path.stat()
            
            return {
                "success": True,
                "path": str(full_path),
                "exists": True,
                "is_file": full_path.is_file(),
                "is_dir": full_path.is_dir(),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "permissions": oct(stat.st_mode)[-3:],
                "extension": full_path.suffix if full_path.is_file() else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_path(self, path: str, create_parents: bool = False) -> Path:
        """Validate and resolve file path."""
        full_path = self.base_path / path
        resolved_path = full_path.resolve()
        
        # Security check: ensure path is within base directory
        try:
            resolved_path.relative_to(self.base_path)
        except ValueError:
            raise ValueError(f"Path outside allowed directory: {path}")
        
        return resolved_path
    
    async def read_resource(self, uri: str) -> str:
        """Read resource from URI."""
        if uri.startswith("file://"):
            path = uri[7:]  # Remove "file://" prefix
            result = await self._read_file({"path": path})
            if result["success"]:
                return result["content"]
            else:
                raise Exception(result["error"])
        else:
            raise Exception(f"Unsupported URI scheme: {uri}")
    
    async def write_resource(self, uri: str, content: str):
        """Write resource to URI."""
        if uri.startswith("file://"):
            path = uri[7:]  # Remove "file://" prefix
            result = await self._write_file({"path": path, "content": content})
            if not result["success"]:
                raise Exception(result["error"])
        else:
            raise Exception(f"Unsupported URI scheme: {uri}")
    
    async def list_resources(self, uri: str) -> List[Resource]:
        """List resources in URI."""
        if uri.startswith("file://"):
            path = uri[7:]  # Remove "file://" prefix
            result = await self._list_directory({"path": path})
            if result["success"]:
                resources = []
                for item in result["contents"]["files"]:
                    resources.append(Resource(
                        uri=f"file://{item['path']}",
                        name=item["name"],
                        description=f"File: {item['name']} ({item['size']} bytes)",
                        mimeType=self._get_mime_type(item["extension"])
                    ))
                return resources
            else:
                raise Exception(result["error"])
        else:
            raise Exception(f"Unsupported URI scheme: {uri}")
    
    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type for file extension."""
        mime_types = {
            ".py": "text/x-python",
            ".js": "text/javascript",
            ".ts": "text/typescript",
            ".html": "text/html",
            ".css": "text/css",
            ".json": "application/json",
            ".xml": "application/xml",
            ".yaml": "text/yaml",
            ".yml": "text/yaml",
            ".md": "text/markdown",
            ".txt": "text/plain"
        }
        return mime_types.get(extension, "application/octet-stream")