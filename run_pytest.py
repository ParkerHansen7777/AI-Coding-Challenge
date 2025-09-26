#!/usr/bin/env python3
"""
Pytest runner script for the AI Coding Challenge project

This script provides various ways to run tests using pytest with different options.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{description}")
    print("=" * 50)
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    """Main function to handle command line arguments and run tests"""
    parser = argparse.ArgumentParser(description="Run tests using pytest")
    parser.add_argument("--coverage", "-c", action="store_true", 
                       help="Run tests with coverage report")
    parser.add_argument("--html", action="store_true", 
                       help="Generate HTML coverage report")
    parser.add_argument("--slow", action="store_true", 
                       help="Include slow tests")
    parser.add_argument("--unit", action="store_true", 
                       help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", 
                       help="Run only integration tests")
    parser.add_argument("--file", "-f", type=str, 
                       help="Run tests from specific file")
    parser.add_argument("--test", "-t", type=str, 
                       help="Run specific test")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Quiet output")
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd_parts = ["py", "-m", "pytest"]
    
    # Add test path
    if args.file:
        cmd_parts.append(args.file)
    elif args.unit:
        cmd_parts.append("tests/unit/")
    elif args.integration:
        cmd_parts.append("tests/integration/")
    else:
        cmd_parts.append("tests/")
    
    # Add specific test
    if args.test:
        cmd_parts.extend(["-k", args.test])
    
    # Add verbosity
    if args.verbose:
        cmd_parts.append("-v")
    elif args.quiet:
        cmd_parts.append("-q")
    
    # Add coverage
    if args.coverage:
        cmd_parts.extend([
            "--cov=mcp_server.tools",
            "--cov-report=term-missing",
            "--cov-report=html" if args.html else ""
        ])
        # Remove empty string if html is not requested
        cmd_parts = [part for part in cmd_parts if part]
    
    # Add slow tests filter
    if not args.slow:
        cmd_parts.extend(["-m", '"not slow"'])
    
    # Join command parts
    cmd = " ".join(cmd_parts)
    
    # Run the command
    return run_command(cmd, "Running pytest tests")


if __name__ == "__main__":
    sys.exit(main())
