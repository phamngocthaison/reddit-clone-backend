#!/usr/bin/env python3
"""
Quick test runner with options for different test scenarios
"""

import sys
import argparse
import subprocess
import time
from typing import List

def run_command(cmd: List[str], timeout: int = 300) -> bool:
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Reddit Clone Backend API Test Runner")
    parser.add_argument("--module", "-m", 
                       choices=["auth", "posts", "comments", "subreddits", "feeds", "all"],
                       default="all",
                       help="Test module to run (default: all)")
    parser.add_argument("--timeout", "-t", 
                       type=int, 
                       default=300,
                       help="Timeout in seconds (default: 300)")
    parser.add_argument("--quick", "-q", 
                       action="store_true",
                       help="Run quick tests only")
    parser.add_argument("--verbose", "-v", 
                       action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    print("🚀 Reddit Clone Backend API Test Runner")
    print("=" * 50)
    
    # Map module names to files
    module_files = {
        "auth": "test_auth_apis.py",
        "posts": "test_posts_apis.py", 
        "comments": "test_comments_apis.py",
        "subreddits": "test_subreddits_apis.py",
        "feeds": "test_feeds_apis.py",
        "all": "test_all_apis.py"
    }
    
    if args.module == "all":
        print(f"📦 Running all test modules...")
        print(f"⏱️  Timeout: {args.timeout} seconds")
    else:
        print(f"📦 Running {args.module} tests...")
        print(f"⏱️  Timeout: {args.timeout} seconds")
    
    print("-" * 50)
    
    # Run the tests
    start_time = time.time()
    
    if args.module == "all":
        success = run_command([sys.executable, "test_all_apis.py"], args.timeout)
    else:
        file_name = module_files[args.module]
        success = run_command([sys.executable, file_name], args.timeout)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 50)
    if success:
        print(f"✅ Tests completed successfully in {duration:.2f} seconds")
        return 0
    else:
        print(f"❌ Tests failed after {duration:.2f} seconds")
        return 1

if __name__ == "__main__":
    exit(main())
