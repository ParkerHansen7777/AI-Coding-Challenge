"""
Get Work Log Tool Implementation

A tool that returns the append-only work log entries.
"""

from pathlib import Path
from typing import Dict, Any, List
from mcp.types import Tool, TextContent
from .base_tool import BaseTool


class GetWorkLogTool(BaseTool):
    """Tool that returns the work log entries"""
    
    def __init__(self):
        # Set up the work log file path in the project root
        project_root = Path(__file__).parent.parent.parent
        self.log_file_path = project_root / "work_log.txt"
    
    @property
    def tool_definition(self) -> Tool:
        """Return the tool definition for MCP registration"""
        return Tool(
            name="getWorkLog",
            description="Returns the append-only work log",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the get work log tool"""
        try:
            if not self.log_file_path.exists():
                return [TextContent(type="text", text="No work log entries found. The work log file does not exist.")]
            
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read().strip()
            
            if not log_content:
                return [TextContent(type="text", text="Work log is empty.")]
            
            return [TextContent(type="text", text=log_content)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading work log: {str(e)}")]
