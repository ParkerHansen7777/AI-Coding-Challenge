"""
Task Manager Tool Implementation

A tool for managing tasks with SQLite database storage.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp.types import Tool, TextContent
from .base_tool import BaseTool


class TaskManagerTool(BaseTool):
    """Tool for managing tasks with SQLite storage"""
    
    def __init__(self):
        # Set up the database file path in the project root
        project_root = Path(__file__).parent.parent.parent
        self.db_path = project_root / "tasks.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    status TEXT NOT NULL CHECK (status IN ('complete', 'not complete')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_name ON tasks(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
    
    def _get_connection(self):
        """Get a database connection with row factory for named access"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @property
    def tool_definition(self) -> Tool:
        """Return the tool definition for MCP registration"""
        return Tool(
            name="taskManager",
            description="Manage tasks - add, list, and mark as complete",
            inputSchema={
                "type": "object",
                "properties": {
                    "option": {
                        "type": "string",
                        "enum": ["addTask", "listTasks", "completeTask"],
                        "description": "Task management option"
                    },
                    "taskName": {
                        "type": "string",
                        "description": "Name of the task (required for addTask and completeTask)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the task (required for addTask)"
                    },
                    "completionStatus": {
                        "type": "string",
                        "enum": ["complete", "not complete"],
                        "description": "Completion status (required for completeTask)"
                    }
                },
                "required": ["option"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the task management tool"""
        option = arguments.get("option")
        
        if option == "addTask":
            return await self._add_task(arguments)
        elif option == "listTasks":
            return await self._list_tasks()
        elif option == "completeTask":
            return await self._complete_task(arguments)
        else:
            return [TextContent(type="text", text="Error: Invalid option provided")]
    
    async def _add_task(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Add a new task"""
        task_name = arguments.get("taskName")
        description = arguments.get("description")
        
        if not task_name or not description:
            return [TextContent(type="text", text="Error: taskName and description are required for addTask")]
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO tasks (name, description, status) VALUES (?, ?, 'not complete')",
                    (task_name, description)
                )
                conn.commit()
            
            return [TextContent(type="text", text=f"Task '{task_name}' added successfully")]
            
        except sqlite3.IntegrityError:
            return [TextContent(type="text", text=f"Error: Task '{task_name}' already exists")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding task: {str(e)}")]
    
    async def _list_tasks(self) -> List[TextContent]:
        """List all tasks"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC")
                tasks = cursor.fetchall()
            
            if not tasks:
                return [TextContent(type="text", text="No tasks found")]
            
            task_list = []
            for task in tasks:
                status_icon = "✅" if task['status'] == 'complete' else "⏳"
                created_date = task['created_at']
                # Format date for better readability
                try:
                    dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = created_date
                
                task_list.append(
                    f"{status_icon} **{task['name']}**\n"
                    f"   Description: {task['description'] or 'No description'}\n"
                    f"   Status: {task['status']}\n"
                    f"   Created: {formatted_date}\n"
                    f"   ID: {task['id']}\n"
                )
            
            return [TextContent(type="text", text="\n".join(task_list))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing tasks: {str(e)}")]
    
    async def _complete_task(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Mark a task as complete or not complete"""
        task_name = arguments.get("taskName")
        completion_status = arguments.get("completionStatus")
        
        if not task_name or not completion_status:
            return [TextContent(type="text", text="Error: taskName and completionStatus are required for completeTask")]
        
        try:
            with self._get_connection() as conn:
                # First check if task exists and get current status
                cursor = conn.execute("SELECT status FROM tasks WHERE name = ?", (task_name,))
                task = cursor.fetchone()
                
                if not task:
                    return [TextContent(type="text", text=f"Error: Task '{task_name}' not found")]
                
                old_status = task['status']
                
                # Update the task
                cursor = conn.execute(
                    "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                    (completion_status, task_name)
                )
                conn.commit()
            
            return [TextContent(
                type="text", 
                text=f"Task '{task_name}' status changed from '{old_status}' to '{completion_status}'"
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error updating task: {str(e)}")]
