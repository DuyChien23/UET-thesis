#!/usr/bin/env python3
"""
Script to run pytest on individual test files to avoid event_loop fixture collision
"""

import os
import subprocess
import sys

def run_test_file(file_path, verbose=True):
    """Run pytest on a single test file using the run_tests.sh script"""
    print(f"\n\n=== Running tests in {file_path} ===\n")
    cmd = ["./run_tests.sh", file_path]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0  # True if tests passed

def main():
    """Run all test files individually"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # List of test files to run
    test_files = [
        "tests/test_algorithms_api.py",
        "tests/test_auth_api.py",
        "tests/test_verification_api.py",
        # Add other test files here as needed
    ]
    
    # Optional: Add specific test cases (if some of the above are still failing)
    test_specific_cases = [
        # "tests/test_auth_api.py::test_basic_user_creation",
    ]
    
    all_passed = True
    failed_tests = []
    
    # Run test files
    for test_file in test_files:
        if not run_test_file(test_file):
            all_passed = False
            failed_tests.append(test_file)
    
    # Run specific test cases
    for test_case in test_specific_cases:
        if not run_test_file(test_case):
            all_passed = False
            failed_tests.append(test_case)
    
    if all_passed:
        print("\n\n✅ All tests passed successfully!")
        return 0
    else:
        print("\n\n❌ Some tests failed!")
        print("Failed tests:")
        for test in failed_tests:
            print(f"  - {test}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 