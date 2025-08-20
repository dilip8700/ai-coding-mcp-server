#!/usr/bin/env python3
"""
Configuration module for MCP Server
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class SecurityConfig:
    """Security configuration."""
    allowed_tools: List[str] = field(default_factory=lambda: [
        "file_read", "file_write", "file_search", "file_list",
        "system_info", "system_command", "system_package",
        "web_scrape", "web_api", "web_download",
        "code_analyze", "code_format", "code_lint",
        "git_status", "git_commit", "git_push", "git_pull",
        "db_query", "db_execute",
        "ai_generate", "ai_analyze", "ai_translate"
    ])
    rate_limit_per_minute: int = 60
    max_file_size_mb: int = 100
    allowed_file_extensions: List[str] = field(default_factory=lambda: [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
        ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg",
        ".txt", ".md", ".java", ".cpp", ".c", ".h", ".hpp", ".cs",
        ".php", ".rb", ".go", ".rs", ".swift", ".kt", ".scala",
        ".sql", ".sh", ".bat", ".ps1"
    ])
    blocked_commands: List[str] = field(default_factory=lambda: [
        "rm -rf /", "format c:", "del /s /q c:\\",
        "sudo", "su", "chmod 777", "chown root"
    ])

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "mcp_server.log"
    max_size_mb: int = 100
    backup_count: int = 5

@dataclass
class MetricsConfig:
    """Metrics configuration."""
    enabled: bool = True
    collect_metrics: bool = True
    metrics_file: str = "metrics.json"
    retention_days: int = 30

@dataclass
class ToolConfig:
    """Tool-specific configuration."""
    # File tools
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    temp_dir: str = "/tmp/mcp_server"
    
    # System tools
    command_timeout: int = 30  # seconds
    max_output_size: int = 1024 * 1024  # 1MB
    
    # Web tools
    request_timeout: int = 10  # seconds
    max_response_size: int = 10 * 1024 * 1024  # 10MB
    user_agent: str = "MCP-Server/1.0"
    
    # Code tools
    max_code_size: int = 1024 * 1024  # 1MB
    supported_languages: List[str] = field(default_factory=lambda: [
        "python", "javascript", "typescript", "java", "cpp", "c",
        "go", "rust", "php", "ruby", "swift", "kotlin", "scala"
    ])
    
    # Git tools
    git_timeout: int = 60  # seconds
    git_max_output: int = 1024 * 1024  # 1MB
    
    # Database tools
    db_timeout: int = 30  # seconds
    max_query_size: int = 1024 * 1024  # 1MB
    
    # AI tools
    ai_timeout: int = 60  # seconds
    max_prompt_size: int = 10000  # characters
    max_response_size: int = 50000  # characters

@dataclass
class Config:
    """Main configuration class."""
    
    # Server settings
    server_name: str = "ai-coding-mcp-server"
    server_version: str = "1.0.0"
    host: str = "localhost"
    port: int = 8000
    
    # Base paths
    base_path: str = field(default_factory=lambda: os.getcwd())
    working_directory: str = field(default_factory=lambda: os.getcwd())
    data_directory: str = field(default_factory=lambda: os.path.join(os.getcwd(), "data"))
    
    # API keys (from environment)
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    github_token: Optional[str] = field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))
    
    # Database settings
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///mcp_server.db"))
    
    # Configuration objects
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Create necessary directories
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(self.tools.temp_dir, exist_ok=True)
        
        # Override with environment variables if present
        self._load_from_env()
        
        # Validate configuration
        self._validate()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Server settings
        if os.getenv("MCP_SERVER_HOST"):
            self.host = os.getenv("MCP_SERVER_HOST")
        if os.getenv("MCP_SERVER_PORT"):
            self.port = int(os.getenv("MCP_SERVER_PORT"))
        
        # Paths
        if os.getenv("MCP_BASE_PATH"):
            self.base_path = os.getenv("MCP_BASE_PATH")
        if os.getenv("MCP_WORKING_DIR"):
            self.working_directory = os.getenv("MCP_WORKING_DIR")
        if os.getenv("MCP_DATA_DIR"):
            self.data_directory = os.getenv("MCP_DATA_DIR")
        
        # Security
        if os.getenv("MCP_RATE_LIMIT"):
            self.security.rate_limit_per_minute = int(os.getenv("MCP_RATE_LIMIT"))
        if os.getenv("MCP_MAX_FILE_SIZE"):
            self.security.max_file_size_mb = int(os.getenv("MCP_MAX_FILE_SIZE"))
        
        # Logging
        if os.getenv("MCP_LOG_LEVEL"):
            self.logging.level = os.getenv("MCP_LOG_LEVEL")
        if os.getenv("MCP_LOG_FILE"):
            self.logging.file = os.getenv("MCP_LOG_FILE")
        
        # Metrics
        if os.getenv("MCP_METRICS_ENABLED"):
            self.metrics.enabled = os.getenv("MCP_METRICS_ENABLED").lower() == "true"
    
    def _validate(self):
        """Validate configuration."""
        # Check required API keys for AI tools
        if not self.openai_api_key and not self.anthropic_api_key:
            print("Warning: No AI API keys found. AI tools will be disabled.")
        
        # Validate paths
        if not os.path.exists(self.base_path):
            raise ValueError(f"Base path does not exist: {self.base_path}")
        if not os.path.exists(self.working_directory):
            raise ValueError(f"Working directory does not exist: {self.working_directory}")
        
        # Validate security settings
        if self.security.rate_limit_per_minute <= 0:
            raise ValueError("Rate limit must be positive")
        if self.security.max_file_size_mb <= 0:
            raise ValueError("Max file size must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "host": self.host,
            "port": self.port,
            "base_path": self.base_path,
            "working_directory": self.working_directory,
            "data_directory": self.data_directory,
            "security": {
                "allowed_tools": self.security.allowed_tools,
                "rate_limit_per_minute": self.security.rate_limit_per_minute,
                "max_file_size_mb": self.security.max_file_size_mb,
                "allowed_file_extensions": self.security.allowed_file_extensions,
                "blocked_commands": self.security.blocked_commands
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
                "max_size_mb": self.logging.max_size_mb,
                "backup_count": self.logging.backup_count
            },
            "metrics": {
                "enabled": self.metrics.enabled,
                "collect_metrics": self.metrics.collect_metrics,
                "metrics_file": self.metrics.metrics_file,
                "retention_days": self.metrics.retention_days
            },
            "tools": {
                "max_file_size": self.tools.max_file_size,
                "temp_dir": self.tools.temp_dir,
                "command_timeout": self.tools.command_timeout,
                "max_output_size": self.tools.max_output_size,
                "request_timeout": self.tools.request_timeout,
                "max_response_size": self.tools.max_response_size,
                "user_agent": self.tools.user_agent,
                "max_code_size": self.tools.max_code_size,
                "supported_languages": self.tools.supported_languages,
                "git_timeout": self.tools.git_timeout,
                "git_max_output": self.tools.git_max_output,
                "db_timeout": self.tools.db_timeout,
                "max_query_size": self.tools.max_query_size,
                "ai_timeout": self.tools.ai_timeout,
                "max_prompt_size": self.tools.max_prompt_size,
                "max_response_size": self.tools.max_response_size
            }
        }
    
    def save_to_file(self, filepath: str):
        """Save configuration to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Config':
        """Load configuration from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        config = cls()
        
        # Update configuration from file
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"Config(server={self.server_name}, version={self.server_version}, base_path={self.base_path})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Config(server_name='{self.server_name}', server_version='{self.server_version}', host='{self.host}', port={self.port})"
