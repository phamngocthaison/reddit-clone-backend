#!/usr/bin/env python3
"""
Reddit Clone Backend - Test Runner
Simple script to run different types of tests
"""

import sys
import subprocess
import os

def run_deploy_test():
    """Run quick deployment test"""
    print("🚀 Running deployment test...")
    return subprocess.run([sys.executable, "test_deploy.py"]).returncode == 0

def run_full_tests():
    """Run full API test suite"""
    print("🧪 Running full API test suite...")
    return subprocess.run([sys.executable, "run_api_tests.py"]).returncode == 0

def run_quick_tests():
    """Run quick tests from tests/api/"""
    print("⚡ Running quick tests...")
    return subprocess.run([sys.executable, "run_api_tests.py", "--quick"]).returncode == 0

def run_module_test(module):
    """Run specific module test"""
    print(f"🔧 Running {module} tests...")
    return subprocess.run([sys.executable, "run_api_tests.py", "--module", module]).returncode == 0

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Reddit Clone Backend - Test Runner")
        print("=" * 40)
        print("Usage:")
        print("  python3 test.py deploy     - Quick deployment test")
        print("  python3 test.py full       - Full test suite")
        print("  python3 test.py quick      - Quick tests")
        print("  python3 test.py auth       - Authentication tests")
        print("  python3 test.py posts      - Posts tests")
        print("  python3 test.py comments   - Comments tests")
        print("  python3 test.py subreddits - Subreddits tests")
        print("  python3 test.py feeds      - Feeds tests")
        print("=" * 40)
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "deploy":
        success = run_deploy_test()
    elif command == "full":
        success = run_full_tests()
    elif command == "quick":
        success = run_quick_tests()
    elif command in ["auth", "posts", "comments", "subreddits", "feeds"]:
        success = run_module_test(command)
    else:
        print(f"❌ Unknown command: {command}")
        return 1
    
    if success:
        print("\n🎉 Tests completed successfully!")
        return 0
    else:
        print("\n❌ Tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
