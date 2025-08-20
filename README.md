# 🤖 MCP Coding Server

A production-ready Model Context Protocol (MCP) server that provides comprehensive tools for AI models to interact with your system.

## 🚀 What is MCP?

MCP (Model Context Protocol) is a standard protocol that allows AI models to call functions on your system. This server provides tools for:

- **File Operations**: Read, write, search files
- **System Commands**: Execute terminal commands safely
- **Web Scraping**: Extract data from websites
- **Code Analysis**: Analyze and format code
- **Git Operations**: Version control commands
- **Database Operations**: SQL queries and commands
- **AI Integration**: Generate and analyze content

## 📋 Features

### 🔧 Core Tools

#### File Operations
- `file_read` - Read file contents
- `file_write` - Write content to files
- `file_search` - Search for files by pattern
- `file_list` - List directory contents
- `file_search_content` - Search text within files
- `file_info` - Get file information

#### System Operations
- `system_info` - Get system information
- `system_command` - Execute terminal commands
- `system_package` - Install Python packages

#### Web Operations
- `web_scrape` - Scrape webpage content
- `web_api` - Make HTTP API calls

#### Code Operations
- `code_analyze` - Analyze code for issues
- `code_format` - Format code

#### Git Operations
- `git_status` - Check git status
- `git_commit` - Commit changes
- `git_push` - Push to remote

#### Database Operations
- `db_query` - Execute SQL queries
- `db_execute` - Execute SQL commands

#### AI Operations
- `ai_generate` - Generate code/text
- `ai_analyze` - Analyze content

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone or download the server files**
   ```bash
   # Make sure you have all the files in your directory
   ls -la
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional)**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export GITHUB_TOKEN="your-github-token"
   ```

4. **Run the server**
   ```bash
   python server.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI tools | None |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI tools | None |
| `GITHUB_TOKEN` | GitHub token for git operations | None |
| `MCP_SERVER_HOST` | Server host | localhost |
| `MCP_SERVER_PORT` | Server port | 8000 |
| `MCP_BASE_PATH` | Base directory for file operations | Current directory |
| `MCP_WORKING_DIR` | Working directory for commands | Current directory |
| `MCP_DATA_DIR` | Data directory | ./data |
| `MCP_RATE_LIMIT` | Rate limit per minute | 60 |
| `MCP_MAX_FILE_SIZE` | Max file size in MB | 100 |
| `MCP_LOG_LEVEL` | Logging level | INFO |
| `MCP_LOG_FILE` | Log file path | mcp_server.log |
| `MCP_METRICS_ENABLED` | Enable metrics collection | true |

### Security Features

- **Rate Limiting**: Prevents abuse with configurable limits
- **Command Validation**: Blocks dangerous system commands
- **Path Validation**: Ensures files are within allowed directories
- **File Size Limits**: Prevents large file operations
- **Extension Filtering**: Only allows safe file types

## 📖 Usage

### Starting the Server

```bash
# Basic start
python server.py

# With custom configuration
MCP_BASE_PATH=/path/to/workspace python server.py

# With logging
MCP_LOG_LEVEL=DEBUG python server.py
```

### Connecting from AI Models

The server communicates via the MCP protocol. AI models can connect and call tools like this:

```python
# Example tool call from AI
{
    "method": "tools/call",
    "params": {
        "name": "file_read",
        "arguments": {
            "path": "main.py"
        }
    }
}
```

### Tool Examples

#### Read a File
```json
{
    "name": "file_read",
    "arguments": {
        "path": "src/main.py",
        "encoding": "utf-8"
    }
}
```

#### Write a File
```json
{
    "name": "file_write",
    "arguments": {
        "path": "new_file.py",
        "content": "print('Hello, World!')"
    }
}
```

#### Execute Command
```json
{
    "name": "system_command",
    "arguments": {
        "command": "ls -la",
        "timeout": 30
    }
}
```

#### Search Files
```json
{
    "name": "file_search",
    "arguments": {
        "pattern": "*.py",
        "recursive": true
    }
}
```

#### Scrape Website
```json
{
    "name": "web_scrape",
    "arguments": {
        "url": "https://example.com"
    }
}
```

## 🏗️ Architecture

### Project Structure
```
mcp_coding_server/
├── server.py              # Main MCP server
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── tools/                # Tool implementations
│   ├── __init__.py
│   ├── file_tools.py     # File operations
│   ├── system_tools.py   # System commands
│   ├── web_tools.py      # Web scraping
│   ├── code_tools.py     # Code analysis
│   ├── git_tools.py      # Git operations
│   ├── database_tools.py # Database operations
│   └── ai_tools.py       # AI integration
└── utils/                # Utilities
    ├── __init__.py
    ├── logger.py         # Logging setup
    ├── security.py       # Security manager
    └── metrics.py        # Metrics collection
```

### Core Components

1. **MCPServer**: Main server class that handles MCP protocol
2. **Tool Classes**: Individual tool implementations
3. **SecurityManager**: Handles security and rate limiting
4. **MetricsCollector**: Collects usage metrics
5. **Config**: Manages configuration and environment variables

## 🔒 Security

### Built-in Protections

- **Command Blocking**: Dangerous commands are automatically blocked
- **Path Validation**: All file operations are restricted to allowed directories
- **Rate Limiting**: Prevents abuse with configurable limits
- **Input Sanitization**: All inputs are sanitized
- **Error Handling**: Comprehensive error handling and logging

### Blocked Commands
- `rm -rf /` - Dangerous file deletion
- `format c:` - Disk formatting
- `sudo` - Privilege escalation
- `chmod 777` - Dangerous permissions
- And many more...

## 📊 Monitoring

### Metrics Collection
The server automatically collects metrics including:
- Request counts
- Response times
- Error rates
- Tool usage statistics

### Logging
Comprehensive logging to both console and file:
- Request/response logging
- Error tracking
- Security events
- Performance metrics

## 🚀 Production Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "server.py"]
```

### Environment Setup
```bash
# Production environment variables
export MCP_LOG_LEVEL=WARNING
export MCP_METRICS_ENABLED=true
export MCP_RATE_LIMIT=30
export MCP_MAX_FILE_SIZE=50
```

## 🔧 Development

### Adding New Tools

1. Create a new tool class in `tools/`
2. Implement the `get_tools()` method
3. Implement the `handle_tool_call()` method
4. Register the tool in `server.py`

### Example Tool
```python
class MyTool:
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="my_tool",
                description="My custom tool",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "param": {"type": "string"}
                    }
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "my_tool":
            return await self._my_tool_function(arguments)
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Errors**: Check file and directory permissions
   ```bash
   chmod +x server.py
   ```

3. **Port Already in Use**: Change the port in configuration
   ```bash
   export MCP_SERVER_PORT=8001
   ```

4. **API Key Issues**: Verify your API keys are set correctly
   ```bash
   echo $OPENAI_API_KEY
   ```

### Debug Mode
```bash
MCP_LOG_LEVEL=DEBUG python server.py
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `mcp_server.log`
3. Enable debug logging
4. Create an issue with detailed information

---

**Happy coding with your AI assistant! 🚀**