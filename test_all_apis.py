#!/usr/bin/env python3
"""
Main test runner for all Reddit Clone Backend APIs
Runs all test suites and provides comprehensive reporting
"""

import sys
import time
import subprocess
from typing import Dict, Any, List, Tuple
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.test_modules = [
            {
                "name": "Authentication APIs",
                "file": "test_auth_apis.py",
                "description": "User registration, login, logout, password reset"
            },
            {
                "name": "Posts APIs", 
                "file": "test_posts_apis.py",
                "description": "Create, read, update, delete posts, voting"
            },
            {
                "name": "Comments APIs",
                "file": "test_comments_apis.py", 
                "description": "Create, read, update, delete comments, replies, voting"
            },
            {
                "name": "Subreddits APIs",
                "file": "test_subreddits_apis.py",
                "description": "Create, manage subreddits, join/leave, moderation"
            },
            {
                "name": "Feeds APIs",
                "file": "test_feeds_apis.py",
                "description": "Personalized news feeds, refresh, statistics"
            }
        ]
        
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def print_header(self):
        """Print test runner header"""
        print("=" * 80)
        print("🚀 REDDIT CLONE BACKEND - COMPREHENSIVE API TEST SUITE")
        print("=" * 80)
        print(f"📅 Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod")
        print(f"📋 Test Modules: {len(self.test_modules)}")
        print("=" * 80)
        print()
    
    def print_module_header(self, module: Dict[str, str], index: int):
        """Print module test header"""
        print(f"📦 [{index+1}/{len(self.test_modules)}] {module['name']}")
        print(f"📝 {module['description']}")
        print(f"🔧 Running: python {module['file']}")
        print("-" * 60)
    
    def run_module_test(self, module: Dict[str, str]) -> Tuple[bool, str, float]:
        """Run a single test module"""
        start_time = time.time()
        
        try:
            # Run the test module
            result = subprocess.run(
                [sys.executable, module["file"]],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per module
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output, duration
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            return False, "Test module timed out after 5 minutes", duration
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            return False, f"Error running test module: {str(e)}", duration
    
    def print_module_result(self, module: Dict[str, str], success: bool, duration: float, output: str):
        """Print module test result"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {module['name']} ({duration:.2f}s)")
        
        if not success:
            print("   Error Details:")
            # Print last few lines of output for debugging
            lines = output.strip().split('\n')
            for line in lines[-5:]:
                if line.strip():
                    print(f"   {line}")
        print()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test modules"""
        self.start_time = time.time()
        self.print_header()
        
        total_tests = 0
        passed_tests = 0
        failed_modules = []
        
        for i, module in enumerate(self.test_modules):
            self.print_module_header(module, i)
            
            success, output, duration = self.run_module_test(module)
            self.print_module_result(module, success, duration, output)
            
            # Store results
            self.results[module["name"]] = {
                "success": success,
                "duration": duration,
                "output": output,
                "file": module["file"]
            }
            
            if success:
                passed_tests += 1
            else:
                failed_modules.append(module["name"])
            
            total_tests += 1
        
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        # Print final summary
        self.print_final_summary(total_tests, passed_tests, failed_modules, total_duration)
        
        return {
            "total_modules": total_tests,
            "passed_modules": passed_tests,
            "failed_modules": failed_modules,
            "total_duration": total_duration,
            "results": self.results
        }
    
    def print_final_summary(self, total: int, passed: int, failed_modules: List[str], duration: float):
        """Print final test summary"""
        print("=" * 80)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"📦 Total Modules: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {len(failed_modules)}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        if failed_modules:
            print("❌ Failed Modules:")
            for module in failed_modules:
                print(f"   • {module}")
            print()
        
        print("📋 Detailed Results:")
        for module_name, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            print(f"   {status} {module_name} ({result['duration']:.2f}s)")
        
        print()
        if passed == total:
            print("🎉 ALL TESTS PASSED! 🎉")
            print("🚀 Your Reddit Clone Backend APIs are working perfectly!")
        else:
            print("⚠️  SOME TESTS FAILED")
            print("🔧 Please check the failed modules above for details")
        
        print("=" * 80)
    
    def save_results_to_file(self, filename: str = None):
        """Save test results to a file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        import json
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "total_modules": len(self.results),
            "passed_modules": sum(1 for r in self.results.values() if r["success"]),
            "failed_modules": [name for name, r in self.results.items() if not r["success"]],
            "total_duration": self.end_time - self.start_time if self.end_time and self.start_time else 0,
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"📄 Test results saved to: {filename}")
        return filename

def main():
    """Main function to run all tests"""
    runner = TestRunner()
    
    try:
        results = runner.run_all_tests()
        
        # Save results to file
        runner.save_results_to_file()
        
        # Return appropriate exit code
        if results["passed_modules"] == results["total_modules"]:
            return 0  # All tests passed
        else:
            return 1  # Some tests failed
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
