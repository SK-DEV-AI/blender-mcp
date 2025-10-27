# Import all tool modules to ensure they're registered before starting the server
from . import tools, integrations, prompts
from .connection import mcp

def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()