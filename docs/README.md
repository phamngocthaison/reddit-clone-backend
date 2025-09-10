# Reddit Clone Backend - API Documentation

## 📚 Tài liệu API hoàn chỉnh

Bộ tài liệu này cung cấp hướng dẫn chi tiết để tích hợp với Reddit Clone Backend API.

## 🚀 Quick Start

### Base URLs
- **Production**: `https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod`
- **Local Development**: `http://localhost:5000`

### Authentication
API sử dụng JWT tokens. Thêm header sau vào requests:
```
Authorization: Bearer <access_token>
```

## 📖 Tài liệu chi tiết

### 1. [API Contract](./api-contract.md)
- Chi tiết tất cả endpoints
- Request/Response schemas
- Error codes và status codes
- Validation rules
- Examples với cURL

### 2. [Frontend Integration Guide](./frontend-integration-guide.md)
- Hướng dẫn tích hợp cho Frontend developers
- Code examples cho React, Vue.js
- Error handling best practices
- Security considerations
- Performance optimization
- Testing strategies

### 3. [Postman Collection](./postman-collection.json)
- Collection đầy đủ để test API
- Auto-save tokens từ login response
- Test cases cho tất cả scenarios
- Environment variables setup

### 4. [Subreddit APIs Collection](./Reddit_Clone_Subreddit_APIs.postman_collection.json)
- Collection riêng cho Subreddit APIs
- Test cases cho tất cả subreddit operations
- Join/Leave subreddit functionality
- Moderator management

### 5. [OpenAPI Specification](./openapi-spec.yaml)
- Swagger/OpenAPI 3.0 spec
- Interactive API documentation
- Import vào Postman, Insomnia, etc.
- Code generation support

### 6. [Development Roadmap](./development-roadmap.md)
- Chi tiết roadmap phát triển
- Timeline và milestones
- Technical architecture evolution
- Success metrics và KPIs

## 🔧 Setup và Testing

### 1. Import Postman Collection
```bash
# Download collection
curl -O https://raw.githubusercontent.com/reddit-clone/backend/main/docs/postman-collection.json

# Import vào Postman
# File -> Import -> Chọn file postman-collection.json
```

### 2. Setup Environment Variables
Tạo environment trong Postman với các variables:
- `baseUrl`: `https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod`
- `email`: `test@example.com`
- `username`: `testuser`
- `password`: `TestPass123`

### 3. Test API với cURL
```bash
# Registration
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123"
  }'

# Login
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

## 🛠️ Frontend Integration

### React Example
```typescript
import AuthService from './services/AuthService';

const authService = new AuthService('https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod');

// Register
const user = await authService.register('user@example.com', 'username', 'password');

// Login
const loginData = await authService.login('user@example.com', 'password');
```

### Vue.js Example
```typescript
import { useAuthStore } from './stores/auth';

const authStore = useAuthStore();

// Register
await authStore.register('user@example.com', 'username', 'password');

// Login
await authStore.login('user@example.com', 'password');
```

## 📊 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Đăng ký user mới | ❌ |
| `POST` | `/auth/login` | Đăng nhập | ❌ |
| `POST` | `/auth/logout` | Đăng xuất | ✅ |
| `POST` | `/auth/forgot-password` | Quên mật khẩu | ❌ |
| `POST` | `/auth/reset-password` | Reset mật khẩu | ❌ |
| `OPTIONS` | `/auth/*` | CORS preflight | ❌ |

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Validation**: Strong password requirements
- **Input Validation**: Comprehensive input sanitization
- **CORS Support**: Cross-origin request handling
- **Error Handling**: Secure error messages

## 📈 Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data
  },
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "message": null,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## 🧪 Testing

### Unit Tests
```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### Integration Tests
```bash
# Run integration tests
npm run test:integration
```

### API Tests
```bash
# Run API tests
npm run test:api
```

## 🚀 Deployment

### Environment Variables
```bash
# Production
API_BASE_URL=https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod

# Development
API_BASE_URL=http://localhost:5000
```

### Health Check
```bash
curl https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/health
```

## 📞 Support

### Issues
- Tạo issue trên GitHub: [Issues](https://github.com/reddit-clone/backend/issues)
- Label: `api`, `documentation`, `integration`

### Contact
- Email: support@redditclone.com
- Slack: #backend-support
- Discord: Reddit Clone Community

## 📝 Changelog

### v1.1.0 (2025-09-10)
- ✅ Subreddit System implementation
- ✅ Create, read, update, delete subreddits
- ✅ Join/leave subreddit functionality
- ✅ Moderator management
- ✅ Subreddit search and filtering
- ✅ Subreddit posts listing
- ✅ Separate SubredditsLambda for better performance
- ✅ Subreddit-specific Postman collection

### v1.0.0 (2025-09-08)
- ✅ Initial API release
- ✅ User registration and login
- ✅ Password reset functionality
- ✅ JWT token authentication
- ✅ CORS support
- ✅ Comprehensive documentation
- ✅ Postman collection
- ✅ OpenAPI specification

## 🔄 Versioning

API sử dụng semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

## 📄 License

MIT License - Xem [LICENSE](../LICENSE) file để biết thêm chi tiết.

---

## 🎯 Next Steps

1. **Import Postman Collection** để test API
2. **Đọc Frontend Integration Guide** để tích hợp
3. **Sử dụng OpenAPI spec** để generate client code
4. **Tham khảo API Contract** cho chi tiết endpoints

## 💡 Tips

- Luôn handle errors properly trong Frontend
- Sử dụng environment variables cho base URLs
- Implement retry logic cho network requests
- Cache tokens securely
- Monitor API performance và errors

---

**Happy Coding! 🚀**
