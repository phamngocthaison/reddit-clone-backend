#!/usr/bin/env python3
"""Test script for User Profile APIs."""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


class UserProfileAPITester:
    """Test class for User Profile APIs."""
    
    def __init__(self, base_url: str = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"):
        """Initialize the tester."""
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user_id = "user_1757432106_d66ab80f40704b1"
        self.test_jwt_token = "eyJraWQiOiJwTDliQlM4K2dKVU5OXC9aK3VObGVmcm9VWkdDNFJhNmV5alwvcnN6T3IydW89IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJmOWJhMTU4Yy1iMDUxLTcwM2UtZGEzZS01ZDNlZDg1MjJiYjUiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTEuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTFfdGN3SUpTVUZTIiwiY2xpZW50X2lkIjoiMWV0Nm81cWR2ZmdjcmoxOHFxYmdsa3BrbTEiLCJvcmlnaW5fanRpIjoiMzcxMTczYTYtZmMxZC00Mjk1LWFiMmUtY2ExZmE2YTJlMWQyIiwiZXZlbnRfaWQiOiJkMzk5Mzc5ZS0xMmY2LTQxMWEtOTEzZS1lYzU3OWVjYTRlNjAiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzU3NTc4MjUwLCJleHAiOjE3NTc1ODE4NTAsImlhdCI6MTc1NzU3ODI1MCwianRpIjoiOGNhOWNkZDUtMWQxNS00NDMyLTk3OTktMWY4Yzk3NDBhNjQ3IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEyMyJ9.xNwl8KsN6xpmvTPPEpySKigkGfM0lKaLSZLICBqGZfGukibIuE8kKZCkL0IFGGP9ATRneT2VKE3sbSzTJQ8fzTIs0yuA1EuKUHCLEw5gwWfI2DKyFXdz57QrNRVAJAake3WjVrEmlKsWT1Ge7KYIE-zBU8CEooe7ppQ4jCmEpA735U4KriqoUpYokUcWFfEx5DQoW08uAobk1-YYUwLOWlZwkGJhyhwtIMYdJvEZCNmD8vK790yHX5i1to01D_NFtheXxpUzIgGykpl5oMeQXAoo7INkYl4YroPBqNYvk0Gmm2HdUnmHsSjpewrOJgcKkhS3nyH6H_ytVN40oAUArg"
        self.results = []
    
    def log_test(self, test_name: str, success: bool, message: str, response_data: Optional[Dict[str, Any]] = None):
        """Log test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
    
    def test_get_my_profile_success(self) -> bool:
        """Test GET /auth/me - Success case."""
        try:
            headers = {
                "Authorization": f"Bearer {self.test_jwt_token}",
                "X-User-ID": self.test_user_id
            }
            
            response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "user" in data.get("data", {}):
                    self.log_test("GET /auth/me - Success", True, "User profile retrieved successfully", data)
                    return True
                else:
                    self.log_test("GET /auth/me - Success", False, f"Invalid response format: {data}", data)
                    return False
            else:
                self.log_test("GET /auth/me - Success", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /auth/me - Success", False, f"Exception: {str(e)}")
            return False
    
    def test_get_my_profile_unauthorized(self) -> bool:
        """Test GET /auth/me - Unauthorized case."""
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            
            if response.status_code == 401:
                data = response.json()
                if not data.get("success") and data.get("error", {}).get("code") == "UNAUTHORIZED":
                    self.log_test("GET /auth/me - Unauthorized", True, "Correctly returned 401 Unauthorized", data)
                    return True
                else:
                    self.log_test("GET /auth/me - Unauthorized", False, f"Invalid error format: {data}", data)
                    return False
            else:
                self.log_test("GET /auth/me - Unauthorized", False, f"Expected 401, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /auth/me - Unauthorized", False, f"Exception: {str(e)}")
            return False
    
    def test_update_my_profile_success(self) -> bool:
        """Test PUT /auth/me - Success case."""
        try:
            headers = {
                "Authorization": f"Bearer {self.test_jwt_token}",
                "X-User-ID": self.test_user_id,
                "Content-Type": "application/json"
            }
            
            data = {
                "displayName": "Test User Updated",
                "bio": "This is a test bio for user profile",
                "avatar": "https://example.com/test-avatar.jpg",
                "isPublic": True,
                "showEmail": False
            }
            
            response = self.session.put(f"{self.base_url}/auth/me", headers=headers, json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success") and "user" in response_data.get("data", {}):
                    self.log_test("PUT /auth/me - Success", True, "User profile updated successfully", response_data)
                    return True
                else:
                    self.log_test("PUT /auth/me - Success", False, f"Invalid response format: {response_data}", response_data)
                    return False
            else:
                self.log_test("PUT /auth/me - Success", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /auth/me - Success", False, f"Exception: {str(e)}")
            return False
    
    def test_update_my_profile_validation_error(self) -> bool:
        """Test PUT /auth/me - Validation error case."""
        try:
            headers = {
                "Authorization": f"Bearer {self.test_jwt_token}",
                "X-User-ID": self.test_user_id,
                "Content-Type": "application/json"
            }
            
            data = {
                "displayName": "",  # Empty display name should fail validation
                "bio": "x" * 501,  # Bio too long
                "avatar": "invalid-url"  # Invalid URL
            }
            
            response = self.session.put(f"{self.base_url}/auth/me", headers=headers, json=data)
            
            if response.status_code == 400:
                response_data = response.json()
                if not response_data.get("success") and response_data.get("error", {}).get("code") == "VALIDATION_ERROR":
                    self.log_test("PUT /auth/me - Validation Error", True, "Correctly returned 400 Validation Error", response_data)
                    return True
                else:
                    self.log_test("PUT /auth/me - Validation Error", False, f"Invalid error format: {response_data}", response_data)
                    return False
            else:
                self.log_test("PUT /auth/me - Validation Error", False, f"Expected 400, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /auth/me - Validation Error", False, f"Exception: {str(e)}")
            return False
    
    def test_get_public_user_profile_success(self) -> bool:
        """Test GET /users/{user_id} - Success case."""
        try:
            response = self.session.get(f"{self.base_url}/users/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "user" in data.get("data", {}):
                    self.log_test("GET /users/{user_id} - Success", True, "Public user profile retrieved successfully", data)
                    return True
                else:
                    self.log_test("GET /users/{user_id} - Success", False, f"Invalid response format: {data}", data)
                    return False
            else:
                self.log_test("GET /users/{user_id} - Success", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /users/{user_id} - Success", False, f"Exception: {str(e)}")
            return False
    
    def test_get_public_user_profile_not_found(self) -> bool:
        """Test GET /users/{user_id} - User not found case."""
        try:
            fake_user_id = "user_nonexistent_12345"
            response = self.session.get(f"{self.base_url}/users/{fake_user_id}")
            
            if response.status_code == 404:
                data = response.json()
                if not data.get("success") and data.get("error", {}).get("code") == "USER_NOT_FOUND":
                    self.log_test("GET /users/{user_id} - Not Found", True, "Correctly returned 404 User Not Found", data)
                    return True
                else:
                    self.log_test("GET /users/{user_id} - Not Found", False, f"Invalid error format: {data}", data)
                    return False
            else:
                self.log_test("GET /users/{user_id} - Not Found", False, f"Expected 404, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /users/{user_id} - Not Found", False, f"Exception: {str(e)}")
            return False
    
    def test_change_password_success(self) -> bool:
        """Test PUT /auth/change-password - Success case."""
        try:
            headers = {
                "Authorization": f"Bearer {self.test_jwt_token}",
                "X-User-ID": self.test_user_id,
                "Content-Type": "application/json"
            }
            
            data = {
                "currentPassword": "TestPassword123",
                "newPassword": "NewTestPassword123"
            }
            
            response = self.session.put(f"{self.base_url}/auth/change-password", headers=headers, json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    self.log_test("PUT /auth/change-password - Success", True, "Password changed successfully", response_data)
                    return True
                else:
                    self.log_test("PUT /auth/change-password - Success", False, f"Invalid response format: {response_data}", response_data)
                    return False
            else:
                self.log_test("PUT /auth/change-password - Success", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /auth/change-password - Success", False, f"Exception: {str(e)}")
            return False
    
    def test_change_password_validation_error(self) -> bool:
        """Test PUT /auth/change-password - Validation error case."""
        try:
            headers = {
                "Authorization": f"Bearer {self.test_jwt_token}",
                "X-User-ID": self.test_user_id,
                "Content-Type": "application/json"
            }
            
            data = {
                "currentPassword": "TestPassword123",
                "newPassword": "weak"  # Weak password should fail validation
            }
            
            response = self.session.put(f"{self.base_url}/auth/change-password", headers=headers, json=data)
            
            if response.status_code == 400:
                response_data = response.json()
                if not response_data.get("success") and response_data.get("error", {}).get("code") == "VALIDATION_ERROR":
                    self.log_test("PUT /auth/change-password - Validation Error", True, "Correctly returned 400 Validation Error", response_data)
                    return True
                else:
                    self.log_test("PUT /auth/change-password - Validation Error", False, f"Invalid error format: {response_data}", response_data)
                    return False
            else:
                self.log_test("PUT /auth/change-password - Validation Error", False, f"Expected 400, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /auth/change-password - Validation Error", False, f"Exception: {str(e)}")
            return False
    
    def test_get_user_posts_success(self) -> bool:
        """Test GET /users/{user_id}/posts - Success case."""
        try:
            response = self.session.get(f"{self.base_url}/users/{self.test_user_id}/posts?limit=10&offset=0&sort=new")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "posts" in data.get("data", {}):
                    self.log_test("GET /users/{user_id}/posts - Success", True, "User posts retrieved successfully", data)
                    return True
                else:
                    self.log_test("GET /users/{user_id}/posts - Success", False, f"Invalid response format: {data}", data)
                    return False
            else:
                self.log_test("GET /users/{user_id}/posts - Success", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /users/{user_id}/posts - Success", False, f"Exception: {str(e)}")
            return False
    
    def test_get_user_comments_success(self) -> bool:
        """Test GET /users/{user_id}/comments - Success case."""
        try:
            response = self.session.get(f"{self.base_url}/users/{self.test_user_id}/comments?limit=10&offset=0&sort=new")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "comments" in data.get("data", {}):
                    self.log_test("GET /users/{user_id}/comments - Success", True, "User comments retrieved successfully", data)
                    return True
                else:
                    self.log_test("GET /users/{user_id}/comments - Success", False, f"Invalid response format: {data}", data)
                    return False
            else:
                self.log_test("GET /users/{user_id}/comments - Success", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /users/{user_id}/comments - Success", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_account_validation_error(self) -> bool:
        """Test DELETE /auth/me - Validation error case (missing password)."""
        try:
            headers = {
                "Authorization": f"Bearer {self.test_jwt_token}",
                "X-User-ID": self.test_user_id,
                "Content-Type": "application/json"
            }
            
            data = {}  # Missing password should fail validation
            
            response = self.session.delete(f"{self.base_url}/auth/me", headers=headers, json=data)
            
            if response.status_code == 400:
                response_data = response.json()
                if not response_data.get("success") and response_data.get("error", {}).get("code") == "VALIDATION_ERROR":
                    self.log_test("DELETE /auth/me - Validation Error", True, "Correctly returned 400 Validation Error", response_data)
                    return True
                else:
                    self.log_test("DELETE /auth/me - Validation Error", False, f"Invalid error format: {response_data}", response_data)
                    return False
            else:
                self.log_test("DELETE /auth/me - Validation Error", False, f"Expected 400, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("DELETE /auth/me - Validation Error", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all user profile API tests."""
        print("🧪 Running User Profile API Tests...")
        print("=" * 50)
        
        tests = [
            self.test_get_my_profile_success,
            self.test_get_my_profile_unauthorized,
            self.test_update_my_profile_success,
            self.test_update_my_profile_validation_error,
            self.test_get_public_user_profile_success,
            self.test_get_public_user_profile_not_found,
            self.test_change_password_success,
            self.test_change_password_validation_error,
            self.test_get_user_posts_success,
            self.test_get_user_comments_success,
            self.test_delete_account_validation_error
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__}: Exception - {str(e)}")
                self.results.append({
                    "test_name": test.__name__,
                    "success": False,
                    "message": f"Exception: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        success_rate = (passed / total) * 100
        
        print("=" * 50)
        print(f"📊 User Profile API Test Results: {passed}/{total} passed ({success_rate:.1f}%)")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": success_rate,
            "results": self.results
        }


def main():
    """Main function to run user profile API tests."""
    tester = UserProfileAPITester()
    results = tester.run_all_tests()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_user_profile_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📁 Results saved to: {filename}")
    
    return results


if __name__ == "__main__":
    main()
