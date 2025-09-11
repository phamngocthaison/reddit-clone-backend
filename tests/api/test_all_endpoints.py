#!/usr/bin/env python3
"""
Comprehensive test script for all Reddit Clone Backend endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser123"
TEST_PASSWORD = "TestPass123"

# Test results storage
test_results = {
    "passed": 0,
    "failed": 0,
    "total": 0,
    "details": []
}

def log_test(test_name, success, message="", response_data=None):
    """Log test result"""
    test_results["total"] += 1
    if success:
        test_results["passed"] += 1
        status = "✅ PASS"
    else:
        test_results["failed"] += 1
        status = "❌ FAIL"
    
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")
    if response_data:
        print(f"   Response: {json.dumps(response_data, indent=2)}")
    print()
    
    test_results["details"].append({
        "test": test_name,
        "success": success,
        "message": message,
        "response": response_data
    })

def test_auth_endpoints():
    """Test all authentication endpoints"""
    print("🔐 TESTING AUTHENTICATION ENDPOINTS")
    print("=" * 50)
    
    # Test 1: User Registration
    print("1. Testing User Registration...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            log_test("User Registration", True, "User registered successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            log_test("User Registration", True, "User already exists (expected)")
        else:
            log_test("User Registration", False, f"Unexpected status: {response.status_code}", response.json())
    except Exception as e:
        log_test("User Registration", False, f"Exception: {str(e)}")
    
    # Test 2: Login with Email
    print("2. Testing Login with Email...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data.get("data", {}):
                log_test("Login with Email", True, "Login successful with email")
                return data["data"]["access_token"]  # Return token for other tests
            else:
                log_test("Login with Email", False, "No access token in response", data)
        else:
            log_test("Login with Email", False, f"Login failed: {response.status_code}", response.json())
    except Exception as e:
        log_test("Login with Email", False, f"Exception: {str(e)}")
    
    # Test 3: Login with Username
    print("3. Testing Login with Username...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data.get("data", {}):
                log_test("Login with Username", True, "Login successful with username")
                return data["data"]["access_token"]  # Return token for other tests
            else:
                log_test("Login with Username", False, "No access token in response", data)
        else:
            log_test("Login with Username", False, f"Login failed: {response.status_code}", response.json())
    except Exception as e:
        log_test("Login with Username", False, f"Exception: {str(e)}")
    
    # Test 4: Login with Both Email and Username
    print("4. Testing Login with Both Email and Username...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data.get("data", {}):
                log_test("Login with Both", True, "Login successful with both credentials")
                return data["data"]["access_token"]  # Return token for other tests
            else:
                log_test("Login with Both", False, "No access token in response", data)
        else:
            log_test("Login with Both", False, f"Login failed: {response.status_code}", response.json())
    except Exception as e:
        log_test("Login with Both", False, f"Exception: {str(e)}")
    
    # Test 5: Login Validation Error (No Credentials)
    print("5. Testing Login Validation Error...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 400:
            data = response.json()
            if data.get("error", {}).get("code") == "VALIDATION_ERROR":
                log_test("Login Validation Error", True, "Validation error correctly returned")
            else:
                log_test("Login Validation Error", False, "Wrong error type", data)
        else:
            log_test("Login Validation Error", False, f"Expected 400, got {response.status_code}", response.json())
    except Exception as e:
        log_test("Login Validation Error", False, f"Exception: {str(e)}")
    
    # Test 6: Login with Invalid Credentials
    print("6. Testing Login with Invalid Credentials...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword123"
        })
        
        if response.status_code == 400:
            data = response.json()
            if "LOGIN_ERROR" in str(data):
                log_test("Login Invalid Credentials", True, "Invalid credentials error correctly returned")
            else:
                log_test("Login Invalid Credentials", False, "Wrong error type", data)
        else:
            log_test("Login Invalid Credentials", False, f"Expected 400, got {response.status_code}", response.json())
    except Exception as e:
        log_test("Login Invalid Credentials", False, f"Exception: {str(e)}")
    
    return None

def test_posts_endpoints(access_token=None):
    """Test all posts endpoints"""
    print("\n📝 TESTING POSTS ENDPOINTS")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "user_1757485758_cde044d0"  # Test user ID
    }
    
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    # Test 1: Create Post
    print("1. Testing Create Post...")
    try:
        response = requests.post(f"{BASE_URL}/posts/create", json={
            "title": "Test Post for API Testing",
            "content": "This is a test post created during API testing",
            "subreddit_id": "subreddit_test_123",
            "post_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        }, headers=headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            post_id = data.get("data", {}).get("post", {}).get("post_id")
            log_test("Create Post", True, f"Post created successfully, ID: {post_id}")
            
            # Test 2: Get Posts
            print("2. Testing Get Posts...")
            try:
                response = requests.get(f"{BASE_URL}/posts", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("posts", [])
                    log_test("Get Posts", True, f"Retrieved {len(posts)} posts")
                else:
                    log_test("Get Posts", False, f"Failed to get posts: {response.status_code}", response.json())
            except Exception as e:
                log_test("Get Posts", False, f"Exception: {str(e)}")
            
            # Test 3: Get Post by ID
            print("3. Testing Get Post by ID...")
            try:
                response = requests.get(f"{BASE_URL}/posts/{post_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    retrieved_post = data.get("data", {}).get("post", {})
                    if retrieved_post.get("post_id") == post_id:
                        log_test("Get Post by ID", True, "Post retrieved successfully")
                    else:
                        log_test("Get Post by ID", False, "Wrong post retrieved", data)
                else:
                    log_test("Get Post by ID", False, f"Failed to get post: {response.status_code}", response.json())
            except Exception as e:
                log_test("Get Post by ID", False, f"Exception: {str(e)}")
            
            # Test 4: Update Post
            print("4. Testing Update Post...")
            try:
                response = requests.put(f"{BASE_URL}/posts/{post_id}", json={
                    "title": "Updated Test Post Title",
                    "content": "This is the updated content of the test post"
                }, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    updated_post = data.get("data", {}).get("post", {})
                    if updated_post.get("title") == "Updated Test Post Title":
                        log_test("Update Post", True, "Post updated successfully")
                    else:
                        log_test("Update Post", False, "Post not updated correctly", data)
                else:
                    log_test("Update Post", False, f"Failed to update post: {response.status_code}", response.json())
            except Exception as e:
                log_test("Update Post", False, f"Exception: {str(e)}")
            
            # Test 5: Vote Post
            print("5. Testing Vote Post...")
            try:
                response = requests.post(f"{BASE_URL}/posts/{post_id}/vote", json={
                    "vote_type": "upvote"
                }, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get("data", {}).get("stats", {})
                    if stats.get("upvotes", 0) > 0:
                        log_test("Vote Post", True, "Post voted successfully")
                    else:
                        log_test("Vote Post", False, "Vote not recorded", data)
                else:
                    log_test("Vote Post", False, f"Failed to vote post: {response.status_code}", response.json())
            except Exception as e:
                log_test("Vote Post", False, f"Exception: {str(e)}")
            
            # Test 6: Delete Post
            print("6. Testing Delete Post...")
            try:
                response = requests.delete(f"{BASE_URL}/posts/{post_id}", headers=headers)
                if response.status_code == 200:
                    log_test("Delete Post", True, "Post deleted successfully")
                else:
                    log_test("Delete Post", False, f"Failed to delete post: {response.status_code}", response.json())
            except Exception as e:
                log_test("Delete Post", False, f"Exception: {str(e)}")
            
            return post_id
        else:
            log_test("Create Post", False, f"Failed to create post: {response.status_code}", response.json())
    except Exception as e:
        log_test("Create Post", False, f"Exception: {str(e)}")
    
    return None

def test_comments_endpoints(access_token=None):
    """Test all comments endpoints"""
    print("\n💬 TESTING COMMENTS ENDPOINTS")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "user_1757485758_cde044d0"  # Test user ID
    }
    
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    # First create a post to comment on
    post_id = "post_test_123"  # Use a test post ID
    
    # Test 1: Create Comment
    print("1. Testing Create Comment...")
    try:
        response = requests.post(f"{BASE_URL}/comments/create", json={
            "post_id": post_id,
            "content": "This is a test comment for API testing",
            "comment_type": "comment",
            "is_nsfw": False,
            "is_spoiler": False
        }, headers=headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            comment_id = data.get("data", {}).get("comment", {}).get("comment_id")
            log_test("Create Comment", True, f"Comment created successfully, ID: {comment_id}")
            
            # Test 2: Get Comments
            print("2. Testing Get Comments...")
            try:
                response = requests.get(f"{BASE_URL}/comments?post_id={post_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    comments = data.get("data", {}).get("comments", [])
                    log_test("Get Comments", True, f"Retrieved {len(comments)} comments")
                else:
                    log_test("Get Comments", False, f"Failed to get comments: {response.status_code}", response.json())
            except Exception as e:
                log_test("Get Comments", False, f"Exception: {str(e)}")
            
            # Test 3: Get Comment by ID
            print("3. Testing Get Comment by ID...")
            try:
                response = requests.get(f"{BASE_URL}/comments/{comment_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    retrieved_comment = data.get("data", {}).get("comment", {})
                    if retrieved_comment.get("comment_id") == comment_id:
                        log_test("Get Comment by ID", True, "Comment retrieved successfully")
                    else:
                        log_test("Get Comment by ID", False, "Wrong comment retrieved", data)
                else:
                    log_test("Get Comment by ID", False, f"Failed to get comment: {response.status_code}", response.json())
            except Exception as e:
                log_test("Get Comment by ID", False, f"Exception: {str(e)}")
            
            # Test 4: Update Comment
            print("4. Testing Update Comment...")
            try:
                response = requests.put(f"{BASE_URL}/comments/{comment_id}", json={
                    "content": "This is the updated comment content"
                }, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    updated_comment = data.get("data", {}).get("comment", {})
                    if updated_comment.get("content") == "This is the updated comment content":
                        log_test("Update Comment", True, "Comment updated successfully")
                    else:
                        log_test("Update Comment", False, "Comment not updated correctly", data)
                else:
                    log_test("Update Comment", False, f"Failed to update comment: {response.status_code}", response.json())
            except Exception as e:
                log_test("Update Comment", False, f"Exception: {str(e)}")
            
            # Test 5: Vote Comment
            print("5. Testing Vote Comment...")
            try:
                response = requests.post(f"{BASE_URL}/comments/{comment_id}/vote", json={
                    "vote_type": "upvote"
                }, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get("data", {}).get("stats", {})
                    if stats.get("upvotes", 0) > 0:
                        log_test("Vote Comment", True, "Comment voted successfully")
                    else:
                        log_test("Vote Comment", False, "Vote not recorded", data)
                else:
                    log_test("Vote Comment", False, f"Failed to vote comment: {response.status_code}", response.json())
            except Exception as e:
                log_test("Vote Comment", False, f"Exception: {str(e)}")
            
            # Test 6: Delete Comment
            print("6. Testing Delete Comment...")
            try:
                response = requests.delete(f"{BASE_URL}/comments/{comment_id}", headers=headers)
                if response.status_code == 200:
                    log_test("Delete Comment", True, "Comment deleted successfully")
                else:
                    log_test("Delete Comment", False, f"Failed to delete comment: {response.status_code}", response.json())
            except Exception as e:
                log_test("Delete Comment", False, f"Exception: {str(e)}")
            
            return comment_id
        else:
            log_test("Create Comment", False, f"Failed to create comment: {response.status_code}", response.json())
    except Exception as e:
        log_test("Create Comment", False, f"Exception: {str(e)}")
    
    return None

def test_error_cases():
    """Test error cases and edge cases"""
    print("\n🚨 TESTING ERROR CASES")
    print("=" * 50)
    
    # Test 1: Invalid Endpoint
    print("1. Testing Invalid Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/invalid/endpoint")
        if response.status_code in [403, 404]:
            log_test("Invalid Endpoint", True, f"{response.status_code} error correctly returned")
        else:
            log_test("Invalid Endpoint", False, f"Expected 403/404, got {response.status_code}", response.json())
    except Exception as e:
        log_test("Invalid Endpoint", False, f"Exception: {str(e)}")
    
    # Test 2: Invalid JSON
    print("2. Testing Invalid JSON...")
    try:
        response = requests.post(f"{BASE_URL}/posts/create", 
                               data="invalid json",
                               headers={"Content-Type": "application/json", "X-User-ID": "user_1757485758_cde044d0"})
        if response.status_code in [400, 401]:
            log_test("Invalid JSON", True, f"{response.status_code} error correctly returned for invalid JSON")
        else:
            log_test("Invalid JSON", False, f"Expected 400/401, got {response.status_code}", response.json())
    except Exception as e:
        log_test("Invalid JSON", False, f"Exception: {str(e)}")
    
    # Test 3: Missing Required Fields
    print("3. Testing Missing Required Fields...")
    try:
        response = requests.post(f"{BASE_URL}/posts/create", json={
            "content": "This post has no title"
        }, headers={"Content-Type": "application/json", "X-User-ID": "user_1757485758_cde044d0"})
        
        if response.status_code == 400:
            data = response.json()
            if "VALIDATION_ERROR" in str(data) or "validation" in str(data).lower():
                log_test("Missing Required Fields", True, "Validation error correctly returned")
            else:
                log_test("Missing Required Fields", False, "Wrong error type", data)
        else:
            log_test("Missing Required Fields", False, f"Expected 400, got {response.status_code}", response.json())
    except Exception as e:
        log_test("Missing Required Fields", False, f"Exception: {str(e)}")

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Success Rate: {(test_results['passed'] / test_results['total'] * 100):.1f}%")
    
    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS:")
        for detail in test_results['details']:
            if not detail['success']:
                print(f"  - {detail['test']}: {detail['message']}")
    
    print("\n" + "=" * 60)

def main():
    """Main test function"""
    print("🚀 STARTING COMPREHENSIVE API TESTING")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test authentication endpoints and get access token
    access_token = test_auth_endpoints()
    
    # Test posts endpoints
    post_id = test_posts_endpoints(access_token)
    
    # Test comments endpoints
    comment_id = test_comments_endpoints(access_token)
    
    # Test error cases
    test_error_cases()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
