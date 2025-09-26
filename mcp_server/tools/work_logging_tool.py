"""
Work Logging Tool Implementation

A tool that keeps track of work in an append-only log with description of work and timestamp.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from mcp.types import Tool, TextContent
from .base_tool import BaseTool


class WorkLoggingTool(BaseTool):
    """Tool that logs work descriptions with timestamps"""
    
    def __init__(self):
        # Set up the work log file path in the project root
        project_root = Path(__file__).parent.parent.parent
        self.log_file_path = project_root / "work_log.txt"
    
    @property
    def tool_definition(self) -> Tool:
        """Return the tool definition for MCP registration"""
        return Tool(
            name="logWork",
            description="Log work performed with timestamp",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Description of work performed"}
                },
                "required": ["description"],
                "additionalProperties": False,
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the work logging tool"""
        description = arguments.get("description", "")
        
        if not description:
            return [TextContent(type="text", text="Error: No work description provided")]
        
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create log entry
            log_entry = f"[{timestamp}] {description}\n"
            
            # Append to work log file
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            return [TextContent(type="text", text=f"Work logged successfully: {description} at {timestamp}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error logging work: {str(e)}")]
    
    def get_work_log(self) -> List[str]:
        """Helper method to read all work log entries"""
        try:
            if not self.log_file_path.exists():
                return []
            
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception:
            return []
