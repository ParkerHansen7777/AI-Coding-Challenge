"""
Unit tests for WorkLoggingTool

This module contains comprehensive unit tests for the workLogging tool,
including edge cases and error handling scenarios.
"""

import os
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from mcp.types import TextContent

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcp_server.tools.work_logging_tool import WorkLoggingTool


class TestWorkLoggingTool:
    """Test class for WorkLoggingTool"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.tool = WorkLoggingTool()
        self.test_log_dir = Path(__file__).parent.parent.parent / "test_files" / "work_logging"
        self.test_log_dir.mkdir(exist_ok=True)
    
    def test_tool_definition(self):
        """Test that the tool definition is correctly structured"""
        definition = self.tool.tool_definition
        
        assert definition.name == "logWork"
        assert definition.description == "Log work performed with timestamp"
        assert definition.inputSchema["type"] == "object"
        assert "description" in definition.inputSchema["properties"]
        assert definition.inputSchema["required"] == ["description"]
        assert definition.inputSchema["additionalProperties"] == False
    
    @pytest.mark.asyncio
    async def test_log_work_success(self):
        """Test successful work logging"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "test_work_log.txt"):
            # Ensure the file doesn't exist initially
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            result = await self.tool.execute({
                "description": "Implemented new feature"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            assert "Implemented new feature" in result[0].text
            
            # Verify the file was created and contains the log entry
            assert self.tool.log_file_path.exists()
            with open(self.tool.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Implemented new feature" in content
                assert "[" in content and "]" in content  # Timestamp format
    
    @pytest.mark.asyncio
    async def test_log_work_empty_description(self):
        """Test work logging with empty description"""
        result = await self.tool.execute({
            "description": ""
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: No work description provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_missing_description(self):
        """Test work logging with missing description"""
        result = await self.tool.execute({})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: No work description provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_whitespace_description(self):
        """Test work logging with whitespace-only description"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "whitespace_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            result = await self.tool.execute({
                "description": "   \n\t  "
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            # The current implementation allows whitespace-only descriptions
            assert "Work logged successfully" in result[0].text
            assert "   \n\t  " in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_multiple_entries(self):
        """Test logging multiple work entries"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "multiple_entries_log.txt"):
            # Ensure the file doesn't exist initially
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            # Log multiple entries
            entries = [
                "First work item",
                "Second work item",
                "Third work item"
            ]
            
            for entry in entries:
                result = await self.tool.execute({"description": entry})
                assert "Work logged successfully" in result[0].text
            
            # Verify all entries are in the file
            with open(self.tool.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for entry in entries:
                    assert entry in content
    
    @pytest.mark.asyncio
    async def test_log_work_unicode_content(self):
        """Test logging work with unicode content"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "unicode_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            unicode_description = "Work with émojis 🚀 and unicode: 中文测试"
            result = await self.tool.execute({
                "description": unicode_description
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            assert unicode_description in result[0].text
            
            # Verify unicode content is properly written to file
            with open(self.tool.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert unicode_description in content
    
    @pytest.mark.asyncio
    async def test_log_work_special_characters(self):
        """Test logging work with special characters"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "special_chars_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            special_description = "Work with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
            result = await self.tool.execute({
                "description": special_description
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            assert special_description in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_long_description(self):
        """Test logging work with very long description"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "long_description_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            long_description = "A" * 1000  # 1000 character description
            result = await self.tool.execute({
                "description": long_description
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            assert long_description in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_newlines_in_description(self):
        """Test logging work with newlines in description"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "newlines_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            multiline_description = "First line\nSecond line\nThird line"
            result = await self.tool.execute({
                "description": multiline_description
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            assert multiline_description in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_timestamp_format(self):
        """Test that timestamps are in the correct format"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "timestamp_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            result = await self.tool.execute({
                "description": "Test timestamp format"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            
            # Verify timestamp format in the file
            with open(self.tool.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Should contain timestamp in format [YYYY-MM-DD HH:MM:SS]
                import re
                timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
                assert re.search(timestamp_pattern, content)
    
    @pytest.mark.asyncio
    async def test_log_work_permission_error(self):
        """Test error handling for permission errors"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "permission_log.txt"):
            with patch("builtins.open", side_effect=PermissionError("Permission denied")):
                result = await self.tool.execute({
                    "description": "Test permission error"
                })
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error logging work" in result[0].text
                assert "Permission denied" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_io_error(self):
        """Test error handling for IO errors"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "io_error_log.txt"):
            with patch("builtins.open", side_effect=OSError("Input/output error")):
                result = await self.tool.execute({
                    "description": "Test IO error"
                })
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error logging work" in result[0].text
                assert "Input/output error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_encoding_error(self):
        """Test error handling for encoding errors"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "encoding_error_log.txt"):
            with patch("builtins.open", side_effect=UnicodeEncodeError("utf-8", "test", 0, 1, "invalid")):
                result = await self.tool.execute({
                    "description": "Test encoding error"
                })
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error logging work" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_general_exception(self):
        """Test error handling for general exceptions"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "general_error_log.txt"):
            with patch("builtins.open", side_effect=Exception("Unexpected error")):
                result = await self.tool.execute({
                    "description": "Test general error"
                })
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Error logging work" in result[0].text
                assert "Unexpected error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_file_path_construction(self):
        """Test that the log file path is constructed correctly"""
        # Test that the path points to the project root
        expected_path = Path(__file__).parent.parent.parent.parent / "work_log.txt"
        assert self.tool.log_file_path == expected_path
    
    @pytest.mark.asyncio
    async def test_log_work_append_mode(self):
        """Test that work is appended to existing log file"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "append_test_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            # Log first entry
            result1 = await self.tool.execute({
                "description": "First entry"
            })
            assert "Work logged successfully" in result1[0].text
            
            # Log second entry
            result2 = await self.tool.execute({
                "description": "Second entry"
            })
            assert "Work logged successfully" in result2[0].text
            
            # Verify both entries are in the file
            with open(self.tool.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "First entry" in content
                assert "Second entry" in content
                # Should have exactly 2 lines
                assert content.count('\n') == 2
    
    @pytest.mark.asyncio
    async def test_log_work_with_extra_arguments(self):
        """Test that extra arguments are ignored"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "extra_args_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            result = await self.tool.execute({
                "description": "Test with extra args",
                "extra_param": "should be ignored",
                "another_param": 123
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            assert "Test with extra args" in result[0].text
    
    def test_get_work_log_helper_method(self):
        """Test the get_work_log helper method"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "helper_test_log.txt"):
            # Test with non-existent file
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            entries = self.tool.get_work_log()
            assert entries == []
            
            # Test with existing file
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("[2025-09-25 09:51:06] First entry\n")
                f.write("[2025-09-25 09:52:43] Second entry\n")
            
            entries = self.tool.get_work_log()
            assert len(entries) == 2
            assert "First entry" in entries[0]
            assert "Second entry" in entries[1]
    
    def test_get_work_log_helper_method_error(self):
        """Test the get_work_log helper method with error"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "helper_error_log.txt"):
            # Create the file first so it exists
            with open(self.tool.log_file_path, 'w', encoding='utf-8') as f:
                f.write("test content\n")
            
            with patch("builtins.open", side_effect=Exception("Read error")):
                entries = self.tool.get_work_log()
                assert entries == []
    
    @pytest.mark.asyncio
    async def test_log_work_timestamp_consistency(self):
        """Test that timestamps are consistent within the same execution"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "timestamp_consistency_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            # Mock datetime to return a fixed timestamp
            fixed_time = datetime(2025, 9, 25, 10, 30, 45)
            with patch('mcp_server.tools.work_logging_tool.datetime') as mock_datetime:
                mock_datetime.now.return_value = fixed_time
                mock_datetime.strftime = fixed_time.strftime
                
                result = await self.tool.execute({
                    "description": "Test timestamp consistency"
                })
                
                assert len(result) == 1
                assert isinstance(result[0], TextContent)
                assert "Work logged successfully" in result[0].text
                assert "2025-09-25 10:30:45" in result[0].text
                
                # Verify timestamp in file
                with open(self.tool.log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert "[2025-09-25 10:30:45]" in content
    
    @pytest.mark.asyncio
    async def test_log_work_empty_string_description(self):
        """Test work logging with empty string description"""
        result = await self.tool.execute({
            "description": ""
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: No work description provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_none_description(self):
        """Test work logging with None description"""
        result = await self.tool.execute({
            "description": None
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: No work description provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_log_work_very_short_description(self):
        """Test work logging with very short description"""
        with patch.object(self.tool, 'log_file_path', self.test_log_dir / "short_description_log.txt"):
            if self.tool.log_file_path.exists():
                self.tool.log_file_path.unlink()
            
            result = await self.tool.execute({
                "description": "A"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Work logged successfully" in result[0].text
            assert "A" in result[0].text


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
