"""
Unit tests for GetWorkLogTool

This module contains comprehensive unit tests for the getWorkLog tool,
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
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcp_server.tools.get_work_log_tool import GetWorkLogTool


class TestGetWorkLogTool:
    """Test class for GetWorkLogTool"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.tool = GetWorkLogTool()
        self.test_log_dir = Path(__file__).parent.parent.parent / "test_files" / "get_work_log"
        self.test_log_dir.mkdir(exist_ok=True)
    
    def test_tool_definition(self):
        """Test that the tool definition is correctly structured"""
        definition = self.tool.tool_definition
        
        assert definition.name == "getWorkLog"
        assert definition.description == "Returns the append-only work log"
        assert definition.inputSchema["type"] == "object"
        assert definition.inputSchema["properties"] == {}
        assert definition.inputSchema["additionalProperties"] == False
    
    @pytest.mark.asyncio
    async def test_get_work_log_with_content(self):
        """Test getting work log with existing content"""
        # Create a temporary work log file with content
        test_log_content = """[2025-09-25 09:51:06] Test work logging functionality
[2025-09-25 09:52:43] I developed the new feature
[2025-09-25 09:53:32] I developed the new feature"""
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "test_work_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(test_log_content)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == test_log_content
    
    @pytest.mark.asyncio
    async def test_get_work_log_empty_file(self):
        """Test getting work log when file exists but is empty"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "empty_work_log.txt"):
            # Create empty file
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("")
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == "Work log is empty."
    
    @pytest.mark.asyncio
    async def test_get_work_log_whitespace_only(self):
        """Test getting work log when file contains only whitespace"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "whitespace_work_log.txt"):
            # Create file with only whitespace
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("   \n\t  \n  ")
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == "Work log is empty."
    
    @pytest.mark.asyncio
    async def test_get_work_log_file_not_exists(self):
        """Test getting work log when file doesn't exist"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "nonexistent_work_log.txt"):
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == "No work log entries found. The work log file does not exist."
    
    @pytest.mark.asyncio
    async def test_get_work_log_single_entry(self):
        """Test getting work log with single entry"""
        single_entry = "[2025-09-25 09:51:06] Single work log entry"
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "single_entry_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(single_entry)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == single_entry
    
    @pytest.mark.asyncio
    async def test_get_work_log_multiple_entries(self):
        """Test getting work log with multiple entries"""
        multiple_entries = """[2025-09-25 09:51:06] First entry
[2025-09-25 09:52:43] Second entry
[2025-09-25 09:53:32] Third entry
[2025-09-25 09:54:15] Fourth entry"""
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "multiple_entries_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(multiple_entries)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == multiple_entries
    
    @pytest.mark.asyncio
    async def test_get_work_log_with_newlines(self):
        """Test getting work log with various newline characters"""
        log_with_newlines = "[2025-09-25 09:51:06] Entry with newlines\n[2025-09-25 09:52:43] Another entry\r\n[2025-09-25 09:53:32] Third entry"
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "newlines_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(log_with_newlines)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            # Normalize line endings for comparison
            expected = log_with_newlines.strip().replace('\r\n', '\n').replace('\r', '\n')
            actual = result[0].text.replace('\r\n', '\n').replace('\r', '\n')
            assert actual == expected
    
    @pytest.mark.asyncio
    async def test_get_work_log_unicode_content(self):
        """Test getting work log with unicode content"""
        unicode_content = """[2025-09-25 09:51:06] Work with émojis 🚀 and unicode
[2025-09-25 09:52:43] 中文测试内容
[2025-09-25 09:53:32] Special chars: àáâãäåæçèéêë"""
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "unicode_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(unicode_content)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == unicode_content
    
    @pytest.mark.asyncio
    async def test_get_work_log_large_content(self):
        """Test getting work log with large content"""
        # Create a large work log with many entries
        large_content = ""
        for i in range(1000):
            large_content += f"[2025-09-25 09:{i//60:02d}:{i%60:02d}] Work log entry number {i}\n"
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "large_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(large_content)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == large_content.strip()
    
    @pytest.mark.asyncio
    async def test_get_work_log_permission_error(self):
        """Test error handling for permission errors"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "permission_log.txt"):
            # Create the file first so it exists, then mock the open to fail
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("test content")
            
            with patch("builtins.open", side_effect=PermissionError("Permission denied")):
                result = await self.tool.execute({})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error reading work log" in result[0].text
                assert "Permission denied" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_work_log_encoding_error(self):
        """Test error handling for encoding errors"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "encoding_log.txt"):
            # Create the file first so it exists, then mock the open to fail
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("test content")
            
            with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")):
                result = await self.tool.execute({})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error reading work log" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_work_log_io_error(self):
        """Test error handling for IO errors"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "io_error_log.txt"):
            # Create the file first so it exists, then mock the open to fail
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("test content")
            
            with patch("builtins.open", side_effect=OSError("Input/output error")):
                result = await self.tool.execute({})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error reading work log" in result[0].text
                assert "Input/output error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_work_log_general_exception(self):
        """Test error handling for general exceptions"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "general_error_log.txt"):
            # Create the file first so it exists, then mock the open to fail
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("test content")
            
            with patch("builtins.open", side_effect=Exception("Unexpected error")):
                result = await self.tool.execute({})
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error reading work log" in result[0].text
                assert "Unexpected error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_work_log_with_arguments(self):
        """Test that the tool ignores any arguments passed"""
        test_log_content = "[2025-09-25 09:51:06] Test entry"
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "args_test_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(test_log_content)
            
            # Pass arguments even though the tool doesn't use them
            result = await self.tool.execute({"some": "argument", "another": "value"})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == test_log_content
    
    @pytest.mark.asyncio
    async def test_get_work_log_file_path_construction(self):
        """Test that the log file path is constructed correctly"""
        # Test that the path points to the project root
        expected_path = Path(__file__).parent.parent.parent.parent / "work_log.txt"
        assert self.tool.log_file_path == expected_path
    
    @pytest.mark.asyncio
    async def test_get_work_log_strips_whitespace(self):
        """Test that the tool strips whitespace from the content"""
        log_with_whitespace = "   \n[2025-09-25 09:51:06] Test entry\n   \n   "
        expected_content = "[2025-09-25 09:51:06] Test entry"
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "whitespace_strip_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(log_with_whitespace)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == expected_content
    
    @pytest.mark.asyncio
    async def test_get_work_log_empty_after_strip(self):
        """Test that file with only whitespace is treated as empty"""
        whitespace_only = "   \n\t  \n  \r\n  "
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "whitespace_only_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(whitespace_only)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == "Work log is empty."
    
    @pytest.mark.asyncio
    async def test_get_work_log_with_timestamps(self):
        """Test work log with various timestamp formats"""
        timestamp_log = """[2025-09-25 09:51:06] Standard timestamp
[2025-09-25 09:52:43.123] Timestamp with milliseconds
[2025-09-25 09:53:32] Another standard timestamp
[2025-09-25 09:54:15.456] Another with milliseconds"""
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "timestamp_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write(timestamp_log)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == timestamp_log
    
    @pytest.mark.asyncio
    async def test_get_work_log_mixed_line_endings(self):
        """Test work log with mixed line endings"""
        mixed_endings = "[2025-09-25 09:51:06] Unix line ending\n[2025-09-25 09:52:43] Windows line ending\r\n[2025-09-25 09:53:32] Mac line ending\r"
        
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "mixed_endings_log.txt"):
            with open(self.tool.log_file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(mixed_endings)
            
            result = await self.tool.execute({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            # Normalize line endings for comparison
            expected = mixed_endings.strip().replace('\r\n', '\n').replace('\r', '\n')
            actual = result[0].text.replace('\r\n', '\n').replace('\r', '\n')
            assert actual == expected


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
