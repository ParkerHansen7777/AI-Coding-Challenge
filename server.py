"""
MCP Challenge Server - Main Entry Point

This is the main entry point that imports and runs the modular MCP server.
The actual server implementation is now in the mcp_server package.
"""

import asyncio
from mcp_server.server import main

if __name__ == "__main__":
    asyncio.run(main())