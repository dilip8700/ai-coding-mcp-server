#!/usr/bin/env python3
"""
Security manager for MCP Server
"""

import time
import re
from typing import Dict, List, Set
from collections import defaultdict, deque
from dataclasses import dataclass, field

@dataclass
class SecurityManager:
    """Security manager for MCP Server."""
    
    allowed_tools: Set[str] = field(default_factory=set)
    blocked_commands: Set[str] = field(default_factory=set)
    rate_limits: Dict[str, deque] = field(default_factory=lambda: defaultdict(lambda: deque()))
    max_requests_per_minute: int = 60
    
    def __post_init__(self):
        """Initialize security settings."""
        # Default allowed tools
        if not self.allowed_tools:
            self.allowed_tools = {
                "file_read", "file_write", "file_search", "file_list",
                "system_info", "system_command", "system_package",
                "web_scrape", "web_api", "web_download",
                "code_analyze", "code_format", "code_lint",
                "git_status", "git_commit", "git_push", "git_pull",
                "db_query", "db_execute",
                "ai_generate", "ai_analyze", "ai_translate"
            }
        
        # Default blocked commands
        if not self.blocked_commands:
            self.blocked_commands = {
                "rm -rf /", "format c:", "del /s /q c:\\",
                "sudo", "su", "chmod 777", "chown root",
                "mkfs", "dd if=", "> /dev/", "> /proc/",
                "rm -rf /etc", "rm -rf /var", "rm -rf /usr",
                "del /s /q c:\\windows", "del /s /q c:\\system"
            }
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed."""
        return tool_name in self.allowed_tools
    
    def check_rate_limit(self, tool_name: str) -> bool:
        """Check if rate limit is exceeded for a tool."""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Remove old entries
        while self.rate_limits[tool_name] and self.rate_limits[tool_name][0] < minute_ago:
            self.rate_limits[tool_name].popleft()
        
        # Check if limit exceeded
        if len(self.rate_limits[tool_name]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.rate_limits[tool_name].append(current_time)
        return True
    
    def is_command_safe(self, command: str) -> bool:
        """Check if a command is safe to execute."""
        command_lower = command.lower().strip()
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if blocked.lower() in command_lower:
                return False
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'del\s+/s\s+/q\s+c:\\',
            r'format\s+c:',
            r'sudo\s+',
            r'su\s+',
            r'chmod\s+777',
            r'chown\s+root',
            r'>\s*/dev/',
            r'>\s*/proc/',
            r'mkfs\s+',
            r'dd\s+if=',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                return False
        
        return True
    
    def validate_file_path(self, path: str, base_path: str) -> bool:
        """Validate if a file path is safe."""
        try:
            from pathlib import Path
            full_path = Path(path).resolve()
            base_path_obj = Path(base_path).resolve()
            
            # Check if path is within base directory
            return str(full_path).startswith(str(base_path_obj))
        except Exception:
            return False
    
    def validate_file_extension(self, filename: str, allowed_extensions: Set[str]) -> bool:
        """Validate file extension."""
        from pathlib import Path
        extension = Path(filename).suffix.lower()
        return extension in allowed_extensions
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input."""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters (except newlines and tabs)
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text
    
    def get_security_report(self) -> Dict:
        """Get security report."""
        return {
            "allowed_tools": list(self.allowed_tools),
            "blocked_commands": list(self.blocked_commands),
            "rate_limits": {
                tool: len(requests) for tool, requests in self.rate_limits.items()
            },
            "max_requests_per_minute": self.max_requests_per_minute
        }