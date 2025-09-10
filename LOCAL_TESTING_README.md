# 🧪 Local JWT Testing Guide

This guide explains how to test JWT validation locally using the provided test scripts.

## 📁 Test Scripts

### 1. `test_jwt_local.py`
Basic JWT validation testing with token generation and parsing.

```bash
python3 test_jwt_local.py
```

**Features:**
- ✅ JWT token generation
- ✅ JWT parsing and validation
- ✅ Authentication scenario testing
- ✅ API endpoint testing examples

### 2. `test_jwt_quick.py`
Quick test suite for JWT validation with live API calls.

```bash
python3 test_jwt_quick.py
```

**Features:**
- ✅ No authentication test (should fail)
- ✅ X-User-ID header test (should pass)
- ✅ JWT token test (should pass)
- ✅ Comments API test with JWT

### 3. `test_jwt_comprehensive.py`
Comprehensive test suite covering all authentication scenarios.

```bash
python3 test_jwt_comprehensive.py
```

**Features:**
- ✅ All authentication methods
- ✅ All API endpoints
- ✅ Error scenarios
- ✅ Public vs protected endpoints

### 4. `generate_jwt_tokens.py`
JWT token generator for testing with multiple users.

```bash
python3 generate_jwt_tokens.py
```

**Features:**
- ✅ Multiple test users
- ✅ Ready-to-use curl commands
- ✅ Token expiration handling

## 🔐 Authentication Methods

### 1. JWT Token Authentication
```bash
curl -X POST 'https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/posts/create' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -d '{"title": "Test Post", "content": "Test content", "subreddit_id": "subreddit_test_123", "post_type": "text"}'
```

### 2. X-User-ID Header Authentication
```bash
curl -X POST 'https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/posts/create' \
  -H 'Content-Type: application/json' \
  -H 'X-User-ID: user_1757485758_cde044d0' \
  -d '{"title": "Test Post", "content": "Test content", "subreddit_id": "subreddit_test_123", "post_type": "text"}'
```

## 🧪 Test Scenarios

### ✅ Expected Success Cases
1. **JWT Token with valid format** → 200 OK
2. **X-User-ID header** → 200 OK
3. **Public endpoints without auth** → 200 OK

### ❌ Expected Failure Cases
1. **No authentication** → 401 UNAUTHORIZED
2. **Invalid JWT token** → 401 UNAUTHORIZED
3. **Malformed JWT token** → 401 UNAUTHORIZED

## 🔧 JWT Token Structure

The test JWT tokens have the following structure:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_1757485758_cde044d0",
    "username": "testuser789",
    "iat": 1757491763,
    "exp": 1757495363
  }
}
```

## 📊 Test Results

### Quick Test Results
```
❌ Test 1: No Authentication
   Status: 401 - ✅ PASS

✅ Test 2: X-User-ID Header
   Status: 200 - ✅ PASS

🔐 Test 3: JWT Token
   Status: 200 - ✅ PASS

💬 Test 4: Comments with JWT
   Status: 200 - ✅ PASS
```

### Comprehensive Test Results
- **Posts API - No Auth**: ✅ 401 UNAUTHORIZED
- **Posts API - X-User-ID**: ✅ 200 SUCCESS
- **Posts API - JWT Token**: ✅ 200 SUCCESS
- **Comments API - No Auth**: ✅ 401 UNAUTHORIZED
- **Comments API - X-User-ID**: ✅ 200 SUCCESS
- **Comments API - JWT Token**: ✅ 200 SUCCESS
- **Public Endpoints**: ✅ 200 SUCCESS (mostly)
- **Invalid JWT Token**: ✅ 401 UNAUTHORIZED

## 🚀 Quick Start

1. **Run basic test:**
   ```bash
   python3 test_jwt_quick.py
   ```

2. **Generate test tokens:**
   ```bash
   python3 generate_jwt_tokens.py
   ```

3. **Run comprehensive test:**
   ```bash
   python3 test_jwt_comprehensive.py
   ```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error**: Make sure you have `requests` installed:
   ```bash
   pip install requests
   ```

2. **JWT Token Expired**: Generate new tokens:
   ```bash
   python3 generate_jwt_tokens.py
   ```

3. **API Endpoint Not Found**: Check if the Lambda functions are deployed correctly.

### Debug Mode

To see detailed JWT parsing, run:
```bash
python3 test_jwt_local.py
```

This will show:
- JWT header and payload
- Extracted user information
- Validation results

## 📝 Notes

- JWT tokens are valid for 1 hour by default
- Test tokens use a simple HMAC signature (not production-ready)
- All test scripts use the live API endpoints
- Authentication is hybrid (supports both JWT and X-User-ID)

## 🎯 Next Steps

1. **Production JWT**: Implement real Cognito JWT validation
2. **Token Refresh**: Add refresh token logic
3. **User Permissions**: Add role-based access control
4. **Rate Limiting**: Add authentication rate limiting
