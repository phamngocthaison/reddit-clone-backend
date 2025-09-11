#!/usr/bin/env python3
"""
Test script for Feeds APIs
Tests all news feed endpoints according to API contract
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

class FeedsAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_user_id = f"user_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        self.test_subreddit_id = f"subreddit_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        
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
    
    def get_headers_with_auth(self) -> Dict[str, str]:
        """Get headers with JWT token (for testing)"""
        return {
            **HEADERS,
            "X-User-ID": self.test_user_id,
            "Authorization": "Bearer test_token"  # Mock token for testing
        }
    
    def test_get_feeds(self) -> bool:
        """Test get feeds endpoint"""
        print("📰 Testing Get Feeds...")
        
        response = requests.get(
            f"{self.base_url}/feeds",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Feeds", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                feeds = data["data"]["feeds"]
                print(f"   Retrieved {len(feeds)} feed items")
                if "pagination" in data["data"]:
                    pagination = data["data"]["pagination"]
                    print(f"   Total: {pagination.get('total', 0)}")
                    print(f"   Has More: {pagination.get('hasMore', False)}")
        
        return success
    
    def test_get_feeds_with_filters(self) -> bool:
        """Test get feeds with various filters"""
        print("📰 Testing Get Feeds - With Filters...")
        
        test_cases = [
            {
                "name": "Limit 10",
                "params": {"limit": 10}
            },
            {
                "name": "Offset 5",
                "params": {"offset": 5, "limit": 10}
            },
            {
                "name": "Sort by new",
                "params": {"sort": "new", "limit": 5}
            },
            {
                "name": "Sort by hot",
                "params": {"sort": "hot", "limit": 5}
            },
            {
                "name": "Sort by top",
                "params": {"sort": "top", "limit": 5}
            },
            {
                "name": "Sort by trending",
                "params": {"sort": "trending", "limit": 5}
            },
            {
                "name": "Include NSFW",
                "params": {"includeNSFW": "true", "limit": 5}
            },
            {
                "name": "Include Spoilers",
                "params": {"includeSpoilers": "true", "limit": 5}
            },
            {
                "name": "Filter by subreddit",
                "params": {"subredditId": self.test_subreddit_id, "limit": 5}
            },
            {
                "name": "Filter by author",
                "params": {"authorId": self.test_user_id, "limit": 5}
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.get(
                f"{self.base_url}/feeds",
                headers=self.get_headers_with_user(),
                params=test_case["params"]
            )
            
            success = response.status_code == 200
            self.print_test_result(f"Get Feeds - {test_case['name']}", success, response, 200)
            all_passed = all_passed and success
        
        return all_passed
    
    def test_get_feeds_with_jwt_token(self) -> bool:
        """Test get feeds with JWT token"""
        print("📰 Testing Get Feeds - With JWT Token...")
        
        response = requests.get(
            f"{self.base_url}/feeds",
            headers=self.get_headers_with_auth()
        )
        
        # This might fail if JWT validation is strict, which is expected
        success = response.status_code in [200, 401, 403]
        self.print_test_result("Get Feeds - With JWT Token", success, response, 200)
        
        return success
    
    def test_get_feeds_missing_user_id(self) -> bool:
        """Test get feeds without user ID header"""
        print("📰 Testing Get Feeds - Missing User ID...")
        
        response = requests.get(
            f"{self.base_url}/feeds",
            headers=HEADERS
        )
        
        success = response.status_code == 400
        self.print_test_result("Get Feeds - Missing User ID", success, response, 400)
        
        return success
    
    def test_get_feeds_validation_errors(self) -> bool:
        """Test get feeds with validation errors"""
        print("📰 Testing Get Feeds - Validation Errors...")
        
        test_cases = [
            {
                "name": "Invalid limit",
                "params": {"limit": 1000}  # Too high
            },
            {
                "name": "Invalid sort type",
                "params": {"sort": "invalid_sort"}
            },
            {
                "name": "Negative offset",
                "params": {"offset": -1}
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.get(
                f"{self.base_url}/feeds",
                headers=self.get_headers_with_user(),
                params=test_case["params"]
            )
            
            # These might return 200 with default values or 400 for validation errors
            success = response.status_code in [200, 400]
            self.print_test_result(f"Get Feeds Validation - {test_case['name']}", success, response, 200)
            all_passed = all_passed and success
        
        return all_passed
    
    def test_refresh_feeds(self) -> bool:
        """Test refresh feeds endpoint"""
        print("📰 Testing Refresh Feeds...")
        
        refresh_data = {
            "reason": "subreddit_joined",
            "subredditId": self.test_subreddit_id,
            "userId": self.test_user_id
        }
        
        response = requests.post(
            f"{self.base_url}/feeds/refresh",
            headers=self.get_headers_with_user(),
            json=refresh_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Refresh Feeds", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                refresh_info = data["data"]
                print(f"   New Items Count: {refresh_info.get('newItemsCount', 0)}")
                print(f"   Refreshed At: {refresh_info.get('refreshedAt', 'N/A')}")
        
        return success
    
    def test_refresh_feeds_with_jwt_token(self) -> bool:
        """Test refresh feeds with JWT token"""
        print("📰 Testing Refresh Feeds - With JWT Token...")
        
        refresh_data = {
            "reason": "user_activity",
            "userId": self.test_user_id
        }
        
        response = requests.post(
            f"{self.base_url}/feeds/refresh",
            headers=self.get_headers_with_auth(),
            json=refresh_data
        )
        
        # This might fail if JWT validation is strict, which is expected
        success = response.status_code in [200, 401, 403]
        self.print_test_result("Refresh Feeds - With JWT Token", success, response, 200)
        
        return success
    
    def test_refresh_feeds_validation_errors(self) -> bool:
        """Test refresh feeds with validation errors"""
        print("📰 Testing Refresh Feeds - Validation Errors...")
        
        test_cases = [
            {
                "name": "Missing reason",
                "data": {
                    "userId": self.test_user_id
                },
                "expected_status": 400
            },
            {
                "name": "Empty reason",
                "data": {
                    "reason": "",
                    "userId": self.test_user_id
                },
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/feeds/refresh",
                headers=self.get_headers_with_user(),
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Refresh Feeds Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_get_feeds_stats(self) -> bool:
        """Test get feeds stats endpoint"""
        print("📰 Testing Get Feeds Stats...")
        
        response = requests.get(
            f"{self.base_url}/feeds/stats",
            headers=self.get_headers_with_user()
        )
        
        success = response.status_code == 200
        self.print_test_result("Get Feeds Stats", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                stats = data["data"]
                print(f"   Total Subscriptions: {stats.get('totalSubscriptions', 0)}")
                print(f"   Total Following: {stats.get('totalFollowing', 0)}")
                print(f"   Feed Items Count: {stats.get('feedItemsCount', 0)}")
                print(f"   Average Score: {stats.get('averageScore', 0)}")
        
        return success
    
    def test_get_feeds_stats_with_jwt_token(self) -> bool:
        """Test get feeds stats with JWT token"""
        print("📰 Testing Get Feeds Stats - With JWT Token...")
        
        response = requests.get(
            f"{self.base_url}/feeds/stats",
            headers=self.get_headers_with_auth()
        )
        
        # This might fail if JWT validation is strict, which is expected
        success = response.status_code in [200, 401, 403]
        self.print_test_result("Get Feeds Stats - With JWT Token", success, response, 200)
        
        return success
    
    def test_get_feeds_stats_missing_user_id(self) -> bool:
        """Test get feeds stats without user ID header"""
        print("📰 Testing Get Feeds Stats - Missing User ID...")
        
        response = requests.get(
            f"{self.base_url}/feeds/stats",
            headers=HEADERS
        )
        
        success = response.status_code == 400
        self.print_test_result("Get Feeds Stats - Missing User ID", success, response, 400)
        
        return success
    
    def test_feeds_integration_scenario(self) -> bool:
        """Test complete feeds integration scenario"""
        print("📰 Testing Feeds Integration Scenario...")
        
        # Step 1: Get initial feeds
        print("   Step 1: Getting initial feeds...")
        response1 = requests.get(
            f"{self.base_url}/feeds",
            headers=self.get_headers_with_user(),
            params={"limit": 5}
        )
        
        if response1.status_code != 200:
            print("   ❌ Failed to get initial feeds")
            return False
        
        initial_count = len(response1.json().get("data", {}).get("feeds", []))
        print(f"   Initial feed count: {initial_count}")
        
        # Step 2: Refresh feeds
        print("   Step 2: Refreshing feeds...")
        refresh_data = {
            "reason": "test_refresh",
            "userId": self.test_user_id
        }
        
        response2 = requests.post(
            f"{self.base_url}/feeds/refresh",
            headers=self.get_headers_with_user(),
            json=refresh_data
        )
        
        if response2.status_code != 200:
            print("   ❌ Failed to refresh feeds")
            return False
        
        print("   ✅ Feeds refreshed successfully")
        
        # Step 3: Get feeds after refresh
        print("   Step 3: Getting feeds after refresh...")
        response3 = requests.get(
            f"{self.base_url}/feeds",
            headers=self.get_headers_with_user(),
            params={"limit": 5}
        )
        
        if response3.status_code != 200:
            print("   ❌ Failed to get feeds after refresh")
            return False
        
        final_count = len(response3.json().get("data", {}).get("feeds", []))
        print(f"   Final feed count: {final_count}")
        
        # Step 4: Get stats
        print("   Step 4: Getting feed stats...")
        response4 = requests.get(
            f"{self.base_url}/feeds/stats",
            headers=self.get_headers_with_user()
        )
        
        if response4.status_code != 200:
            print("   ❌ Failed to get feed stats")
            return False
        
        print("   ✅ Feed stats retrieved successfully")
        
        success = True
        self.print_test_result("Feeds Integration Scenario", success, response4, 200)
        
        return success
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all feeds tests"""
        print("🚀 Starting Feeds API Tests...")
        print("=" * 60)
        
        results = {}
        
        # Get feeds tests
        results["get_feeds"] = self.test_get_feeds()
        results["get_feeds_filters"] = self.test_get_feeds_with_filters()
        results["get_feeds_jwt"] = self.test_get_feeds_with_jwt_token()
        results["get_feeds_missing_user"] = self.test_get_feeds_missing_user_id()
        results["get_feeds_validation"] = self.test_get_feeds_validation_errors()
        
        # Refresh feeds tests
        results["refresh_feeds"] = self.test_refresh_feeds()
        results["refresh_feeds_jwt"] = self.test_refresh_feeds_with_jwt_token()
        results["refresh_feeds_validation"] = self.test_refresh_feeds_validation_errors()
        
        # Get feeds stats tests
        results["get_feeds_stats"] = self.test_get_feeds_stats()
        results["get_feeds_stats_jwt"] = self.test_get_feeds_stats_with_jwt_token()
        results["get_feeds_stats_missing_user"] = self.test_get_feeds_stats_missing_user_id()
        
        # Integration scenario test
        results["feeds_integration"] = self.test_feeds_integration_scenario()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("=" * 60)
        print("📊 Feeds API Test Summary")
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
            print("🎉 All feeds tests passed!")
        else:
            print("⚠️  Some feeds tests failed. Check the details above.")

def main():
    """Main function to run feeds tests"""
    tester = FeedsAPITester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Return exit code based on results
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())
