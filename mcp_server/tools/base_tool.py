"""
Base tool interface for MCP tools

This module provides the base class that all MCP tools should inherit from
to ensure consistent behavior and interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from mcp.types import Tool, TextContent


class BaseTool(ABC):
    """Base class for all MCP tools"""
    
    @property
    @abstractmethod
    def tool_definition(self) -> Tool:
        """Return the tool definition for MCP registration"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the tool with the given arguments"""
        pass
