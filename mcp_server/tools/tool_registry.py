"""
Tool Registry

This module manages the registration and execution of all MCP tools.
"""

from typing import Dict, List, Any
from mcp.types import Tool, TextContent
from .base_tool import BaseTool
from .analyze_file_tool import AnalyzeFileTool
from .work_logging_tool import WorkLoggingTool
from .get_work_log_tool import GetWorkLogTool
from .task_manager_tool import TaskManagerTool


class ToolRegistry:
    """Registry for managing MCP tools"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register the default tools"""
        self.register_tool(AnalyzeFileTool())
        self.register_tool(WorkLoggingTool())
        self.register_tool(GetWorkLogTool())
        self.register_tool(TaskManagerTool())
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool"""
        self._tools[tool.tool_definition.name] = tool
    
    def get_tool_definitions(self) -> List[Tool]:
        """Get all tool definitions for MCP registration"""
        return [tool.tool_definition for tool in self._tools.values()]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a tool by name with the given arguments"""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        
        return await self._tools[name].execute(arguments)
    
    def list_tool_names(self) -> List[str]:
        """Get a list of all registered tool names"""
        return list(self._tools.keys())
