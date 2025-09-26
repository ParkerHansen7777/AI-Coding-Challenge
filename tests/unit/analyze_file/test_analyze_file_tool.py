"""
Unit tests for AnalyzeFileTool

This module contains comprehensive unit tests for the analyzeFile tool,
including edge cases and error handling scenarios.
"""

import os
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import patch, mock_open
from mcp.types import TextContent

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_server.tools.analyze_file_tool import AnalyzeFileTool


class TestAnalyzeFileTool:
    """Test class for AnalyzeFileTool"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.tool = AnalyzeFileTool()
        self.test_files_dir = Path(__file__).parent.parent.parent / "test_files" / "analyze_file"
    
    def test_tool_definition(self):
        """Test that the tool definition is correctly structured"""
        definition = self.tool.tool_definition
        
        assert definition.name == "analyzeFile"
        assert definition.description == "Analyze a file with various options"
        assert "file" in definition.inputSchema["properties"]
        assert "options" in definition.inputSchema["properties"]
        assert definition.inputSchema["required"] == ["file", "options"]
        assert "lineCount" in definition.inputSchema["properties"]["options"]["enum"]
        assert "hasTodos" in definition.inputSchema["properties"]["options"]["enum"]
    
    @pytest.mark.asyncio
    async def test_line_count_empty_file(self):
        """Test line counting on an empty file"""
        file_path = self.test_files_dir / "empty_file.txt"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has 0 lines" in result[0].text
    
    @pytest.mark.asyncio
    async def test_line_count_single_line(self):
        """Test line counting on a single line file"""
        file_path = self.test_files_dir / "single_line.txt"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has 1 lines" in result[0].text
    
    @pytest.mark.asyncio
    async def test_line_count_multiline_file(self):
        """Test line counting on a multiline file"""
        file_path = self.test_files_dir / "multiline_file.txt"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has 5 lines" in result[0].text
    
    @pytest.mark.asyncio
    async def test_line_count_python_file(self):
        """Test line counting on a Python file"""
        file_path = self.test_files_dir / "sample_code.py"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has" in result[0].text and "lines" in result[0].text
        # The exact line count may vary, but should be > 0
        assert int(result[0].text.split("has ")[1].split(" lines")[0]) > 0
    
    @pytest.mark.asyncio
    async def test_has_todos_with_todos(self):
        """Test TODO detection on a file with TODO comments"""
        file_path = self.test_files_dir / "sample_code.py"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "hasTodos"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has a TODO comment" in result[0].text
    
    @pytest.mark.asyncio
    async def test_has_todos_without_todos(self):
        """Test TODO detection on a file without TODO comments"""
        file_path = self.test_files_dir / "truly_clean.py"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "hasTodos"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "does not have a TODO comment" in result[0].text
    
    @pytest.mark.asyncio
    async def test_has_todos_various_patterns(self):
        """Test TODO detection with various TODO patterns"""
        file_path = self.test_files_dir / "various_todos.py"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "hasTodos"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has a TODO comment" in result[0].text
    
    @pytest.mark.asyncio
    async def test_relative_path_handling(self):
        """Test that relative paths are handled correctly"""
        # Use a relative path from the project root
        relative_path = "tests/test_files/analyze_file/single_line.txt"
        result = await self.tool.execute({
            "file": relative_path,
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has 1 lines" in result[0].text
    
    @pytest.mark.asyncio
    async def test_absolute_path_handling(self):
        """Test that absolute paths are handled correctly"""
        file_path = self.test_files_dir / "single_line.txt"
        result = await self.tool.execute({
            "file": str(file_path.absolute()),
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "has 1 lines" in result[0].text
    
    @pytest.mark.asyncio
    async def test_file_not_found(self):
        """Test error handling for non-existent files"""
        result = await self.tool.execute({
            "file": "nonexistent_file.txt",
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: File" in result[0].text and "not found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_empty_file_path(self):
        """Test error handling for empty file path"""
        result = await self.tool.execute({
            "file": "",
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: No file path provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_missing_file_argument(self):
        """Test error handling for missing file argument"""
        result = await self.tool.execute({
            "options": "lineCount"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: No file path provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_invalid_option(self):
        """Test error handling for invalid analysis option"""
        file_path = self.test_files_dir / "single_line.txt"
        result = await self.tool.execute({
            "file": str(file_path),
            "options": "invalidOption"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: Unknown analysis option" in result[0].text
    
    @pytest.mark.asyncio
    async def test_missing_options_argument(self):
        """Test error handling for missing options argument"""
        file_path = self.test_files_dir / "single_line.txt"
        result = await self.tool.execute({
            "file": str(file_path)
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: Unknown analysis option" in result[0].text
    
    @pytest.mark.asyncio
    async def test_permission_error_handling(self):
        """Test error handling for permission errors"""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = await self.tool.execute({
                "file": "test_file.txt",
                "options": "lineCount"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error reading file" in result[0].text
    
    @pytest.mark.asyncio
    async def test_unicode_encoding_error(self):
        """Test error handling for encoding errors"""
        with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")):
            result = await self.tool.execute({
                "file": "test_file.txt",
                "options": "lineCount"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error reading file" in result[0].text
    
    @pytest.mark.asyncio
    async def test_general_exception_handling(self):
        """Test error handling for general exceptions"""
        with patch("builtins.open", side_effect=Exception("Unexpected error")):
            result = await self.tool.execute({
                "file": "test_file.txt",
                "options": "lineCount"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error reading file" in result[0].text
    
    @pytest.mark.asyncio
    async def test_todo_case_sensitivity(self):
        """Test that TODO detection is case sensitive"""
        # Create a temporary file with lowercase 'todo'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# todo: lowercase todo comment\n")
            temp_file = f.name
        
        try:
            result = await self.tool.execute({
                "file": temp_file,
                "options": "hasTodos"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            # The current implementation only looks for 'TODO', not 'todo'
            assert "does not have a TODO comment" in result[0].text
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_todo_in_string_literal(self):
        """Test that TODO detection works even when TODO is in a string literal"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("TODO: This is a string with TODO")\n')
            temp_file = f.name
        
        try:
            result = await self.tool.execute({
                "file": temp_file,
                "options": "hasTodos"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "has a TODO comment" in result[0].text
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_todo_in_multiline_comment(self):
        """Test TODO detection in multiline comments"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''"""
This is a multiline docstring
TODO: This should be detected
"""
def function():
    pass
''')
            temp_file = f.name
        
        try:
            result = await self.tool.execute({
                "file": temp_file,
                "options": "hasTodos"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "has a TODO comment" in result[0].text
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self):
        """Test handling of large files (simulated)"""
        # Create a temporary file with many lines
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(1000):
                f.write(f"Line {i}\n")
            temp_file = f.name
        
        try:
            result = await self.tool.execute({
                "file": temp_file,
                "options": "lineCount"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "has 1000 lines" in result[0].text
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_file_with_only_newlines(self):
        """Test file containing only newline characters"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('\n\n\n\n')
            temp_file = f.name
        
        try:
            result = await self.tool.execute({
                "file": temp_file,
                "options": "lineCount"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "has 4 lines" in result[0].text
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_file_with_windows_line_endings(self):
        """Test file with Windows line endings (CRLF)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, newline='') as f:
            f.write('Line 1\r\nLine 2\r\nLine 3\r\n')
            temp_file = f.name
        
        try:
            result = await self.tool.execute({
                "file": temp_file,
                "options": "lineCount"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "has 3 lines" in result[0].text
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_file_with_mixed_line_endings(self):
        """Test file with mixed line endings"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, newline='') as f:
            f.write('Line 1\nLine 2\r\nLine 3\n')
            temp_file = f.name
        
        try:
            result = await self.tool.execute({
                "file": temp_file,
                "options": "lineCount"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "has 3 lines" in result[0].text
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
