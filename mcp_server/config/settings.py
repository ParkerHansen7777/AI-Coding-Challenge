"""
Server configuration settings

This module contains all configuration constants and settings
for the MCP Challenge Server.
"""

from pathlib import Path

# Server configuration
SERVER_NAME = "MCP-Challenge"
SERVER_VERSION = "1.0.0"

# Project root directory (parent of mcp_server package)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Tool configuration
SUPPORTED_ANALYSIS_OPTIONS = ["lineCount", "hasTodos"]

# Error messages
ERROR_MESSAGES = {
    "no_file_path": "Error: No file path provided",
    "file_not_found": "Error: File '{}' not found",
    "unknown_analysis_option": "Error: Unknown analysis option '{}'",
    "file_read_error": "Error reading file: {}",
    "unknown_tool": "Unknown tool: {}"
}


class ServerConfig:
    """Server configuration class"""
    
    def __init__(self):
        self.name = SERVER_NAME
        self.version = SERVER_VERSION
        self.project_root = PROJECT_ROOT
        self.supported_analysis_options = SUPPORTED_ANALYSIS_OPTIONS
        self.error_messages = ERROR_MESSAGES
