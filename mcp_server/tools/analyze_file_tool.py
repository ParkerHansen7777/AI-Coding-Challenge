"""
Analyze File Tool Implementation

A tool that analyzes files with various options like line counting.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from mcp.types import Tool, TextContent
from .base_tool import BaseTool


class AnalyzeFileTool(BaseTool):
    """Tool that analyzes files with various options"""
    
    @property
    def tool_definition(self) -> Tool:
        """Return the tool definition for MCP registration"""
        return Tool(
            name="analyzeFile",
            description="Analyze a file with various options",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Path to the file to analyze"},
                    "options": {"type": "string", "enum": ["lineCount", "hasTodos"], "description": "Analysis option"}
                },
                "required": ["file", "options"],
                "additionalProperties": False,
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the analyze file tool"""
        file_path = arguments.get("file", "")
        options = arguments.get("options", "")
        
        if not file_path:
            return [TextContent(type="text", text="Error: No file path provided")]
        
        try:
            # Convert relative path to absolute path based on project root
            if not os.path.isabs(file_path):
                # Get the directory where this script is located (project root)
                project_root = Path(__file__).parent.parent.parent
                file_path = project_root / file_path
            else:
                file_path = Path(file_path)
            
            if options == "lineCount":
                # Count lines in the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f)
                return [TextContent(type="text", text=f"File '{file_path}' has {line_count} lines")]
            elif options == "hasTodos":
                # Check if the file has a TODO comment
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'TODO' in line:
                            return [TextContent(type="text", text=f"File '{file_path}' has a TODO comment")]
                return [TextContent(type="text", text=f"File '{file_path}' does not have a TODO comment")]
            else:
                return [TextContent(type="text", text=f"Error: Unknown analysis option '{options}'")]
        except FileNotFoundError:
            return [TextContent(type="text", text=f"Error: File '{file_path}' not found")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {str(e)}")]
