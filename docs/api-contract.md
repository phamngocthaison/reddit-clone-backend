# Reddit Clone Backend - API Contract

## Base URL
```
Production: https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod
Local Development: http://localhost:5000
```

## Authentication
API sử dụng JWT tokens cho authentication. Tất cả protected endpoints yêu cầu `Authorization` header:
```
Authorization: Bearer <access_token>
```

## Common Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data here
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

## HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `500` - Internal Server Error

---

## Authentication Endpoints

### 1. User Registration

**POST** `/auth/register`

Đăng ký user mới.

#### Request Body
```json
{
  "email": "user@example.com",
  "username": "username123",
  "password": "SecurePass123"
}
```

#### Validation Rules
- **email**: Valid email format, required
- **username**: 3-20 characters, alphanumeric and underscores only, required
- **password**: Minimum 8 characters, must contain uppercase, lowercase, and numbers, required

#### Success Response (200)
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "userId": "user_1757350912_8004796b44e0429",
      "email": "user@example.com",
      "username": "username123",
      "createdAt": "2025-09-08T17:01:52.011263Z",
      "isActive": true
    }
  },
  "error": null
}
```

#### Error Responses
- `400` - Validation errors:
  ```json
  {
    "success": false,
    "error": {
      "code": "REGISTRATION_ERROR",
      "message": "Invalid email format"
    }
  }
  ```
- `400` - User already exists:
  ```json
  {
    "success": false,
    "error": {
      "code": "REGISTRATION_ERROR",
      "message": "User with this email already exists"
    }
  }
  ```

---

### 2. User Login

**POST** `/auth/login`

Đăng nhập user.

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Success Response (200)
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "userId": "user_1757350912_8004796b44e0429",
      "email": "user@example.com",
      "username": "username123",
      "createdAt": "2025-09-08T17:01:52.011263Z",
      "isActive": true
    },
    "accessToken": "eyJ0eXAiOiJKV1QiLCJraWQiOiJkdW1teSIsImFsZyI6IlJTMjU2In0...",
    "refreshToken": "ddc65f38-c806-41c7-840a-98a5a5d7f604",
    "idToken": "eyJ0eXAiOiJKV1QiLCJraWQiOiJkdW1teSIsImFsZyI6IlJTMjU2In0..."
  },
  "error": null
}
```

#### Error Responses
- `400` - Invalid credentials:
  ```json
  {
    "success": false,
    "error": {
      "code": "LOGIN_ERROR",
      "message": "Invalid credentials"
    }
  }
  ```
- `400` - User not found:
  ```json
  {
    "success": false,
    "error": {
      "code": "LOGIN_ERROR",
      "message": "User not found"
    }
  }
  ```

---

### 3. User Logout

**POST** `/auth/logout`

Đăng xuất user.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body
```json
{}
```

#### Success Response (200)
```json
{
  "success": true,
  "message": "Logout successful",
  "data": null,
  "error": null
}
```

#### Error Responses
- `401` - Missing or invalid token:
  ```json
  {
    "success": false,
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Invalid or missing authorization token"
    }
  }
  ```

---

### 4. Forgot Password

**POST** `/auth/forgot-password`

Gửi email reset password.

#### Request Body
```json
{
  "email": "user@example.com"
}
```

#### Success Response (200)
```json
{
  "success": true,
  "message": "Password reset code sent to email",
  "data": null,
  "error": null
}
```

#### Error Responses
- `400` - User not found:
  ```json
  {
    "success": false,
    "error": {
      "code": "FORGOT_PASSWORD_ERROR",
      "message": "User not found"
    }
  }
  ```

---

### 5. Reset Password

**POST** `/auth/reset-password`

Reset password với confirmation code.

#### Request Body
```json
{
  "email": "user@example.com",
  "confirmationCode": "123456",
  "newPassword": "NewSecurePass123"
}
```

#### Validation Rules
- **newPassword**: Minimum 8 characters, must contain uppercase, lowercase, and numbers, required

#### Success Response (200)
```json
{
  "success": true,
  "message": "Password reset successful",
  "data": null,
  "error": null
}
```

#### Error Responses
- `400` - Invalid confirmation code:
  ```json
  {
    "success": false,
    "error": {
      "code": "RESET_PASSWORD_ERROR",
      "message": "Invalid confirmation code"
    }
  }
  ```
- `400` - Expired code:
  ```json
  {
    "success": false,
    "error": {
      "code": "RESET_PASSWORD_ERROR",
      "message": "Confirmation code has expired"
    }
  }
  ```

---

## CORS Support

API hỗ trợ CORS cho tất cả origins. Preflight OPTIONS requests được hỗ trợ:

**OPTIONS** `/auth/*`

#### Response Headers
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## Error Codes Reference

| Code | Description |
|------|-------------|
| `REGISTRATION_ERROR` | User registration failed |
| `LOGIN_ERROR` | User login failed |
| `UNAUTHORIZED` | Invalid or missing authentication |
| `FORGOT_PASSWORD_ERROR` | Forgot password operation failed |
| `RESET_PASSWORD_ERROR` | Password reset operation failed |
| `NOT_FOUND` | Endpoint not found |
| `INTERNAL_ERROR` | Internal server error |

---

## Rate Limiting

Hiện tại API chưa implement rate limiting, nhưng khuyến nghị:
- Registration: 5 requests per minute per IP
- Login: 10 requests per minute per IP
- Password reset: 3 requests per minute per email

---

## Security Notes

1. **Password Requirements**: Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số
2. **Token Expiration**: Access tokens có thời hạn sử dụng (thường 1 giờ)
3. **HTTPS Only**: Production API chỉ hỗ trợ HTTPS
4. **Input Validation**: Tất cả input đều được validate nghiêm ngặt
5. **Error Messages**: Error messages không tiết lộ thông tin nhạy cảm

---

## Testing

### Test với cURL

#### Registration
```bash
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123"
  }'
```

#### Login
```bash
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

#### Logout
```bash
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/logout \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{}'
```

---

## Changelog

### v1.0.0 (2025-09-08)
- Initial API release
- User registration and login
- Password reset functionality
- JWT token authentication
- CORS support
