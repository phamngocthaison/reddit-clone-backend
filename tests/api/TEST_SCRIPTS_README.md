# Reddit Clone Backend - API Test Scripts

Bộ test scripts toàn diện cho tất cả các API endpoints của Reddit Clone Backend.

## 📁 Cấu trúc Test Scripts

```
test_scripts/
├── test_auth_apis.py          # Authentication APIs
├── test_posts_apis.py         # Posts APIs  
├── test_comments_apis.py      # Comments APIs
├── test_subreddits_apis.py    # Subreddits APIs
├── test_feeds_apis.py         # Feeds APIs
├── test_all_apis.py           # Main test runner
└── TEST_SCRIPTS_README.md     # Documentation
```

## 🚀 Cách sử dụng

### 1. Chạy tất cả tests
```bash
python test_all_apis.py
```

### 2. Chạy từng module riêng lẻ
```bash
# Authentication APIs
python test_auth_apis.py

# Posts APIs
python test_posts_apis.py

# Comments APIs
python test_comments_apis.py

# Subreddits APIs
python test_subreddits_apis.py

# Feeds APIs
python test_feeds_apis.py
```

### 3. Chạy với timeout
```bash
# Set timeout 10 minutes
timeout 600 python test_all_apis.py
```

## 📋 Test Coverage

### Authentication APIs (`test_auth_apis.py`)
- ✅ User Registration
- ✅ User Login (email, username, both)
- ✅ User Logout
- ✅ Forgot Password
- ✅ Reset Password
- ✅ Validation Error Testing
- ✅ Duplicate User Testing
- ✅ Invalid Credentials Testing

**Total Tests: 12**

### Posts APIs (`test_posts_apis.py`)
- ✅ Create Post (text, link)
- ✅ Get Posts (with filters)
- ✅ Get Post by ID
- ✅ Update Post
- ✅ Delete Post
- ✅ Vote Post (upvote, downvote, remove)
- ✅ Validation Error Testing
- ✅ Access Control Testing
- ✅ Edge Cases (trailing slash, etc.)

**Total Tests: 15**

### Comments APIs (`test_comments_apis.py`)
- ✅ Create Comment
- ✅ Create Reply Comment
- ✅ Get Comments (with filters)
- ✅ Get Comments by Post ID
- ✅ Get Comment by ID
- ✅ Update Comment
- ✅ Delete Comment
- ✅ Vote Comment (upvote, downvote, remove)
- ✅ Validation Error Testing
- ✅ Access Control Testing

**Total Tests: 16**

### Subreddits APIs (`test_subreddits_apis.py`)
- ✅ Create Subreddit
- ✅ Get Subreddits (with filters)
- ✅ Get Subreddit by ID/Name
- ✅ Update Subreddit
- ✅ Join/Leave Subreddit
- ✅ Get Subreddit Posts
- ✅ Add/Remove Moderator
- ✅ Delete Subreddit
- ✅ Validation Error Testing
- ✅ Access Control Testing

**Total Tests: 18**

### Feeds APIs (`test_feeds_apis.py`)
- ✅ Get Feeds (with filters)
- ✅ Refresh Feeds
- ✅ Get Feeds Stats
- ✅ JWT Token Testing
- ✅ Validation Error Testing
- ✅ Integration Scenario Testing

**Total Tests: 11**

## 🔧 Configuration

### Base URL
Tất cả scripts sử dụng production URL:
```
https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod
```

### Headers
- `Content-Type: application/json`
- `X-User-ID: <test_user_id>` (for testing)
- `Authorization: Bearer <token>` (for JWT testing)

### Test Data
- Tự động generate test data với timestamp
- Sử dụng random strings để tránh conflicts
- Clean up sau mỗi test run

## 📊 Test Results

### Output Format
```
✅ PASS Test Name
❌ FAIL Test Name
   Expected: 200, Got: 400
   Response: Error message...
```

### Summary Report
```
📊 API Test Summary
==================
Total Tests: 72
Passed: 68
Failed: 4
Success Rate: 94.4%
```

### JSON Results File
Test results được lưu vào file JSON với timestamp:
```
test_results_20250110_143022.json
```

## 🐛 Debugging

### Common Issues
1. **Network Timeout**: Tăng timeout trong script
2. **Validation Errors**: Kiểm tra request data format
3. **Authentication Errors**: Kiểm tra headers và tokens
4. **Rate Limiting**: Thêm delay giữa các requests

### Debug Mode
Thêm debug prints trong scripts:
```python
print(f"Request: {method} {url}")
print(f"Headers: {headers}")
print(f"Data: {json.dumps(data, indent=2)}")
print(f"Response: {response.status_code} {response.text}")
```

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install requests
      - name: Run API tests
        run: python test_all_apis.py
```

### Docker Example
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY test_*.py ./
RUN pip install requests
CMD ["python", "test_all_apis.py"]
```

## 📈 Performance Monitoring

### Metrics Tracked
- Response time per endpoint
- Success rate per module
- Total test duration
- Memory usage (if needed)

### Performance Baselines
- Individual test: < 5 seconds
- Module test: < 2 minutes
- Full test suite: < 10 minutes

## 🛠️ Maintenance

### Adding New Tests
1. Tạo test function với naming convention: `test_<feature>_<scenario>()`
2. Sử dụng `print_test_result()` để format output
3. Return boolean success status
4. Add vào `run_all_tests()` method

### Updating Existing Tests
1. Maintain backward compatibility
2. Update test data if API changes
3. Update expected status codes
4. Update documentation

### Test Data Management
- Use unique identifiers (timestamp + random)
- Clean up created data after tests
- Avoid hardcoded test data
- Use environment variables for configuration

## 📞 Support

Nếu gặp vấn đề với test scripts:

1. **Check logs**: Xem output chi tiết của failed tests
2. **Verify API status**: Đảm bảo API endpoints đang hoạt động
3. **Check network**: Kiểm tra kết nối internet
4. **Update scripts**: Cập nhật scripts theo API changes

## 🎯 Best Practices

1. **Isolation**: Mỗi test độc lập, không phụ thuộc vào test khác
2. **Cleanup**: Xóa test data sau khi test xong
3. **Error Handling**: Handle tất cả error cases
4. **Documentation**: Comment rõ ràng cho mỗi test
5. **Maintenance**: Update tests khi API thay đổi

---

**Happy Testing! 🚀**
