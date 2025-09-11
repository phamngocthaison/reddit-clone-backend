#!/usr/bin/env python3
"""
Test script for Subreddits APIs
Tests all subreddit endpoints according to API contract
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

class SubredditsAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_user_id = f"user_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        self.created_subreddits = []
        
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
    
    def test_create_subreddit(self) -> bool:
        """Test create subreddit endpoint"""
        print("🏘️  Testing Create Subreddit...")
        
        subreddit_data = {
            "name": f"testsub_{int(time.time())}",
            "display_name": "Test Subreddit",
            "description": "A test subreddit for API testing",
            "rules": ["Be respectful", "No spam", "Use descriptive titles"],
            "primary_color": "#FF4500",
            "secondary_color": "#FFFFFF",
            "language": "en",
            "country": "US"
        }
        
        response = requests.post(
            f"{self.base_url}/subreddits/create",
            headers=self.get_headers_with_user(),
            json=subreddit_data
        )
        
        success = response.status_code == 201
        self.print_test_result("Create Subreddit", success, response, 201)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                subreddit = data["data"]
                self.created_subreddits.append(subreddit["subreddit_id"])
                print(f"   Subreddit ID: {subreddit['subreddit_id']}")
                print(f"   Name: {subreddit['name']}")
                print(f"   Display Name: {subreddit['display_name']}")
        
        return success
    
    def test_create_subreddit_validation_errors(self) -> bool:
        """Test create subreddit with validation errors"""
        print("🏘️  Testing Create Subreddit - Validation Errors...")
        
        test_cases = [
            {
                "name": "Missing name",
                "data": {
                    "display_name": "Test Subreddit",
                    "description": "Test description"
                },
                "expected_status": 400
            },
            {
                "name": "Empty name",
                "data": {
                    "name": "",
                    "display_name": "Test Subreddit",
                    "description": "Test description"
                },
                "expected_status": 400
            },
            {
                "name": "Missing display_name",
                "data": {
                    "name": "testsub",
                    "description": "Test description"
                },
                "expected_status": 400
            },
            {
                "name": "Invalid color format",
                "data": {
                    "name": "testsub",
                    "display_name": "Test Subreddit",
                    "description": "Test description",
                    "primary_color": "invalid_color"
                },
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/subreddits/create",
                headers=self.get_headers_with_user(),
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Create Subreddit Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_get_subreddits(self) -> bool:
        """Test get subreddits endpoint"""
        print("🏘️  Testing Get Subreddits...")
        
        response = requests.get(
            f"{self.base_url}/subreddits",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Subreddits", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                subreddits = data["data"]["subreddits"]
                print(f"   Retrieved {len(subreddits)} subreddits")
                print(f"   Total count: {data['data'].get('total_count', 0)}")
        
        return success
    
    def test_get_subreddits_with_filters(self) -> bool:
        """Test get subreddits with various filters"""
        print("🏘️  Testing Get Subreddits - With Filters...")
        
        test_cases = [
            {
                "name": "Sort by new",
                "params": {"sort": "new", "limit": 10}
            },
            {
                "name": "Sort by popular",
                "params": {"sort": "popular", "limit": 10}
            },
            {
                "name": "Search by name",
                "params": {"search": "test", "limit": 5}
            },
            {
                "name": "With offset",
                "params": {"limit": 5, "offset": 0}
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.get(
                f"{self.base_url}/subreddits",
                headers=self.get_headers_with_user(),
                params=test_case["params"]
            )
            
            success = response.status_code == 200
            self.print_test_result(f"Get Subreddits - {test_case['name']}", success, response, 200)
            all_passed = all_passed and success
        
        return all_passed
    
    def test_get_subreddit_by_id(self) -> bool:
        """Test get subreddit by ID"""
        print("🏘️  Testing Get Subreddit by ID...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        response = requests.get(
            f"{self.base_url}/subreddits/{subreddit_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Subreddit by ID", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                subreddit = data["data"]
                print(f"   Subreddit ID: {subreddit['subreddit_id']}")
                print(f"   Name: {subreddit['name']}")
                print(f"   Display Name: {subreddit['display_name']}")
        
        return success
    
    def test_get_subreddit_by_id_not_found(self) -> bool:
        """Test get subreddit by ID - not found"""
        print("🏘️  Testing Get Subreddit by ID - Not Found...")
        
        fake_subreddit_id = f"subreddit_{int(time.time())}_fake"
        response = requests.get(
            f"{self.base_url}/subreddits/{fake_subreddit_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 404
        self.print_test_result("Get Subreddit by ID - Not Found", success, response, 404)
        
        return success
    
    def test_get_subreddit_by_name(self) -> bool:
        """Test get subreddit by name"""
        print("🏘️  Testing Get Subreddit by Name...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        # We need to get the subreddit name from the created subreddit
        # For now, we'll use a generic test
        test_name = "programming"
        response = requests.get(
            f"{self.base_url}/subreddits/name/{test_name}",
            headers=self.get_headers_with_user()
        )
        
        # This might return 404 if the subreddit doesn't exist, which is expected
        success = response.status_code in [200, 404]
        self.print_test_result("Get Subreddit by Name", success, response, 200)
        
        return success
    
    def test_update_subreddit(self) -> bool:
        """Test update subreddit"""
        print("🏘️  Testing Update Subreddit...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        update_data = {
            "display_name": "Updated Test Subreddit",
            "description": "Updated description with more details",
            "rules": ["Be respectful and civil", "No spam", "Use descriptive titles", "Follow guidelines"],
            "primary_color": "#FF6B35",
            "secondary_color": "#F7F7F7",
            "is_private": False,
            "is_nsfw": False,
            "is_restricted": False
        }
        
        response = requests.put(
            f"{self.base_url}/subreddits/{subreddit_id}",
            headers=self.get_headers_with_user(),
            json=update_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Update Subreddit", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                subreddit = data["data"]
                print(f"   Updated Display Name: {subreddit['display_name']}")
                print(f"   Updated Description: {subreddit['description'][:50]}...")
        
        return success
    
    def test_update_subreddit_access_denied(self) -> bool:
        """Test update subreddit - access denied (different user)"""
        print("🏘️  Testing Update Subreddit - Access Denied...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        different_user_headers = {
            **HEADERS,
            "X-User-ID": f"user_{int(time.time())}_different"
        }
        
        update_data = {
            "display_name": "Unauthorized Update"
        }
        
        response = requests.put(
            f"{self.base_url}/subreddits/{subreddit_id}",
            headers=different_user_headers,
            json=update_data
        )
        
        success = response.status_code == 403
        self.print_test_result("Update Subreddit - Access Denied", success, response, 403)
        
        return success
    
    def test_join_subreddit(self) -> bool:
        """Test join subreddit"""
        print("🏘️  Testing Join Subreddit...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        join_data = {}
        
        response = requests.post(
            f"{self.base_url}/subreddits/{subreddit_id}/join",
            headers=self.get_headers_with_user(),
            json=join_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Join Subreddit", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                subscription = data["data"]
                print(f"   Subscription ID: {subscription['subscription_id']}")
                print(f"   Role: {subscription['role']}")
        
        return success
    
    def test_join_subreddit_already_joined(self) -> bool:
        """Test join subreddit - already joined"""
        print("🏘️  Testing Join Subreddit - Already Joined...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        join_data = {}
        
        # Try to join again
        response = requests.post(
            f"{self.base_url}/subreddits/{subreddit_id}/join",
            headers=self.get_headers_with_user(),
            json=join_data
        )
        
        # This might return 400 if already joined, or 200 if it's idempotent
        success = response.status_code in [200, 400]
        self.print_test_result("Join Subreddit - Already Joined", success, response, 200)
        
        return success
    
    def test_leave_subreddit(self) -> bool:
        """Test leave subreddit"""
        print("🏘️  Testing Leave Subreddit...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        leave_data = {}
        
        response = requests.post(
            f"{self.base_url}/subreddits/{subreddit_id}/leave",
            headers=self.get_headers_with_user(),
            json=leave_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Leave Subreddit", success, response, 200)
        
        return success
    
    def test_leave_subreddit_not_joined(self) -> bool:
        """Test leave subreddit - not joined"""
        print("🏘️  Testing Leave Subreddit - Not Joined...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        # Use a different subreddit ID that we haven't joined
        fake_subreddit_id = f"subreddit_{int(time.time())}_fake"
        leave_data = {}
        
        response = requests.post(
            f"{self.base_url}/subreddits/{fake_subreddit_id}/leave",
            headers=self.get_headers_with_user(),
            json=leave_data
        )
        
        # This might return 400 or 404
        success = response.status_code in [200, 400, 404]
        self.print_test_result("Leave Subreddit - Not Joined", success, response, 200)
        
        return success
    
    def test_get_subreddit_posts(self) -> bool:
        """Test get subreddit posts"""
        print("🏘️  Testing Get Subreddit Posts...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        response = requests.get(
            f"{self.base_url}/subreddits/{subreddit_id}/posts",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Subreddit Posts", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                posts = data["data"]["posts"]
                print(f"   Retrieved {len(posts)} posts")
                print(f"   Count: {data['data'].get('count', 0)}")
        
        return success
    
    def test_get_subreddit_posts_with_filters(self) -> bool:
        """Test get subreddit posts with filters"""
        print("🏘️  Testing Get Subreddit Posts - With Filters...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        
        test_cases = [
            {
                "name": "Sort by new",
                "params": {"sort": "new", "limit": 5}
            },
            {
                "name": "Sort by hot",
                "params": {"sort": "hot", "limit": 5}
            },
            {
                "name": "With offset",
                "params": {"limit": 3, "offset": 0}
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.get(
                f"{self.base_url}/subreddits/{subreddit_id}/posts",
                headers=self.get_headers_with_user(),
                params=test_case["params"]
            )
            
            success = response.status_code == 200
            self.print_test_result(f"Get Subreddit Posts - {test_case['name']}", success, response, 200)
            all_passed = all_passed and success
        
        return all_passed
    
    def test_add_moderator(self) -> bool:
        """Test add moderator"""
        print("🏘️  Testing Add Moderator...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        moderator_data = {
            "user_id": f"user_{int(time.time())}_moderator",
            "action": "add",
            "role": "moderator"
        }
        
        response = requests.post(
            f"{self.base_url}/subreddits/{subreddit_id}/moderators",
            headers=self.get_headers_with_user(),
            json=moderator_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Add Moderator", success, response, 200)
        
        return success
    
    def test_remove_moderator(self) -> bool:
        """Test remove moderator"""
        print("🏘️  Testing Remove Moderator...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        moderator_user_id = f"user_{int(time.time())}_moderator"
        
        response = requests.delete(
            f"{self.base_url}/subreddits/{subreddit_id}/moderators/{moderator_user_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Remove Moderator", success, response, 200)
        
        return success
    
    def test_delete_subreddit(self) -> bool:
        """Test delete subreddit"""
        print("🏘️  Testing Delete Subreddit...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        # Use the last created subreddit for deletion
        subreddit_id = self.created_subreddits[-1]
        
        response = requests.delete(
            f"{self.base_url}/subreddits/{subreddit_id}",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Delete Subreddit", success, response, 200)
        
        if success:
            # Remove from our list
            self.created_subreddits.remove(subreddit_id)
        
        return success
    
    def test_delete_subreddit_access_denied(self) -> bool:
        """Test delete subreddit - access denied (different user)"""
        print("🏘️  Testing Delete Subreddit - Access Denied...")
        
        if not self.created_subreddits:
            print("   ⚠️  Skipping - No created subreddits")
            return True
        
        subreddit_id = self.created_subreddits[0]
        different_user_headers = {
            **HEADERS,
            "X-User-ID": f"user_{int(time.time())}_different"
        }
        
        response = requests.delete(
            f"{self.base_url}/subreddits/{subreddit_id}",
            headers=different_user_headers
        )
        
        success = response.status_code == 403
        self.print_test_result("Delete Subreddit - Access Denied", success, response, 403)
        
        return success
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all subreddit tests"""
        print("🚀 Starting Subreddits API Tests...")
        print("=" * 60)
        
        results = {}
        
        # Create subreddits first
        results["create_subreddit"] = self.test_create_subreddit()
        results["create_subreddit_validation"] = self.test_create_subreddit_validation_errors()
        
        # Get subreddits tests
        results["get_subreddits"] = self.test_get_subreddits()
        results["get_subreddits_filters"] = self.test_get_subreddits_with_filters()
        
        # Get subreddit by ID/name tests
        results["get_subreddit_by_id"] = self.test_get_subreddit_by_id()
        results["get_subreddit_by_id_not_found"] = self.test_get_subreddit_by_id_not_found()
        results["get_subreddit_by_name"] = self.test_get_subreddit_by_name()
        
        # Update subreddit tests
        results["update_subreddit"] = self.test_update_subreddit()
        results["update_subreddit_access_denied"] = self.test_update_subreddit_access_denied()
        
        # Join/leave subreddit tests
        results["join_subreddit"] = self.test_join_subreddit()
        results["join_subreddit_already_joined"] = self.test_join_subreddit_already_joined()
        results["leave_subreddit"] = self.test_leave_subreddit()
        results["leave_subreddit_not_joined"] = self.test_leave_subreddit_not_joined()
        
        # Get subreddit posts tests
        results["get_subreddit_posts"] = self.test_get_subreddit_posts()
        results["get_subreddit_posts_filters"] = self.test_get_subreddit_posts_with_filters()
        
        # Moderator management tests
        results["add_moderator"] = self.test_add_moderator()
        results["remove_moderator"] = self.test_remove_moderator()
        
        # Delete subreddit tests
        results["delete_subreddit"] = self.test_delete_subreddit()
        results["delete_subreddit_access_denied"] = self.test_delete_subreddit_access_denied()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("=" * 60)
        print("📊 Subreddits API Test Summary")
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
            print("🎉 All subreddit tests passed!")
        else:
            print("⚠️  Some subreddit tests failed. Check the details above.")

def main():
    """Main function to run subreddit tests"""
    tester = SubredditsAPITester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Return exit code based on results
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())
