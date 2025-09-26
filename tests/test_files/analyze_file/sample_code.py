#!/usr/bin/env python3
"""
Sample Python file for testing
This file contains various types of content for testing purposes.
"""

import os
import sys
from pathlib import Path

# TODO: Add error handling for file operations
def read_file(filename):
    """Read a file and return its contents"""
    with open(filename, 'r') as f:
        return f.read()

# TODO: Implement better logging
def log_message(message):
    """Log a message to console"""
    print(f"LOG: {message}")

class TestClass:
    """A test class for demonstration"""
    
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        """Return the stored value"""
        return self.value

if __name__ == "__main__":
    # Main execution block
    test = TestClass()
    print(f"Value: {test.get_value()}")
