# MCP Challenge Server

A modular MCP (Model Context Protocol) server implementation with separated tools and utilities for better maintainability.

## Project Structure

```
AI-Coding-Challenge/
├── mcp_server/                 # Main server package
│   ├── __init__.py
│   ├── server.py              # Main server implementation
│   ├── config/                # Configuration package
│   │   ├── __init__.py
│   │   └── settings.py        # Server configuration and constants
│   ├── tools/                 # Tools package
│   │   ├── __init__.py
│   │   ├── base_tool.py       # Base tool interface
│   │   ├── analyze_file_tool.py # File analysis tool
│   │   ├── get_work_log_tool.py # Work log retrieval tool
│   │   ├── work_logging_tool.py # Work logging tool
│   │   ├── task_manager_tool.py # Task management tool
│   │   └── tool_registry.py   # Tool registration and management
│   └── utils/                 # Utilities package
│       ├── __init__.py
│       └── path_utils.py      # Path utility functions
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── requirements.txt       # Test dependencies
│   ├── README_CONCISE.md     # Test documentation
│   ├── test_files/           # Test data organized by tool
│   │   ├── analyze_file/     # AnalyzeFileTool test files
│   │   ├── get_work_log/     # GetWorkLogTool test files
│   │   ├── task_manager/     # TaskManagerTool test files
│   │   └── work_logging/     # WorkLoggingTool test files
│   └── unit/                 # Unit tests organized by tool
│       ├── analyze_file/     # AnalyzeFileTool tests (25 tests)
│       ├── get_work_log/     # GetWorkLogTool tests (20 tests)
│       ├── task_manager/     # TaskManagerTool tests (33 tests)
│       └── work_logging/     # WorkLoggingTool tests (24 tests)
├── server.py                  # Main entry point
├── requirements.txt           # Python dependencies
├── pytest.ini               # Pytest configuration
├── run_pytest.py            # Pytest runner script
├── PROJECT_PLAN.md          # Project documentation
├── README.md                # This file
├── tasks.db                 # SQLite database for tasks
└── work_log.txt             # Work log file
```

## Available Tools

1. **Analyze File Tool**: Analyzes files with various options (line counting, TODO detection)
2. **Work Logging Tool**: Logs work descriptions with timestamps
3. **Get Work Log Tool**: Retrieves work log entries
4. **Task Manager Tool**: Manages tasks with SQLite database storage

## Test Coverage

- **Total Tests**: 102 unit tests
- **Coverage**: 100% across all tools
- **Tools Tested**: All 4 tools with comprehensive edge cases and error handling

## Setting up MCP Server in Cursor

To use this MCP server with Cursor IDE, follow these steps:

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Cursor MCP Settings

1. Open Cursor IDE
2. Go to Settings (Ctrl/Cmd + ,)
3. Search for "MCP" or navigate to Extensions → MCP
4. Add a new MCP server configuration

### 3. Add Server Configuration

Add the following configuration to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "mcp-challenge": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/your/AI-Coding-Challenge"
    }
  }
}
```

**Note**: Update the `cwd` path to match your actual project directory.

### 4. Alternative Configuration (if using virtual environment)

If you're using a virtual environment:

```json
{
  "mcpServers": {
    "mcp-challenge": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["server.py"],
      "cwd": "/path/to/your/AI-Coding-Challenge"
    }
  }
}
```

### 5. Restart Cursor

After adding the configuration, restart Cursor IDE to load the MCP server.

### 6. Verify Connection

Once Cursor restarts, you should see the MCP server tools available:
- `mcp_MCP-Challenge_analyzeFile` - Analyze files with various options
- `mcp_MCP-Challenge_logWork` - Log work descriptions with timestamps  
- `mcp_MCP-Challenge_getWorkLog` - Retrieve work log entries
- `mcp_MCP-Challenge_taskManager` - Manage tasks with database storage

### Troubleshooting

- **Server not starting**: Check that Python is in your PATH and all dependencies are installed
- **Tools not appearing**: Verify the `cwd` path is correct and the server.py file exists
- **Permission errors**: Ensure Cursor has permission to execute Python scripts in the project directory

## Running Tests
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
py -m pytest tests/ -v

# Run with coverage
py -m pytest tests/ --cov=mcp_server.tools --cov-report=term-missing
```

## Adding New Tools

1. Create a new tool class in `mcp_server/tools/` that inherits from `BaseTool`
2. Implement the `tool_definition` property and `execute` method
3. Register the tool in `tool_registry.py`

## Dependencies

- Python 3.8+
- mcp>=1.0.0
