#!/usr/bin/env python3
"""
Test runner script for the API project.
This script provides convenient ways to run different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type=None, verbose=False, coverage=True):
    """
    Run tests with specified options.
    
    Args:
        test_type (str): Type of tests to run (unit, integration, all)
        verbose (bool): Whether to run in verbose mode
        coverage (bool): Whether to include coverage reporting
    """
    cmd = ["python", "-m", "pytest"]
    
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    elif test_type == "auth":
        cmd.extend(["-m", "auth"])
    
    if verbose:
        cmd.append("-v")
    
    if not coverage:
        cmd.extend(["--no-cov"])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode


def run_specific_test(test_path):
    """
    Run a specific test file or test function.
    
    Args:
        test_path (str): Path to the test file or specific test
    """
    cmd = ["python", "-m", "pytest", test_path, "-v"]
    
    print(f"Running specific test: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Test passed!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test failed with exit code {e.returncode}")
        return e.returncode


def list_tests():
    """List all available tests."""
    cmd = ["python", "-m", "pytest", "--collect-only", "-q"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Available tests:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error listing tests: {e}")


def main():
    parser = argparse.ArgumentParser(description="Test runner for the API project")
    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "api", "auth", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--test", "-T",
        help="Run a specific test file or test function"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available tests"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return 0
    
    if args.test:
        return run_specific_test(args.test)
    
    return run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=not args.no_coverage
    )


if __name__ == "__main__":
    sys.exit(main()) 