#!/usr/bin/env python3
"""
Quick Test Script for Reddit Clone Backend v2.5
Based on Postman Collection: Reddit_Clone_Backend_v2.5.postman_collection.json

This script tests all major endpoints to ensure deployment is working correctly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_USERNAME = "testuser123"
TEST_PASSWORD = "TestPass123"

# Test data
TEST_SUBREDDIT_ID = "subreddit_1757518063_01b8625d"
TEST_POST_ID = "post_1757508287_f8e2cbd7"
TEST_COMMENT_ID = "comment_1757509982_351caa27"

class RedditCloneTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time()
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data)"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            return response.status_code < 400, response_data
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test 1: Register User
        success, data = self.make_request("POST", "/auth/register", {
            "email": TEST_USER_EMAIL,
            "username": TEST_USER_USERNAME,
            "password": TEST_PASSWORD
        })
        self.log_test("Register User", success, 
                     "User already exists" if not success and "already exists" in str(data) else "")
        
        # Test 2: Login with Email
        success, data = self.make_request("POST", "/auth/login", {
            "email": TEST_USER_EMAIL,
            "password": TEST_PASSWORD
        })
        if success and "access_token" in data:
            self.access_token = data["access_token"]
            self.user_id = data.get("user_id")
        self.log_test("Login with Email", success, 
                     f"Got token: {bool(self.access_token)}")
        
        # Test 3: Get Current User Profile
        if self.access_token:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-User-ID": self.user_id
            }
            success, data = self.make_request("GET", "/auth/me", headers=headers)
            self.log_test("Get Current User Profile", success)
    
    def test_posts(self):
        """Test posts endpoints"""
        print("\n📝 Testing Posts...")
        
        if not self.access_token:
            self.log_test("Posts Tests", False, "No access token available")
            return
        
        headers = {"X-User-ID": self.user_id}
        
        # Test 1: Create Post
        success, data = self.make_request("POST", "/posts/create", {
            "title": "Quick Test Post",
            "content": "This is a test post for quick testing",
            "subreddit_id": TEST_SUBREDDIT_ID,
            "post_type": "text",
            "is_nsfw": False,
            "is_spoiler": False,
            "flair": "Test",
            "tags": ["test", "quick"]
        }, headers)
        if success and "post_id" in data:
            self.test_post_id = data["post_id"]
        self.log_test("Create Post", success, 
                     f"Created post: {self.test_post_id if success else 'Failed'}")
        
        # Test 2: Get Posts
        success, data = self.make_request("GET", "/posts?limit=5&offset=0&sort=new")
        self.log_test("Get Posts", success, 
                     f"Retrieved {len(data.get('data', {}).get('posts', []))} posts" if success else "")
        
        # Test 3: Get Post by ID
        post_id = self.test_post_id if hasattr(self, 'test_post_id') else TEST_POST_ID
        success, data = self.make_request("GET", f"/posts/{post_id}")
        self.log_test("Get Post by ID", success, 
                     f"Post ID: {post_id}" if success else "")
        
        # Test 4: Vote Post
        success, data = self.make_request("POST", f"/posts/{post_id}/vote", {
            "vote_type": "upvote"
        }, headers)
        self.log_test("Vote Post", success)
    
    def test_comments(self):
        """Test comments endpoints"""
        print("\n💬 Testing Comments...")
        
        if not self.access_token:
            self.log_test("Comments Tests", False, "No access token available")
            return
        
        headers = {"X-User-ID": self.user_id}
        post_id = getattr(self, 'test_post_id', TEST_POST_ID)
        
        # Test 1: Create Comment
        success, data = self.make_request("POST", "/comments/create", {
            "post_id": post_id,
            "content": "This is a test comment for quick testing",
            "parent_id": None,
            "comment_type": "comment",
            "is_nsfw": False,
            "is_spoiler": False,
            "flair": "Test",
            "tags": ["test", "comment"]
        }, headers)
        if success and "comment_id" in data:
            self.test_comment_id = data["comment_id"]
        self.log_test("Create Comment", success, 
                     f"Created comment: {self.test_comment_id if success else 'Failed'}")
        
        # Test 2: Get Comments
        success, data = self.make_request("GET", f"/comments?post_id={post_id}&limit=5&offset=0")
        self.log_test("Get Comments", success, 
                     f"Retrieved {len(data.get('data', {}).get('comments', []))} comments" if success else "")
        
        # Test 3: Get Comment by ID
        comment_id = getattr(self, 'test_comment_id', TEST_COMMENT_ID)
        success, data = self.make_request("GET", f"/comments/{comment_id}")
        self.log_test("Get Comment by ID", success, 
                     f"Comment ID: {comment_id}" if success else "")
        
        # Test 4: Vote Comment
        success, data = self.make_request("POST", f"/comments/{comment_id}/vote", {
            "vote_type": "upvote"
        }, headers)
        self.log_test("Vote Comment", success)
    
    def test_subreddits(self):
        """Test subreddits endpoints"""
        print("\n🏘️ Testing Subreddits...")
        
        if not self.access_token:
            self.log_test("Subreddits Tests", False, "No access token available")
            return
        
        headers = {"X-User-ID": self.user_id}
        
        # Test 1: Get Subreddits
        success, data = self.make_request("GET", "/subreddits?limit=5&offset=0&sort=new")
        self.log_test("Get Subreddits", success, 
                     f"Retrieved {len(data.get('data', {}).get('subreddits', []))} subreddits" if success else "")
        
        # Test 2: Get Subreddit by ID
        success, data = self.make_request("GET", f"/subreddits/{TEST_SUBREDDIT_ID}", headers)
        self.log_test("Get Subreddit by ID", success, 
                     f"Subreddit ID: {TEST_SUBREDDIT_ID}" if success else "")
        
        # Test 3: Get Subreddit Posts
        success, data = self.make_request("GET", f"/subreddits/{TEST_SUBREDDIT_ID}/posts?limit=5&offset=0&sort=new")
        self.log_test("Get Subreddit Posts", success, 
                     f"Retrieved {len(data.get('data', {}).get('posts', []))} posts" if success else "")
        
        # Test 4: Join Subreddit
        success, data = self.make_request("POST", f"/subreddits/{TEST_SUBREDDIT_ID}/join", {}, headers)
        self.log_test("Join Subreddit", success)
    
    def test_user_profiles(self):
        """Test user profile endpoints"""
        print("\n👤 Testing User Profiles...")
        
        if not self.user_id:
            self.log_test("User Profile Tests", False, "No user ID available")
            return
        
        # Test 1: Get Public User Profile
        success, data = self.make_request("GET", f"/users/{self.user_id}")
        self.log_test("Get Public User Profile", success, 
                     f"User ID: {self.user_id}" if success else "")
        
        # Test 2: Get User Posts
        success, data = self.make_request("GET", f"/users/{self.user_id}/posts?limit=5&offset=0&sort=new")
        self.log_test("Get User Posts", success, 
                     f"Retrieved {len(data.get('data', {}).get('posts', []))} posts" if success else "")
        
        # Test 3: Get User Comments
        success, data = self.make_request("GET", f"/users/{self.user_id}/comments?limit=5&offset=0&sort=new")
        self.log_test("Get User Comments", success, 
                     f"Retrieved {len(data.get('data', {}).get('comments', []))} comments" if success else "")
    
    def test_feeds(self):
        """Test news feeds endpoints"""
        print("\n📰 Testing News Feeds...")
        
        if not self.access_token:
            self.log_test("Feeds Tests", False, "No access token available")
            return
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-User-ID": self.user_id
        }
        
        # Test 1: Get Feed
        success, data = self.make_request("GET", "/feeds?limit=5&offset=0&sort=new", headers=headers)
        self.log_test("Get Feed", success, 
                     f"Retrieved {len(data.get('data', {}).get('posts', []))} feed posts" if success else "")
        
        # Test 2: Get Feed Stats
        success, data = self.make_request("GET", "/feeds/stats", headers=headers)
        self.log_test("Get Feed Stats", success)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Reddit Clone Backend Quick Test")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run test suites
        self.test_authentication()
        self.test_posts()
        self.test_comments()
        self.test_subreddits()
        self.test_user_profiles()
        self.test_feeds()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️ Duration: {duration:.2f}s")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 50)
        
        # Return exit code
        return 0 if failed_tests == 0 else 1

def main():
    """Main function"""
    tester = RedditCloneTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
