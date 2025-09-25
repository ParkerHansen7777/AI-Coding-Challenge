import asyncio
import os
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

server = Server("MCP-Challenge")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="echo",
            description="Echo back the provided text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to echo back"}
                },
                "required": ["text"],
                "additionalProperties": False,
            }
        ),
        Tool(
            name="analyzeFile",
            description="Analyze a file with various options",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Path to the file to analyze"},
                    "options": {"type": "string", "enum": ["lineCount"], "description": "Analysis option"}
                },
                "required": ["file", "options"],
                "additionalProperties": False,
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "echo":
        text = arguments.get("text", "")
        return [TextContent(type="text", text=f"You said: {text}")]
    elif name == "analyzeFile":
        file_path = arguments.get("file", "")
        options = arguments.get("options", "")
        
        if not file_path:
            return [TextContent(type="text", text="Error: No file path provided")]
        
        try:
            # Convert relative path to absolute path based on project root
            if not os.path.isabs(file_path):
                # Get the directory where this script is located (project root)
                project_root = Path(__file__).parent
                file_path = project_root / file_path
            else:
                file_path = Path(file_path)
            
            if options == "lineCount":
                # Count lines in the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f)
                return [TextContent(type="text", text=f"File '{file_path}' has {line_count} lines")]
            else:
                return [TextContent(type="text", text=f"Error: Unknown analysis option '{options}'")]
        except FileNotFoundError:
            return [TextContent(type="text", text=f"Error: File '{file_path}' not found")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {str(e)}")]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        init_opts = server.create_initialization_options()
        await server.run(read, write, initialization_options=init_opts)

if __name__ == "__main__":
    asyncio.run(main())