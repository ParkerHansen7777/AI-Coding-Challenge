"""
MCP Challenge Server

A modular MCP (Model Context Protocol) server implementation.
This is the main server file that orchestrates all tools and handles MCP communication.
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from .tools.tool_registry import ToolRegistry
from .config.settings import SERVER_NAME


class MCPChallengeServer:
    """Main MCP Challenge Server class"""
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.tool_registry = ToolRegistry()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools():
            """List all available tools"""
            return self.tool_registry.get_tool_definitions()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Call a tool by name with arguments"""
            return await self.tool_registry.execute_tool(name, arguments)
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read, write):
            init_opts = self.server.create_initialization_options()
            await self.server.run(read, write, initialization_options=init_opts)


async def main():
    """Main entry point"""
    server = MCPChallengeServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
