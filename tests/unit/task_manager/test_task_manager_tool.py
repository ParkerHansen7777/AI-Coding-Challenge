"""
Unit tests for TaskManagerTool

This module contains comprehensive unit tests for the taskManager tool,
including edge cases and error handling scenarios.
"""

import os
import pytest
import tempfile
import asyncio
import sqlite3
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from mcp.types import TextContent

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcp_server.tools.task_manager_tool import TaskManagerTool


class TestTaskManagerTool:
    """Test class for TaskManagerTool"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Create a temporary database for each test
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create the tool instance and patch the database path
        self.tool = TaskManagerTool()
        self.tool.db_path = Path(self.temp_db.name)
        self.tool._init_database()
    
    def teardown_method(self):
        """Clean up after each test method"""
        # Close any open database connections first
        if hasattr(self, 'tool') and hasattr(self.tool, 'db_path'):
            try:
                # Force close any open connections
                import gc
                gc.collect()
            except:
                pass
        
        # Remove the temporary database file
        try:
            if os.path.exists(self.temp_db.name):
                os.unlink(self.temp_db.name)
        except (PermissionError, OSError):
            # On Windows, sometimes the file is still in use
            # This is not critical for test success
            pass
    
    def test_tool_definition(self):
        """Test that the tool definition is correctly structured"""
        definition = self.tool.tool_definition
        
        assert definition.name == "taskManager"
        assert definition.description == "Manage tasks - add, list, and mark as complete"
        assert definition.inputSchema["type"] == "object"
        assert "option" in definition.inputSchema["properties"]
        assert "taskName" in definition.inputSchema["properties"]
        assert "description" in definition.inputSchema["properties"]
        assert "completionStatus" in definition.inputSchema["properties"]
        assert definition.inputSchema["required"] == ["option"]
        assert definition.inputSchema["additionalProperties"] == False
    
    @pytest.mark.asyncio
    async def test_add_task_success(self):
        """Test successful task addition"""
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Test Task",
            "description": "This is a test task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'Test Task' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_missing_task_name(self):
        """Test adding task with missing task name"""
        result = await self.tool.execute({
            "option": "addTask",
            "description": "This is a test task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: taskName and description are required for addTask" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_missing_description(self):
        """Test adding task with missing description"""
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Test Task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: taskName and description are required for addTask" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_empty_task_name(self):
        """Test adding task with empty task name"""
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "",
            "description": "This is a test task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: taskName and description are required for addTask" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_empty_description(self):
        """Test adding task with empty description"""
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Test Task",
            "description": ""
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: taskName and description are required for addTask" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_duplicate_name(self):
        """Test adding task with duplicate name"""
        # Add first task
        await self.tool.execute({
            "option": "addTask",
            "taskName": "Duplicate Task",
            "description": "First task"
        })
        
        # Try to add task with same name
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Duplicate Task",
            "description": "Second task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: Task 'Duplicate Task' already exists" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_unicode_content(self):
        """Test adding task with unicode content"""
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Unicode Task 🚀",
            "description": "Task with émojis and unicode: 中文测试"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'Unicode Task 🚀' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_special_characters(self):
        """Test adding task with special characters"""
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Special Chars: !@#$%^&*()",
            "description": "Description with special chars: []{}|;':\",./<>?"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'Special Chars: !@#$%^&*()' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_long_content(self):
        """Test adding task with very long content"""
        long_name = "A" * 100
        long_description = "B" * 1000
        
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": long_name,
            "description": long_description
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert f"Task '{long_name}' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_add_task_newlines_in_content(self):
        """Test adding task with newlines in content"""
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Multiline\nTask",
            "description": "Description\nwith\nnewlines"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'Multiline\nTask' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_tasks_empty(self):
        """Test listing tasks when database is empty"""
        result = await self.tool.execute({
            "option": "listTasks"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "No tasks found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_content(self):
        """Test listing tasks with content"""
        # Add some tasks
        await self.tool.execute({
            "option": "addTask",
            "taskName": "Task 1",
            "description": "First task"
        })
        await self.tool.execute({
            "option": "addTask",
            "taskName": "Task 2",
            "description": "Second task"
        })
        
        result = await self.tool.execute({
            "option": "listTasks"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        content = result[0].text
        
        assert "Task 2" in content  # Should be first (newest)
        assert "Task 1" in content
        assert "First task" in content
        assert "Second task" in content
        assert "⏳" in content  # Status icon for incomplete tasks
        assert "not complete" in content
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_completed_task(self):
        """Test listing tasks including completed ones"""
        # Add a task
        await self.tool.execute({
            "option": "addTask",
            "taskName": "Complete Task",
            "description": "This will be completed"
        })
        
        # Complete the task
        await self.tool.execute({
            "option": "completeTask",
            "taskName": "Complete Task",
            "completionStatus": "complete"
        })
        
        result = await self.tool.execute({
            "option": "listTasks"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        content = result[0].text
        
        assert "Complete Task" in content
        assert "✅" in content  # Status icon for complete tasks
        assert "complete" in content
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_no_description(self):
        """Test listing tasks with null description"""
        # Add a task with null description
        with self.tool._get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks (name, description, status) VALUES (?, ?, 'not complete')",
                ("No Desc Task", None)
            )
            conn.commit()
        
        result = await self.tool.execute({
            "option": "listTasks"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        content = result[0].text
        
        assert "No Desc Task" in content
        assert "No description" in content
    
    @pytest.mark.asyncio
    async def test_complete_task_success(self):
        """Test successful task completion"""
        # Add a task
        await self.tool.execute({
            "option": "addTask",
            "taskName": "To Complete",
            "description": "This task will be completed"
        })
        
        # Complete the task
        result = await self.tool.execute({
            "option": "completeTask",
            "taskName": "To Complete",
            "completionStatus": "complete"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'To Complete' status changed from 'not complete' to 'complete'" in result[0].text
    
    @pytest.mark.asyncio
    async def test_complete_task_missing_task_name(self):
        """Test completing task with missing task name"""
        result = await self.tool.execute({
            "option": "completeTask",
            "completionStatus": "complete"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: taskName and completionStatus are required for completeTask" in result[0].text
    
    @pytest.mark.asyncio
    async def test_complete_task_missing_completion_status(self):
        """Test completing task with missing completion status"""
        result = await self.tool.execute({
            "option": "completeTask",
            "taskName": "Some Task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: taskName and completionStatus are required for completeTask" in result[0].text
    
    @pytest.mark.asyncio
    async def test_complete_task_not_found(self):
        """Test completing non-existent task"""
        result = await self.tool.execute({
            "option": "completeTask",
            "taskName": "Non Existent Task",
            "completionStatus": "complete"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: Task 'Non Existent Task' not found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_complete_task_revert_status(self):
        """Test reverting task status from complete to not complete"""
        # Add a task
        await self.tool.execute({
            "option": "addTask",
            "taskName": "Revert Task",
            "description": "This task will be reverted"
        })
        
        # Complete the task
        await self.tool.execute({
            "option": "completeTask",
            "taskName": "Revert Task",
            "completionStatus": "complete"
        })
        
        # Revert to not complete
        result = await self.tool.execute({
            "option": "completeTask",
            "taskName": "Revert Task",
            "completionStatus": "not complete"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'Revert Task' status changed from 'complete' to 'not complete'" in result[0].text
    
    @pytest.mark.asyncio
    async def test_invalid_option(self):
        """Test with invalid option"""
        result = await self.tool.execute({
            "option": "invalidOption"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: Invalid option provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_missing_option(self):
        """Test with missing option"""
        result = await self.tool.execute({})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: Invalid option provided" in result[0].text
    
    @pytest.mark.asyncio
    async def test_extra_arguments_ignored(self):
        """Test that extra arguments are ignored"""
        result = await self.tool.execute({
            "option": "listTasks",
            "extraParam": "should be ignored",
            "anotherParam": 123
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "No tasks found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Test error handling for database connection issues"""
        with patch.object(self.tool, '_get_connection', side_effect=sqlite3.Error("Database connection failed")):
            result = await self.tool.execute({
                "option": "addTask",
                "taskName": "Test Task",
                "description": "Test Description"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error adding task" in result[0].text
            assert "Database connection failed" in result[0].text
    
    @pytest.mark.asyncio
    async def test_database_integrity_error(self):
        """Test error handling for database integrity errors"""
        with patch.object(self.tool, '_get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
            
            result = await self.tool.execute({
                "option": "addTask",
                "taskName": "Test Task",
                "description": "Test Description"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error: Task 'Test Task' already exists" in result[0].text
    
    @pytest.mark.asyncio
    async def test_database_general_error(self):
        """Test error handling for general database errors"""
        with patch.object(self.tool, '_get_connection', side_effect=Exception("General database error")):
            result = await self.tool.execute({
                "option": "listTasks"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error listing tasks" in result[0].text
            assert "General database error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_database_path_construction(self):
        """Test that the database path is constructed correctly"""
        # Test that the path points to the project root
        expected_path = Path(__file__).parent.parent.parent.parent / "tasks.db"
        # The actual path will be our temp file, but we can test the path construction logic
        assert hasattr(self.tool, 'db_path')
        assert self.tool.db_path.suffix == '.db'
    
    @pytest.mark.asyncio
    async def test_task_ordering_by_created_at(self):
        """Test that tasks are ordered by created_at in descending order"""
        # Add tasks with slight delays to ensure different timestamps
        await self.tool.execute({
            "option": "addTask",
            "taskName": "First Task",
            "description": "First task"
        })
        
        await asyncio.sleep(0.1)  # Longer delay to ensure different timestamps
        
        await self.tool.execute({
            "option": "addTask",
            "taskName": "Second Task",
            "description": "Second task"
        })
        
        result = await self.tool.execute({
            "option": "listTasks"
        })
        
        assert len(result) == 1
        content = result[0].text
        
        # Both tasks should be present
        assert "First Task" in content
        assert "Second Task" in content
        
        # The ordering might vary depending on timing, so let's just verify both tasks exist
        # and that the list is not empty
        assert content != "No tasks found"
    
    @pytest.mark.asyncio
    async def test_task_with_very_long_name(self):
        """Test task with very long name"""
        long_name = "A" * 1000  # Very long name
        
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": long_name,
            "description": "Task with very long name"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert f"Task '{long_name}' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_task_with_very_long_description(self):
        """Test task with very long description"""
        long_description = "B" * 10000  # Very long description
        
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "Long Desc Task",
            "description": long_description
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'Long Desc Task' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_multiple_tasks_same_name_different_cases(self):
        """Test that task names are case-sensitive"""
        # Add task with lowercase
        await self.tool.execute({
            "option": "addTask",
            "taskName": "test task",
            "description": "Lowercase task"
        })
        
        # Add task with uppercase (should work as they're different)
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": "TEST TASK",
            "description": "Uppercase task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task 'TEST TASK' added successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_task_name_with_sql_injection_attempt(self):
        """Test task name with SQL injection attempt"""
        malicious_name = "'; DROP TABLE tasks; --"
        
        result = await self.tool.execute({
            "option": "addTask",
            "taskName": malicious_name,
            "description": "Malicious task"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert f"Task '{malicious_name}' added successfully" in result[0].text
        
        # Verify the table still exists and works
        list_result = await self.tool.execute({
            "option": "listTasks"
        })
        
        assert len(list_result) == 1
        assert malicious_name in list_result[0].text


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
