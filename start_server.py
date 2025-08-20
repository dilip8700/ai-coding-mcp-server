#!/usr/bin/env python3
"""
Startup script for MCP Server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'mcp', 'fastapi', 'uvicorn', 'pydantic', 'python-dotenv',
        'requests', 'beautifulsoup4', 'aiofiles', 'aiohttp'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing dependencies:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstalling missing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print("   pip install -r requirements.txt")
            return False
    
    return True

def setup_environment():
    """Setup environment variables."""
    print("🔧 Setting up environment...")
    
    # Create necessary directories
    directories = ['data', 'logs', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Set default environment variables if not already set
    env_vars = {
        'MCP_LOG_LEVEL': 'INFO',
        'MCP_METRICS_ENABLED': 'true',
        'MCP_RATE_LIMIT': '60',
        'MCP_MAX_FILE_SIZE': '100'
    }
    
    for var, value in env_vars.items():
        if not os.getenv(var):
            os.environ[var] = value
            print(f"   Set {var}={value}")

def main():
    """Main startup function."""
    print("🚀 Starting MCP Coding Server...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    print("\n✅ Environment ready!")
    print("\n📋 Server Information:")
    print(f"   - Python: {sys.version}")
    print(f"   - Working Directory: {os.getcwd()}")
    print(f"   - Log Level: {os.getenv('MCP_LOG_LEVEL', 'INFO')}")
    print(f"   - Rate Limit: {os.getenv('MCP_RATE_LIMIT', '60')} requests/minute")
    print(f"   - Max File Size: {os.getenv('MCP_MAX_FILE_SIZE', '100')} MB")
    
    # Check for API keys
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("\n⚠️  Warning: No AI API keys found.")
        print("   AI tools will be limited. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for full functionality.")
    
    print("\n🎯 Starting server...")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Import and run the server
        from server import main as server_main
        import asyncio
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()