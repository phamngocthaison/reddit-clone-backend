#!/usr/bin/env python3
"""
Test script for Comments APIs
Tests all comments endpoints according to API contract
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

class CommentsAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_user_id = f"user_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        self.test_post_id = f"post_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        self.created_comments = []
        
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
    
    def test_create_comment(self) -> bool:
        """Test create comment endpoint"""
        print("💬 Testing Create Comment...")
        
        comment_data = {
            "post_id": self.test_post_id,
            "content": "This is a great post! Thanks for sharing.",
            "parent_id": None,
            "comment_type": "comment",
            "is_nsfw": False,
            "is_spoiler": False,
            "flair": "Discussion",
            "tags": ["feedback", "positive"]
        }
        
        response = requests.post(
            f"{self.base_url}/comments/create",
            headers=self.get_headers_with_user(),
            json=comment_data
        )
        
        success = response.status_code == 201
        self.print_test_result("Create Comment", success, response, 201)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                comment = data["data"]["comment"]
                self.created_comments.append(comment["comment_id"])
                print(f"   Comment ID: {comment['comment_id']}")
                print(f"   Content: {comment['content'][:50]}...")
                print(f"   Post ID: {comment['post_id']}")
        
        return success
    
    def test_create_comment_validation_errors(self) -> bool:
        """Test create comment with validation errors"""
        print("💬 Testing Create Comment - Validation Errors...")
        
        test_cases = [
            {
                "name": "Empty content",
                "data": {
                    "post_id": self.test_post_id,
                    "content": "",
                    "comment_type": "comment"
                },
                "expected_status": 400
            },
            {
                "name": "Missing content",
                "data": {
                    "post_id": self.test_post_id,
                    "comment_type": "comment"
                },
                "expected_status": 400
            },
            {
                "name": "Missing post_id",
                "data": {
                    "content": "Test comment",
                    "comment_type": "comment"
                },
                "expected_status": 400
            },
            {
                "name": "Invalid comment type",
                "data": {
                    "post_id": self.test_post_id,
                    "content": "Test comment",
                    "comment_type": "invalid_type"
                },
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/comments/create",
                headers=self.get_headers_with_user(),
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Create Comment Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_create_reply_comment(self) -> bool:
        """Test create reply comment"""
        print("💬 Testing Create Reply Comment...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No parent comment")
            return True
        
        parent_comment_id = self.created_comments[0]
        reply_data = {
            "post_id": self.test_post_id,
            "content": "I agree with your point!",
            "parent_id": parent_comment_id,
            "comment_type": "comment",
            "is_nsfw": False,
            "is_spoiler": False,
            "flair": "Agreement",
            "tags": ["reply", "agreement"]
        }
        
        response = requests.post(
            f"{self.base_url}/comments/create",
            headers=self.get_headers_with_user(),
            json=reply_data
        )
        
        success = response.status_code == 201
        self.print_test_result("Create Reply Comment", success, response, 201)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                comment = data["data"]["comment"]
                self.created_comments.append(comment["comment_id"])
                print(f"   Reply ID: {comment['comment_id']}")
                print(f"   Parent ID: {comment['parent_id']}")
        
        return success
    
    def test_get_comments(self) -> bool:
        """Test get comments endpoint"""
        print("💬 Testing Get Comments...")
        
        response = requests.get(
            f"{self.base_url}/comments",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Comments", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                comments = data["data"]["comments"]
                print(f"   Retrieved {len(comments)} comments")
                print(f"   Total count: {data['data'].get('total_count', 0)}")
        
        return success
    
    def test_get_comments_with_filters(self) -> bool:
        """Test get comments with various filters"""
        print("💬 Testing Get Comments - With Filters...")
        
        test_cases = [
            {
                "name": "Filter by post_id",
                "params": {"post_id": self.test_post_id, "limit": 10}
            },
            {
                "name": "Filter by author",
                "params": {"author_id": self.test_user_id, "limit": 10}
            },
            {
                "name": "Sort by created_at desc",
                "params": {"sort_by": "created_at", "sort_order": "desc", "limit": 5}
            },
            {
                "name": "Sort by score asc",
                "params": {"sort_by": "score", "sort_order": "asc", "limit": 5}
            },
            {
                "name": "With offset",
                "params": {"limit": 5, "offset": 0}
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.get(
                f"{self.base_url}/comments",
                headers=self.get_headers_with_user(),
                params=test_case["params"]
            )
            
            success = response.status_code == 200
            self.print_test_result(f"Get Comments - {test_case['name']}", success, response, 200)
            all_passed = all_passed and success
        
        return all_passed
    
    def test_get_comments_by_post_id(self) -> bool:
        """Test get comments by post ID"""
        print("💬 Testing Get Comments by Post ID...")
        
        response = requests.get(
            f"{self.base_url}/posts/{self.test_post_id}/comments",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Comments by Post ID", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                comments = data["data"]["comments"]
                print(f"   Retrieved {len(comments)} comments for post {self.test_post_id}")
                print(f"   Count: {data['data'].get('count', 0)}")
        
        return success
    
    def test_get_comments_by_post_id_with_filters(self) -> bool:
        """Test get comments by post ID with filters"""
        print("💬 Testing Get Comments by Post ID - With Filters...")
        
        test_cases = [
            {
                "name": "Sort by created_at",
                "params": {"sort_by": "created_at", "sort_order": "desc", "limit": 5}
            },
            {
                "name": "Sort by score",
                "params": {"sort_by": "score", "sort_order": "asc", "limit": 5}
            },
            {
                "name": "With offset",
                "params": {"limit": 3, "offset": 0}
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.get(
                f"{self.base_url}/posts/{self.test_post_id}/comments",
                headers=self.get_headers_with_user(),
                params=test_case["params"]
            )
            
            success = response.status_code == 200
            self.print_test_result(f"Get Comments by Post ID - {test_case['name']}", success, response, 200)
            all_passed = all_passed and success
        
        return all_passed
    
    def test_get_comment_by_id(self) -> bool:
        """Test get comment by ID"""
        print("💬 Testing Get Comment by ID...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        response = requests.get(
            f"{self.base_url}/comments/{comment_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Comment by ID", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                comment = data["data"]["comment"]
                print(f"   Comment ID: {comment['comment_id']}")
                print(f"   Content: {comment['content'][:50]}...")
        
        return success
    
    def test_get_comment_by_id_not_found(self) -> bool:
        """Test get comment by ID - not found"""
        print("💬 Testing Get Comment by ID - Not Found...")
        
        fake_comment_id = f"comment_{int(time.time())}_fake"
        response = requests.get(
            f"{self.base_url}/comments/{fake_comment_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 404
        self.print_test_result("Get Comment by ID - Not Found", success, response, 404)
        
        return success
    
    def test_update_comment(self) -> bool:
        """Test update comment"""
        print("💬 Testing Update Comment...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        update_data = {
            "content": "Updated comment content with more details",
            "is_nsfw": False,
            "is_spoiler": True,
            "flair": "Updated Flair",
            "tags": ["updated", "feedback"]
        }
        
        response = requests.put(
            f"{self.base_url}/comments/{comment_id}",
            headers=self.get_headers_with_user(),
            json=update_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Update Comment", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                comment = data["data"]["comment"]
                print(f"   Updated Content: {comment['content'][:50]}...")
                print(f"   Updated Flair: {comment['flair']}")
        
        return success
    
    def test_update_comment_access_denied(self) -> bool:
        """Test update comment - access denied (different user)"""
        print("💬 Testing Update Comment - Access Denied...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        different_user_headers = {
            **HEADERS,
            "X-User-ID": f"user_{int(time.time())}_different"
        }
        
        update_data = {
            "content": "Unauthorized update"
        }
        
        response = requests.put(
            f"{self.base_url}/comments/{comment_id}",
            headers=different_user_headers,
            json=update_data
        )
        
        success = response.status_code == 403
        self.print_test_result("Update Comment - Access Denied", success, response, 403)
        
        return success
    
    def test_vote_comment(self) -> bool:
        """Test vote comment"""
        print("💬 Testing Vote Comment...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        vote_data = {
            "vote_type": "upvote"
        }
        
        response = requests.post(
            f"{self.base_url}/comments/{comment_id}/vote",
            headers=self.get_headers_with_user(),
            json=vote_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Vote Comment - Upvote", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                stats = data["data"]["stats"]
                print(f"   Score: {stats['score']}")
                print(f"   Upvotes: {stats['upvotes']}")
        
        return success
    
    def test_vote_comment_downvote(self) -> bool:
        """Test vote comment - downvote"""
        print("💬 Testing Vote Comment - Downvote...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        vote_data = {
            "vote_type": "downvote"
        }
        
        response = requests.post(
            f"{self.base_url}/comments/{comment_id}/vote",
            headers=self.get_headers_with_user(),
            json=vote_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Vote Comment - Downvote", success, response, 200)
        
        return success
    
    def test_vote_comment_remove(self) -> bool:
        """Test vote comment - remove vote"""
        print("💬 Testing Vote Comment - Remove Vote...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        vote_data = {
            "vote_type": "remove"
        }
        
        response = requests.post(
            f"{self.base_url}/comments/{comment_id}/vote",
            headers=self.get_headers_with_user(),
            json=vote_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Vote Comment - Remove Vote", success, response, 200)
        
        return success
    
    def test_vote_comment_validation_errors(self) -> bool:
        """Test vote comment with validation errors"""
        print("💬 Testing Vote Comment - Validation Errors...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        
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
                f"{self.base_url}/comments/{comment_id}/vote",
                headers=self.get_headers_with_user(),
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Vote Comment Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_delete_comment(self) -> bool:
        """Test delete comment"""
        print("💬 Testing Delete Comment...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        # Use the last created comment for deletion
        comment_id = self.created_comments[-1]
        
        response = requests.delete(
            f"{self.base_url}/comments/{comment_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Delete Comment", success, response, 200)
        
        if success:
            # Remove from our list
            self.created_comments.remove(comment_id)
        
        return success
    
    def test_delete_comment_access_denied(self) -> bool:
        """Test delete comment - access denied (different user)"""
        print("💬 Testing Delete Comment - Access Denied...")
        
        if not self.created_comments:
            print("   ⚠️  Skipping - No created comments")
            return True
        
        comment_id = self.created_comments[0]
        different_user_headers = {
            **HEADERS,
            "X-User-ID": f"user_{int(time.time())}_different"
        }
        
        response = requests.delete(
            f"{self.base_url}/comments/{comment_id}",
            headers=different_user_headers
        )
        
        success = response.status_code == 403
        self.print_test_result("Delete Comment - Access Denied", success, response, 403)
        
        return success
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all comments tests"""
        print("🚀 Starting Comments API Tests...")
        print("=" * 60)
        
        results = {}
        
        # Create comments first
        results["create_comment"] = self.test_create_comment()
        results["create_reply_comment"] = self.test_create_reply_comment()
        results["create_comment_validation"] = self.test_create_comment_validation_errors()
        
        # Get comments tests
        results["get_comments"] = self.test_get_comments()
        results["get_comments_filters"] = self.test_get_comments_with_filters()
        results["get_comments_by_post_id"] = self.test_get_comments_by_post_id()
        results["get_comments_by_post_id_filters"] = self.test_get_comments_by_post_id_with_filters()
        
        # Get comment by ID tests
        results["get_comment_by_id"] = self.test_get_comment_by_id()
        results["get_comment_by_id_not_found"] = self.test_get_comment_by_id_not_found()
        
        # Update comment tests
        results["update_comment"] = self.test_update_comment()
        results["update_comment_access_denied"] = self.test_update_comment_access_denied()
        
        # Vote comment tests
        results["vote_comment_upvote"] = self.test_vote_comment()
        results["vote_comment_downvote"] = self.test_vote_comment_downvote()
        results["vote_comment_remove"] = self.test_vote_comment_remove()
        results["vote_comment_validation"] = self.test_vote_comment_validation_errors()
        
        # Delete comment tests
        results["delete_comment"] = self.test_delete_comment()
        results["delete_comment_access_denied"] = self.test_delete_comment_access_denied()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("=" * 60)
        print("📊 Comments API Test Summary")
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
            print("🎉 All comments tests passed!")
        else:
            print("⚠️  Some comments tests failed. Check the details above.")

def main():
    """Main function to run comments tests"""
    tester = CommentsAPITester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Return exit code based on results
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())
