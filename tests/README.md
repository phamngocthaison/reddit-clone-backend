# Reddit Clone Backend - Test Suite

Thư mục chứa tất cả các test scripts cho Reddit Clone Backend.

## 📁 Cấu trúc thư mục

```
tests/
├── api/                          # API test scripts
│   ├── test_auth_apis.py         # Authentication APIs
│   ├── test_posts_apis.py        # Posts APIs
│   ├── test_comments_apis.py     # Comments APIs
│   ├── test_subreddits_apis.py   # Subreddits APIs
│   ├── test_feeds_apis.py        # Feeds APIs
│   ├── test_all_apis.py          # Main test runner
│   ├── run_tests.py              # Command-line test runner
│   ├── quick_test.py             # Quick functionality test
│   └── TEST_SCRIPTS_README.md    # Detailed documentation
├── conftest.py                   # Pytest configuration
├── test_models.py                # Model tests
├── test_services.py              # Service tests
└── README.md                     # This file
```

## 🚀 Cách sử dụng

### Từ root directory:

```bash
# Chạy tất cả API tests
python3 run_api_tests.py

# Chạy quick test
python3 run_api_tests.py --quick

# Chạy test module cụ thể
python3 run_api_tests.py --module auth
python3 run_api_tests.py --module posts
python3 run_api_tests.py --module comments
python3 run_api_tests.py --module subreddits
python3 run_api_tests.py --module feeds
```

### Từ tests/api/ directory:

```bash
cd tests/api/

# Chạy tất cả tests
python3 test_all_apis.py

# Chạy từng module
python3 test_auth_apis.py
python3 test_posts_apis.py
python3 test_comments_apis.py
python3 test_subreddits_apis.py
python3 test_feeds_apis.py

# Chạy quick test
python3 quick_test.py

# Chạy với options
python3 run_tests.py --module auth --timeout 300
```

## 🧪 Test Types

### API Tests (`tests/api/`)
- **Comprehensive API testing** cho tất cả endpoints
- **74 test cases** covering toàn bộ API contract
- **Automated test data generation**
- **Detailed error reporting**
- **JSON results export**

### Unit Tests (`tests/`)
- **Model validation tests**
- **Service logic tests**
- **Pytest-based testing**

## 🔧 CI/CD Integration

### GitHub Actions
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
        run: pip install requests pytest
      - name: Run API tests
        run: python3 run_api_tests.py
```

### Deploy with Tests
```bash
# Deploy infrastructure và chạy tests
python3 deploy_with_tests.py
```

## 📊 Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Authentication | 14 | Registration, Login, Logout, Password Reset |
| Posts | 15 | CRUD, Voting, Filtering, Validation |
| Comments | 16 | CRUD, Replies, Voting, Filtering |
| Subreddits | 18 | CRUD, Join/Leave, Moderation |
| Feeds | 11 | Personalized Feeds, Refresh, Stats |
| **Total** | **74** | **Complete API Coverage** |

## 🐛 Debugging

### Common Issues
1. **Network timeout**: Tăng timeout trong scripts
2. **API errors**: Kiểm tra API endpoints status
3. **Test data conflicts**: Sử dụng unique timestamps
4. **Permission errors**: Kiểm tra file permissions

### Debug Mode
```bash
# Verbose output
python3 run_api_tests.py --module auth --verbose

# Quick test for basic functionality
python3 run_api_tests.py --quick
```

## 📈 Performance

### Test Execution Times
- **Quick test**: ~30 seconds
- **Single module**: ~2-5 minutes
- **Full test suite**: ~10-15 minutes

### Optimization Tips
- Chạy tests song song khi có thể
- Sử dụng quick test cho development
- Cache test data khi có thể
- Monitor API response times

## 🔄 Maintenance

### Adding New Tests
1. Tạo test function trong module tương ứng
2. Follow naming convention: `test_<feature>_<scenario>()`
3. Sử dụng `print_test_result()` cho output formatting
4. Return boolean success status
5. Update documentation

### Updating Tests
1. Maintain backward compatibility
2. Update test data khi API changes
3. Update expected status codes
4. Test với different environments

## 📞 Support

Nếu gặp vấn đề:
1. Check logs chi tiết
2. Verify API status
3. Check network connectivity
4. Update test scripts nếu cần

---

**Happy Testing! 🚀**
