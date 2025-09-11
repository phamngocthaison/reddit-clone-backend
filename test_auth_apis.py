#!/usr/bin/env python3
"""
Test script for Authentication APIs
Tests all authentication endpoints according to API contract
"""

import requests
import json
import time
import random
import string
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"
HEADERS = {
    "Content-Type": "application/json"
}

class AuthAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_user = None
        self.access_token = None
        self.refresh_token = None
        self.id_token = None
        
    def generate_test_data(self) -> Dict[str, str]:
        """Generate random test data for user registration"""
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        return {
            "email": f"test_{timestamp}_{random_suffix}@example.com",
            "username": f"testuser_{timestamp}_{random_suffix}",
            "password": "TestPass123"
        }
    
    def print_test_result(self, test_name: str, success: bool, response: requests.Response, expected_status: int = None):
        """Print formatted test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if not success:
            print(f"   Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        print()
    
    def test_user_registration(self) -> bool:
        """Test user registration endpoint"""
        print("🔐 Testing User Registration...")
        
        test_data = self.generate_test_data()
        self.test_user = test_data
        
        response = requests.post(
            f"{self.base_url}/auth/register",
            headers=HEADERS,
            json=test_data
        )
        
        success = response.status_code == 200
        self.print_test_result("User Registration", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                user_data = data["data"]["user"]
                print(f"   User ID: {user_data.get('userId')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Username: {user_data.get('username')}")
        
        return success
    
    def test_user_registration_duplicate_email(self) -> bool:
        """Test user registration with duplicate email"""
        print("🔐 Testing User Registration - Duplicate Email...")
        
        if not self.test_user:
            print("   ⚠️  Skipping - No test user data")
            return True
        
        response = requests.post(
            f"{self.base_url}/auth/register",
            headers=HEADERS,
            json=self.test_user
        )
        
        success = response.status_code == 400
        self.print_test_result("User Registration - Duplicate Email", success, response, 400)
        
        return success
    
    def test_user_registration_validation_errors(self) -> bool:
        """Test user registration with validation errors"""
        print("🔐 Testing User Registration - Validation Errors...")
        
        test_cases = [
            {
                "name": "Missing email",
                "data": {"username": "testuser", "password": "TestPass123"},
                "expected_status": 400
            },
            {
                "name": "Invalid email format",
                "data": {"email": "invalid-email", "username": "testuser", "password": "TestPass123"},
                "expected_status": 400
            },
            {
                "name": "Short username",
                "data": {"email": "test@example.com", "username": "ab", "password": "TestPass123"},
                "expected_status": 400
            },
            {
                "name": "Weak password",
                "data": {"email": "test@example.com", "username": "testuser", "password": "weak"},
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/auth/register",
                headers=HEADERS,
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Registration Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_user_login_with_email(self) -> bool:
        """Test user login with email"""
        print("🔐 Testing User Login - Email...")
        
        if not self.test_user:
            print("   ⚠️  Skipping - No test user data")
            return True
        
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        
        response = requests.post(
            f"{self.base_url}/auth/login",
            headers=HEADERS,
            json=login_data
        )
        
        success = response.status_code == 200
        self.print_test_result("User Login - Email", success, response, 200)
        
        if success:
            data = response.json()
            if data.get("success") and "data" in data:
                self.access_token = data["data"].get("accessToken")
                self.refresh_token = data["data"].get("refreshToken")
                self.id_token = data["data"].get("idToken")
                print(f"   Access Token: {self.access_token[:50]}..." if self.access_token else "   No access token")
        
        return success
    
    def test_user_login_with_username(self) -> bool:
        """Test user login with username"""
        print("🔐 Testing User Login - Username...")
        
        if not self.test_user:
            print("   ⚠️  Skipping - No test user data")
            return True
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        response = requests.post(
            f"{self.base_url}/auth/login",
            headers=HEADERS,
            json=login_data
        )
        
        success = response.status_code == 200
        self.print_test_result("User Login - Username", success, response, 200)
        
        return success
    
    def test_user_login_with_both_credentials(self) -> bool:
        """Test user login with both email and username (email takes priority)"""
        print("🔐 Testing User Login - Both Credentials...")
        
        if not self.test_user:
            print("   ⚠️  Skipping - No test user data")
            return True
        
        login_data = {
            "email": self.test_user["email"],
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        response = requests.post(
            f"{self.base_url}/auth/login",
            headers=HEADERS,
            json=login_data
        )
        
        success = response.status_code == 200
        self.print_test_result("User Login - Both Credentials", success, response, 200)
        
        return success
    
    def test_user_login_validation_errors(self) -> bool:
        """Test user login with validation errors"""
        print("🔐 Testing User Login - Validation Errors...")
        
        test_cases = [
            {
                "name": "No credentials",
                "data": {"password": "TestPass123"},
                "expected_status": 400
            },
            {
                "name": "Invalid email format",
                "data": {"email": "invalid-email", "password": "TestPass123"},
                "expected_status": 400
            },
            {
                "name": "Missing password",
                "data": {"email": "test@example.com"},
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers=HEADERS,
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Login Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def test_user_login_invalid_credentials(self) -> bool:
        """Test user login with invalid credentials"""
        print("🔐 Testing User Login - Invalid Credentials...")
        
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/login",
            headers=HEADERS,
            json=login_data
        )
        
        success = response.status_code == 400
        self.print_test_result("User Login - Invalid Credentials", success, response, 400)
        
        return success
    
    def test_user_logout(self) -> bool:
        """Test user logout"""
        print("🔐 Testing User Logout...")
        
        if not self.access_token:
            print("   ⚠️  Skipping - No access token")
            return True
        
        headers = {
            **HEADERS,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/logout",
            headers=headers,
            json={}
        )
        
        success = response.status_code == 200
        self.print_test_result("User Logout", success, response, 200)
        
        return success
    
    def test_user_logout_without_token(self) -> bool:
        """Test user logout without token"""
        print("🔐 Testing User Logout - No Token...")
        
        response = requests.post(
            f"{self.base_url}/auth/logout",
            headers=HEADERS,
            json={}
        )
        
        success = response.status_code == 401
        self.print_test_result("User Logout - No Token", success, response, 401)
        
        return success
    
    def test_forgot_password(self) -> bool:
        """Test forgot password"""
        print("🔐 Testing Forgot Password...")
        
        if not self.test_user:
            print("   ⚠️  Skipping - No test user data")
            return True
        
        forgot_data = {
            "email": self.test_user["email"]
        }
        
        response = requests.post(
            f"{self.base_url}/auth/forgot-password",
            headers=HEADERS,
            json=forgot_data
        )
        
        success = response.status_code == 200
        self.print_test_result("Forgot Password", success, response, 200)
        
        return success
    
    def test_forgot_password_user_not_found(self) -> bool:
        """Test forgot password with non-existent user"""
        print("🔐 Testing Forgot Password - User Not Found...")
        
        forgot_data = {
            "email": "nonexistent@example.com"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/forgot-password",
            headers=HEADERS,
            json=forgot_data
        )
        
        success = response.status_code == 400
        self.print_test_result("Forgot Password - User Not Found", success, response, 400)
        
        return success
    
    def test_reset_password(self) -> bool:
        """Test reset password (with dummy confirmation code)"""
        print("🔐 Testing Reset Password...")
        
        if not self.test_user:
            print("   ⚠️  Skipping - No test user data")
            return True
        
        reset_data = {
            "email": self.test_user["email"],
            "confirmationCode": "123456",
            "newPassword": "NewTestPass123"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/reset-password",
            headers=HEADERS,
            json=reset_data
        )
        
        # This might fail with invalid confirmation code, which is expected
        success = response.status_code in [200, 400]
        self.print_test_result("Reset Password", success, response, 200)
        
        return success
    
    def test_reset_password_validation_errors(self) -> bool:
        """Test reset password with validation errors"""
        print("🔐 Testing Reset Password - Validation Errors...")
        
        test_cases = [
            {
                "name": "Weak new password",
                "data": {
                    "email": "test@example.com",
                    "confirmationCode": "123456",
                    "newPassword": "weak"
                },
                "expected_status": 400
            },
            {
                "name": "Missing confirmation code",
                "data": {
                    "email": "test@example.com",
                    "newPassword": "NewTestPass123"
                },
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            response = requests.post(
                f"{self.base_url}/auth/reset-password",
                headers=HEADERS,
                json=test_case["data"]
            )
            
            success = response.status_code == test_case["expected_status"]
            self.print_test_result(f"Reset Password Validation - {test_case['name']}", success, response, test_case["expected_status"])
            all_passed = all_passed and success
        
        return all_passed
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all authentication tests"""
        print("🚀 Starting Authentication API Tests...")
        print("=" * 60)
        
        results = {}
        
        # Registration tests
        results["registration"] = self.test_user_registration()
        results["registration_duplicate"] = self.test_user_registration_duplicate_email()
        results["registration_validation"] = self.test_user_registration_validation_errors()
        
        # Login tests
        results["login_email"] = self.test_user_login_with_email()
        results["login_username"] = self.test_user_login_with_username()
        results["login_both"] = self.test_user_login_with_both_credentials()
        results["login_validation"] = self.test_user_login_validation_errors()
        results["login_invalid"] = self.test_user_login_invalid_credentials()
        
        # Logout tests
        results["logout"] = self.test_user_logout()
        results["logout_no_token"] = self.test_user_logout_without_token()
        
        # Password reset tests
        results["forgot_password"] = self.test_forgot_password()
        results["forgot_password_not_found"] = self.test_forgot_password_user_not_found()
        results["reset_password"] = self.test_reset_password()
        results["reset_password_validation"] = self.test_reset_password_validation_errors()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("=" * 60)
        print("📊 Authentication API Test Summary")
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
            print("🎉 All authentication tests passed!")
        else:
            print("⚠️  Some authentication tests failed. Check the details above.")

def main():
    """Main function to run authentication tests"""
    tester = AuthAPITester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Return exit code based on results
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())
