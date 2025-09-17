# Reddit Clone Backend - Testing Guide

This directory contains comprehensive testing scripts for the Reddit Clone Backend API, based on the Postman collection `Reddit_Clone_Backend_v2.5.postman_collection.json`.

## 🚀 Quick Start

### Simple Test (Recommended for deployment verification)
```bash
./run_tests.sh
# or
python3 quick_test_simple.py
```

### Full Test Suite
```bash
./run_tests.sh --level full
# or
python3 quick_test.py
```

## 📁 Test Files

### 1. `quick_test_simple.py`
- **Purpose**: Quick verification of critical endpoints
- **Duration**: ~10-30 seconds
- **Use Case**: After each deployment
- **Tests**: 6 critical endpoints only

### 2. `quick_test.py`
- **Purpose**: Comprehensive test of all endpoints
- **Duration**: ~60-120 seconds
- **Use Case**: Full regression testing
- **Tests**: All major API endpoints with authentication

### 3. `run_tests.sh`
- **Purpose**: Test runner with options and timeout handling
- **Features**: 
  - Multiple test levels
  - Timeout protection
  - Exit code handling
  - Help documentation

## 🧪 Test Coverage

### Simple Test (6 endpoints)
- ✅ GET /posts - Get posts list
- ✅ GET /subreddits - Get subreddits list
- ✅ GET /subreddits/{id}/posts - Get subreddit posts
- ✅ GET /users/{id}/posts - Get user posts
- ✅ GET /posts/{id} - Get specific post
- ✅ GET /comments/{id} - Get specific comment

### Full Test Suite (20+ endpoints)
- 🔐 **Authentication** (6 endpoints)
  - Register User
  - Login with Email
  - Get Current User Profile
- 📝 **Posts** (5 endpoints)
  - Create Post
  - Get Posts
  - Get Post by ID
  - Vote Post
- 💬 **Comments** (5 endpoints)
  - Create Comment
  - Get Comments
  - Get Comment by ID
  - Vote Comment
- 🏘️ **Subreddits** (4 endpoints)
  - Get Subreddits
  - Get Subreddit by ID
  - Get Subreddit Posts
  - Join Subreddit
- 👤 **User Profiles** (3 endpoints)
  - Get Public User Profile
  - Get User Posts
  - Get User Comments
- 📰 **News Feeds** (2 endpoints)
  - Get Feed
  - Get Feed Stats

## 🛠️ Usage Examples

### Basic Usage
```bash
# Run simple test (default)
./run_tests.sh

# Run full test suite
./run_tests.sh --level full

# Run with verbose output
./run_tests.sh --verbose
```

### Direct Python Execution
```bash
# Simple test
python3 quick_test_simple.py

# Full test suite
python3 quick_test.py
```

### CI/CD Integration
```bash
# In your deployment pipeline
./run_tests.sh --level simple
if [ $? -eq 0 ]; then
    echo "Deployment successful!"
else
    echo "Deployment failed tests!"
    exit 1
fi
```

## 📊 Test Results

### Success Output
```
🚀 Reddit Clone Backend - Quick Test
====================================
✅ Get Posts
✅ Get Subreddits
✅ Get Subreddit Posts
✅ Get User Posts
✅ Get Post by ID
✅ Get Comment by ID
====================================
Results: 6/6 tests passed
Success Rate: 100.0%
```

### Failure Output
```
❌ Get Posts
   Status: 500
❌ Get Subreddits
   Error: Connection timeout
====================================
Results: 4/6 tests passed
Success Rate: 66.7%
```

## ⚙️ Configuration

### Environment Variables
The tests use the following configuration:
- `BASE_URL`: `https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod`
- `TEST_USER_EMAIL`: `test@example.com`
- `TEST_USER_USERNAME`: `testuser123`
- `TEST_PASSWORD`: `TestPass123`

### Test Data
- Test Subreddit ID: `subreddit_1757518063_01b8625d`
- Test Post ID: `post_1757508287_f8e2cbd7`
- Test Comment ID: `comment_1757509982_351caa27`

## 🔧 Customization

### Adding New Tests
1. Edit `quick_test_simple.py` for simple tests
2. Edit `quick_test.py` for full test suite
3. Follow the existing pattern:
   ```python
   success, data = self.make_request("GET", "/new-endpoint")
   self.log_test("New Test", success, "Description")
   ```

### Modifying Test Data
Update the configuration variables at the top of each script:
```python
BASE_URL = "your-api-url"
TEST_USER_EMAIL = "your-test-email"
# ... other variables
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Check if the API is running
   - Verify the BASE_URL is correct
   - Check network connectivity

2. **Authentication Failures**
   - Verify test user credentials
   - Check if user exists in the system
   - Verify Cognito configuration

3. **Test Data Not Found**
   - Update test IDs with valid ones from your database
   - Check if test data exists in DynamoDB

4. **Permission Errors**
   - Make sure scripts are executable: `chmod +x *.py *.sh`
   - Check Python installation: `python3 --version`

### Debug Mode
For detailed debugging, modify the scripts to print full responses:
```python
print(f"Response: {json.dumps(response_data, indent=2)}")
```

## 📈 Monitoring

### Exit Codes
- `0`: All tests passed
- `1`: Some tests failed
- `124`: Test timed out

### Logging
Test results are logged with timestamps and can be redirected to files:
```bash
./run_tests.sh > test_results.log 2>&1
```

## 🔄 Integration with Deployment

### Pre-deployment
```bash
# Quick verification before deployment
./run_tests.sh --level simple
```

### Post-deployment
```bash
# Full verification after deployment
./run_tests.sh --level full
```

### Automated Testing
Add to your CI/CD pipeline:
```yaml
- name: Test API
  run: |
    ./run_tests.sh --level simple
    if [ $? -ne 0 ]; then
      echo "API tests failed!"
      exit 1
    fi
```

## 📝 Notes

- Tests are designed to be non-destructive (read-only operations)
- Authentication tests may create test users (safe to run multiple times)
- Full test suite includes write operations (create posts, comments)
- All tests have timeout protection to prevent hanging
- Tests are based on the actual Postman collection structure
