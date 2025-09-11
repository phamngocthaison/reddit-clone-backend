#!/usr/bin/env python3
"""
Test script for Posts APIs
Tests all posts endpoints according to API contract
"""

import requests
import json
import time
import random
import string
from typing import Dict, Any, Optional, List

# Configuration
BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"
HEADERS = {
    "Content-Type": "application/json"
}

class PostsAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_user_id = f"user_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        self.test_subreddit_id = f"subreddit_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        self.created_posts = []
        
    def print_test_result(self, test_name: str, success: bool, response: requests.Response, expected_status: int = None):
        """Print formatted test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if not success:
            print(f"   Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        print()
    
    def get_headers_with_user(self) -> Dict[str, str]:
        """Get headers with test user ID"""
        return {
            **HEADERS,
            "X-User-ID": self.test_user_id
        }
    
    def test_create_post(self) -> bool:
        """Test create post endpoint"""
        print("📝 Testing Create Post...")
        
        post_data = {
            "title": "Test Post Title",
            "content": "This is a test post content with some interesting information.",
            "subreddit_id": self.test_subreddit_id,
            "post_type": "text",
            "url": None,
            "media_urls": None,
            "is_nsfw": False,
            "is_spoiler": False,
            "flair": "Discussion",
            "tags": ["test", "api", "programming"]
        }
        
        response = requests.post(
            f"{self.base_url}/posts/create",
            headers=self.get_headers_with_user(),
            json=post_data
        )
        
        success = response.status_code == 201
        self.print_test_result("Create Post", success, response, 201)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                post = data["data"]["post"]
                self.created_posts.append(post["post_id"])
                print(f"   Post ID: {post['post_id']}")
                print(f"   Title: {post['title']}")
                print(f"   Author: {post['author_username']}")
        
        return success
    
    def test_create_post_validation_errors(self) -> bool:
        """Test create post with validation errors"""
        print("📝 Testing Create Post - Validation Errors...")
        
        test_cases = [
            {
                "name": "Empty title",
                "data": {
                    "title": "",
                    "content": "Test content",
                    "subreddit_id": self.test_subreddit_id,
                    "post_type": "text"
                },
                "expected_status": 400
            },
            {
                "name": "Missing title",
                "data": {
                    "content": "Test content",
                    "subreddit_id": self.test_subreddit_id,
                    "post_type": "text"
                },
                "expected_status": 400
            },
            {
                "name": "Missing content for text post",
                "data": {
                    "title": "Test Title",
                    "subreddit_id": self.test_subreddit_id,
                    "post_type": "text"
                },
                "expected_status": 400
            },
            {
                "name": "Invalid post type",
                "data": {
                    "title": "Test Title",
                    "content": "Test content",
                    "subreddit_id": self.test_subreddit_id,
                    "post_type": "invalid_type"
                },
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/posts/create",
                headers=self.get_headers_with_user(),
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Create Post Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_create_link_post(self) -> bool:
        """Test create link post"""
        print("📝 Testing Create Link Post...")
        
        post_data = {
            "title": "Interesting Article",
            "content": "Check out this amazing article!",
            "subreddit_id": self.test_subreddit_id,
            "post_type": "link",
            "url": "https://example.com/article",
            "media_urls": None,
            "is_nsfw": False,
            "is_spoiler": False,
            "flair": "Link",
            "tags": ["article", "news"]
        }
        
        response = requests.post(
            f"{self.base_url}/posts/create",
            headers=self.get_headers_with_user(),
            json=post_data
        )
        
        success = response.status_code == 201
        self.print_test_result("Create Link Post", success, response, 201)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                post = data["data"]["post"]
                self.created_posts.append(post["post_id"])
                print(f"   Post ID: {post['post_id']}")
                print(f"   URL: {post['url']}")
        
        return success
    
    def test_get_posts(self) -> bool:
        """Test get posts endpoint"""
        print("📝 Testing Get Posts...")
        
        response = requests.get(
            f"{self.base_url}/posts",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Posts", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                posts = data["data"]["posts"]
                print(f"   Retrieved {len(posts)} posts")
                print(f"   Total count: {data['data'].get('total_count', 0)}")
        
        return success
    
    def test_get_posts_with_filters(self) -> bool:
        """Test get posts with various filters"""
        print("📝 Testing Get Posts - With Filters...")
        
        test_cases = [
            {
                "name": "Filter by subreddit",
                "params": {"subreddit_id": self.test_subreddit_id, "limit": 10}
            },
            {
                "name": "Filter by author",
                "params": {"author_id": self.test_user_id, "limit": 10}
            },
            {
                "name": "Sort by new",
                "params": {"sort": "new", "limit": 5}
            },
            {
                "name": "Filter by post type",
                "params": {"post_type": "text", "limit": 5}
            },
            {
                "name": "Filter NSFW",
                "params": {"is_nsfw": "false", "limit": 5}
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.get(
                f"{self.base_url}/posts",
                headers=self.get_headers_with_user(),
                params=test_case["params"]
            )
            
            success = response.status_code == 200
            self.print_test_result(f"Get Posts - {test_case['name']}", success, response, 200)
            all_passed = all_passed and success
        
        return all_passed
    
    def test_get_post_by_id(self) -> bool:
        """Test get post by ID"""
        print("📝 Testing Get Post by ID...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        response = requests.get(
            f"{self.base_url}/posts/{post_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Post by ID", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                post = data["data"]["post"]
                print(f"   Post ID: {post['post_id']}")
                print(f"   Title: {post['title']}")
        
        return success
    
    def test_get_post_by_id_not_found(self) -> bool:
        """Test get post by ID - not found"""
        print("📝 Testing Get Post by ID - Not Found...")
        
        fake_post_id = f"post_{int(time.time())}_fake"
        response = requests.get(
            f"{self.base_url}/posts/{fake_post_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 404
        self.print_test_result("Get Post by ID - Not Found", success, response, 404)
        
        return success
    
    def test_update_post(self) -> bool:
        """Test update post"""
        print("📝 Testing Update Post...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        update_data = {
            "title": "Updated Post Title",
            "content": "Updated content with more information",
            "is_nsfw": False,
            "is_spoiler": True,
            "flair": "Updated Flair",
            "tags": ["updated", "test"]
        }
        
        response = requests.put(
            f"{self.base_url}/posts/{post_id}",
            headers=self.get_headers_with_user(),
            json=update_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Update Post", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                post = data["data"]["post"]
                print(f"   Updated Title: {post['title']}")
                print(f"   Updated Flair: {post['flair']}")
        
        return success
    
    def test_update_post_access_denied(self) -> bool:
        """Test update post - access denied (different user)"""
        print("📝 Testing Update Post - Access Denied...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        different_user_headers = {
            **HEADERS,
            "X-User-ID": f"user_{int(time.time())}_different"
        }
        
        update_data = {
            "title": "Unauthorized Update"
        }
        
        response = requests.put(
            f"{self.base_url}/posts/{post_id}",
            headers=different_user_headers,
            json=update_data
        )
        
        success = response.status_code == 403
        self.print_test_result("Update Post - Access Denied", success, response, 403)
        
        return success
    
    def test_vote_post(self) -> bool:
        """Test vote post"""
        print("📝 Testing Vote Post...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        vote_data = {
            "vote_type": "upvote"
        }
        
        response = requests.post(
            f"{self.base_url}/posts/{post_id}/vote",
            headers=self.get_headers_with_user(),
            json=vote_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Vote Post - Upvote", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                stats = data["data"]["stats"]
                print(f"   Score: {stats['score']}")
                print(f"   Upvotes: {stats['upvotes']}")
        
        return success
    
    def test_vote_post_downvote(self) -> bool:
        """Test vote post - downvote"""
        print("📝 Testing Vote Post - Downvote...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        vote_data = {
            "vote_type": "downvote"
        }
        
        response = requests.post(
            f"{self.base_url}/posts/{post_id}/vote",
            headers=self.get_headers_with_user(),
            json=vote_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Vote Post - Downvote", success, response, 200)
        
        return success
    
    def test_vote_post_remove(self) -> bool:
        """Test vote post - remove vote"""
        print("📝 Testing Vote Post - Remove Vote...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        vote_data = {
            "vote_type": "remove"
        }
        
        response = requests.post(
            f"{self.base_url}/posts/{post_id}/vote",
            headers=self.get_headers_with_user(),
            json=vote_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Vote Post - Remove Vote", success, response, 200)
        
        return success
    
    def test_vote_post_validation_errors(self) -> bool:
        """Test vote post with validation errors"""
        print("📝 Testing Vote Post - Validation Errors...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        
        test_cases = [
            {
                "name": "Invalid vote type",
                "data": {"vote_type": "invalid"},
                "expected_status": 400
            },
            {
                "name": "Missing vote type",
                "data": {},
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/posts/{post_id}/vote",
                headers=self.get_headers_with_user(),
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Vote Post Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_delete_post(self) -> bool:
        """Test delete post"""
        print("📝 Testing Delete Post...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        # Use the last created post for deletion
        post_id = self.created_posts[-1]
        
        response = requests.delete(
            f"{self.base_url}/posts/{post_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Delete Post", success, response, 200)
        
        if success:
            # Remove from our list
            self.created_posts.remove(post_id)
        
        return success
    
    def test_delete_post_access_denied(self) -> bool:
        """Test delete post - access denied (different user)"""
        print("📝 Testing Delete Post - Access Denied...")
        
        if not self.created_posts:
            print("   ⚠️  Skipping - No created posts")
            return True
        
        post_id = self.created_posts[0]
        different_user_headers = {
            **HEADERS,
            "X-User-ID": f"user_{int(time.time())}_different"
        }
        
        response = requests.delete(
            f"{self.base_url}/posts/{post_id}",
            headers=different_user_headers
        )
        
        success = response.status_code == 403
        self.print_test_result("Delete Post - Access Denied", success, response, 403)
        
        return success
    
    def test_get_posts_trailing_slash(self) -> bool:
        """Test get posts with trailing slash (edge case)"""
        print("📝 Testing Get Posts - Trailing Slash...")
        
        response = requests.get(
            f"{self.base_url}/posts/",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Posts - Trailing Slash", success, response, 200)
        
        return success
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all posts tests"""
        print("🚀 Starting Posts API Tests...")
        print("=" * 60)
        
        results = {}
        
        # Create posts first
        results["create_post"] = self.test_create_post()
        results["create_link_post"] = self.test_create_link_post()
        results["create_post_validation"] = self.test_create_post_validation_errors()
        
        # Get posts tests
        results["get_posts"] = self.test_get_posts()
        results["get_posts_filters"] = self.test_get_posts_with_filters()
        results["get_posts_trailing_slash"] = self.test_get_posts_trailing_slash()
        
        # Get post by ID tests
        results["get_post_by_id"] = self.test_get_post_by_id()
        results["get_post_by_id_not_found"] = self.test_get_post_by_id_not_found()
        
        # Update post tests
        results["update_post"] = self.test_update_post()
        results["update_post_access_denied"] = self.test_update_post_access_denied()
        
        # Vote post tests
        results["vote_post_upvote"] = self.test_vote_post()
        results["vote_post_downvote"] = self.test_vote_post_downvote()
        results["vote_post_remove"] = self.test_vote_post_remove()
        results["vote_post_validation"] = self.test_vote_post_validation_errors()
        
        # Delete post tests
        results["delete_post"] = self.test_delete_post()
        results["delete_post_access_denied"] = self.test_delete_post_access_denied()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("=" * 60)
        print("📊 Posts API Test Summary")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        print("Detailed Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        print()
        if passed == total:
            print("🎉 All posts tests passed!")
        else:
            print("⚠️  Some posts tests failed. Check the details above.")

def main():
    """Main function to run posts tests"""
    tester = PostsAPITester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Return exit code based on results
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())
