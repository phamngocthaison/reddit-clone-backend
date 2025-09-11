#!/usr/bin/env python3
"""
Main API test runner - runs all API tests from tests/api/ folder
"""

import sys
import os
import subprocess
import time
from datetime import datetime

def run_api_tests():
    """Run all API tests from tests/api/ folder"""
    
    # Change to tests/api directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests', 'api')
    os.chdir(test_dir)
    
    print("🚀 Reddit Clone Backend - API Test Suite")
    print("=" * 60)
    print(f"📅 Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Test Directory: {test_dir}")
    print("=" * 60)
    print()
    
    # Run the main test runner
    try:
        result = subprocess.run([sys.executable, "test_all_apis.py"], 
                              capture_output=False, 
                              timeout=600)  # 10 minute timeout
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Test suite timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_quick_test():
    """Run quick API test"""
    
    # Change to tests/api directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests', 'api')
    os.chdir(test_dir)
    
    print("⚡ Quick API Test")
    print("=" * 40)
    
    try:
        result = subprocess.run([sys.executable, "quick_test.py"], 
                              capture_output=False, 
                              timeout=120)  # 2 minute timeout
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Quick test timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running quick test: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reddit Clone Backend API Test Runner")
    parser.add_argument("--quick", "-q", action="store_true", 
                       help="Run quick test only")
    parser.add_argument("--module", "-m", 
                       choices=["auth", "posts", "comments", "subreddits", "feeds"],
                       help="Run specific module test")
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_test()
    elif args.module:
        # Run specific module
        test_dir = os.path.join(os.path.dirname(__file__), 'tests', 'api')
        os.chdir(test_dir)
        
        module_files = {
            "auth": "test_auth_apis.py",
            "posts": "test_posts_apis.py", 
            "comments": "test_comments_apis.py",
            "subreddits": "test_subreddits_apis.py",
            "feeds": "test_feeds_apis.py"
        }
        
        file_name = module_files[args.module]
        print(f"🔧 Running {args.module} tests...")
        
        try:
            result = subprocess.run([sys.executable, file_name], 
                                  capture_output=False, 
                                  timeout=300)  # 5 minute timeout
            success = result.returncode == 0
        except Exception as e:
            print(f"❌ Error running {args.module} tests: {e}")
            success = False
    else:
        success = run_api_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
