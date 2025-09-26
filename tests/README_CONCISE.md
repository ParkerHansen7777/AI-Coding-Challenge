# Test Suite

Comprehensive unit tests for MCP tools with 100% coverage.

## Structure

```
tests/
├── test_files/          # Test data organized by tool
│   ├── analyze_file/
│   ├── get_work_log/
│   ├── task_manager/
│   └── work_logging/
└── unit/                # Unit tests organized by tool
    ├── analyze_file/
    ├── get_work_log/
    ├── task_manager/
    └── work_logging/
```

## Running Tests

```bash
# Install dependencies
pip install -r tests/requirements.txt

# Run all tests
py -m pytest tests/ -v

# Run specific tool
py -m pytest tests/unit/analyze_file/ -v

# Run with coverage
py -m pytest tests/ --cov=mcp_server.tools --cov-report=term-missing
```

## Test Results

- **Total Tests**: 101
- **Passed**: 101
- **Coverage**: 100%

## Tools Tested

| Tool | Tests | Coverage |
|------|-------|----------|
| AnalyzeFileTool | 25 | Line count, TODO detection, error handling |
| GetWorkLogTool | 20 | File reading, content parsing, error handling |
| WorkLoggingTool | 24 | Work logging, timestamp handling, error handling |
| TaskManagerTool | 32 | CRUD operations, database handling, error handling |

## Test Categories

Each tool includes tests for:
- **Basic Functionality**: Core tool operations
- **Edge Cases**: Boundary conditions and unusual inputs
- **Error Handling**: File system errors, permission issues, invalid inputs
- **Input Validation**: Missing/empty parameters, invalid options
- **Content Format**: Unicode, special characters, line endings

## Dependencies

- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `unittest.mock` - Mocking support (built-in)
