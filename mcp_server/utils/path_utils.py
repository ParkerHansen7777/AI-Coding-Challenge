"""
Path utility functions

This module contains utility functions for handling file paths
and resolving relative paths to absolute paths.
"""

import os
from pathlib import Path
from ..config.settings import PROJECT_ROOT


def resolve_file_path(file_path: str) -> Path:
    """
    Resolve a file path to an absolute Path object.
    
    Args:
        file_path: The file path to resolve (can be relative or absolute)
        
    Returns:
        Path: Absolute path to the file
    """
    if os.path.isabs(file_path):
        return Path(file_path)
    else:
        return PROJECT_ROOT / file_path
