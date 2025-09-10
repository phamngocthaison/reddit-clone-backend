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

## Posts Endpoints

### 1. Create Post

**POST** `/posts/create`

Tạo post mới.

#### Headers
```
Content-Type: application/json
X-User-ID: user_1234567890_abcdef12  # For testing purposes
```

#### Request Body
```json
{
  "title": "My First Post",
  "content": "This is the content of my post",
  "subreddit_id": "subreddit_123",
  "post_type": "text",
  "url": null,
  "media_urls": null,
  "is_nsfw": false,
  "is_spoiler": false,
  "flair": "Discussion",
  "tags": ["programming", "tutorial"]
}
```

#### Validation Rules
- **title**: 1-300 characters, required
- **content**: Max 40000 characters, required for text posts
- **subreddit_id**: Valid subreddit ID, required
- **post_type**: One of: "text", "link", "image", "video", "poll", default: "text"
- **url**: Valid URL, required for link posts
- **media_urls**: Array of URLs, for image/video posts
- **is_nsfw**: Boolean, default: false
- **is_spoiler**: Boolean, default: false
- **flair**: Max 100 characters, optional
- **tags**: Array of strings, optional

#### Success Response (201)
```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "post": {
      "post_id": "post_1757473451_1f984949",
      "title": "My First Post",
      "content": "This is the content of my post",
      "author_id": "user_1234567890_abcdef12",
      "author_username": "testuser123",
      "subreddit_id": "subreddit_123",
      "subreddit_name": "Test Subreddit",
      "post_type": "text",
      "url": null,
      "media_urls": null,
      "score": 0,
      "upvotes": 0,
      "downvotes": 0,
      "comment_count": 0,
      "view_count": 0,
      "created_at": "2025-09-10T03:04:11.075189+00:00",
      "updated_at": "2025-09-10T03:04:11.075189+00:00",
      "is_deleted": false,
      "is_locked": false,
      "is_sticky": false,
      "is_nsfw": false,
      "is_spoiler": false,
      "flair": "Discussion",
      "tags": ["programming", "tutorial"],
      "awards": null,
      "user_vote": null
    }
  }
}
```

#### Error Responses
- `400` - Validation errors:
  ```json
  {
    "success": false,
    "message": "Validation error",
    "error": {
      "code": "POST_VALIDATION_ERROR",
      "message": "Title is required for text posts"
    }
  }
  ```
- `403` - Access denied:
  ```json
  {
    "success": false,
    "message": "Access denied",
    "error": {
      "code": "POST_ACCESS_DENIED",
      "message": "Author not found"
    }
  }
  ```

---

### 2. Get Posts

**GET** `/posts`

Lấy danh sách posts với filtering và pagination.

#### Query Parameters
- **subreddit_id** (optional): Filter by subreddit
- **author_id** (optional): Filter by author
- **sort** (optional): Sort order - "hot", "new", "top", "rising", "controversial" (default: "hot")
- **time_filter** (optional): Time filter for top/controversial - "hour", "day", "week", "month", "year", "all" (default: "day")
- **limit** (optional): Number of posts (1-100, default: 25)
- **offset** (optional): Pagination offset (default: 0)
- **post_type** (optional): Filter by post type
- **is_nsfw** (optional): Filter by NSFW status

#### Example Request
```
GET /posts?subreddit_id=subreddit_123&sort=hot&limit=10&offset=0
```

#### Success Response (200)
```json
{
  "success": true,
  "message": "Posts retrieved successfully",
  "data": {
    "posts": [
      {
        "post_id": "post_1757473451_1f984949",
        "title": "My First Post",
        "content": "This is the content of my post",
        "author_id": "user_1234567890_abcdef12",
        "author_username": "testuser123",
        "subreddit_id": "subreddit_123",
        "subreddit_name": "Test Subreddit",
        "post_type": "text",
        "url": null,
        "media_urls": [],
        "score": 0,
        "upvotes": 0,
        "downvotes": 0,
        "comment_count": 0,
        "view_count": 0,
        "created_at": "2025-09-10T03:04:11.075189+00:00",
        "updated_at": "2025-09-10T03:04:11.075189+00:00",
        "is_deleted": false,
        "is_locked": false,
        "is_sticky": false,
        "is_nsfw": false,
        "is_spoiler": false,
        "flair": "Discussion",
        "tags": ["programming", "tutorial"],
        "awards": [],
        "user_vote": null
      }
    ],
    "total_count": 1,
    "has_more": false,
    "next_offset": null
  }
}
```

---

### 3. Get Post by ID

**GET** `/posts/{post_id}`

Lấy chi tiết một post theo ID.

#### Path Parameters
- **post_id**: ID của post cần lấy

#### Success Response (200)
```json
{
  "success": true,
  "message": "Post retrieved successfully",
  "data": {
    "post": {
      "post_id": "post_1757473451_1f984949",
      "title": "My First Post",
      "content": "This is the content of my post",
      "author_id": "user_1234567890_abcdef12",
      "author_username": "testuser123",
      "subreddit_id": "subreddit_123",
      "subreddit_name": "Test Subreddit",
      "post_type": "text",
      "url": null,
      "media_urls": [],
      "score": 0,
      "upvotes": 0,
      "downvotes": 0,
      "comment_count": 0,
      "view_count": 0,
      "created_at": "2025-09-10T03:04:11.075189+00:00",
      "updated_at": "2025-09-10T03:04:11.075189+00:00",
      "is_deleted": false,
      "is_locked": false,
      "is_sticky": false,
      "is_nsfw": false,
      "is_spoiler": false,
      "flair": "Discussion",
      "tags": ["programming", "tutorial"],
      "awards": [],
      "user_vote": null
    }
  }
}
```

#### Error Responses
- `404` - Post not found:
  ```json
  {
    "success": false,
    "message": "Post not found",
    "error": {
      "code": "POST_NOT_FOUND",
      "message": "Post not found"
    }
  }
  ```

---

### 4. Update Post

**PUT** `/posts/{post_id}`

Cập nhật post (chỉ author mới có thể cập nhật).

#### Headers
```
Content-Type: application/json
X-User-ID: user_1234567890_abcdef12  # Must be the post author
```

#### Path Parameters
- **post_id**: ID của post cần cập nhật

#### Request Body
```json
{
  "title": "Updated Post Title",
  "content": "Updated content",
  "is_nsfw": false,
  "is_spoiler": true,
  "flair": "Updated Flair",
  "tags": ["updated", "tags"]
}
```

#### Success Response (200)
```json
{
  "success": true,
  "message": "Post updated successfully",
  "data": {
    "post": {
      "post_id": "post_1757473451_1f984949",
      "title": "Updated Post Title",
      "content": "Updated content",
      "author_id": "user_1234567890_abcdef12",
      "author_username": "testuser123",
      "subreddit_id": "subreddit_123",
      "subreddit_name": "Test Subreddit",
      "post_type": "text",
      "url": null,
      "media_urls": [],
      "score": 0,
      "upvotes": 0,
      "downvotes": 0,
      "comment_count": 0,
      "view_count": 0,
      "created_at": "2025-09-10T03:04:11.075189+00:00",
      "updated_at": "2025-09-10T03:04:12.123456+00:00",
      "is_deleted": false,
      "is_locked": false,
      "is_sticky": false,
      "is_nsfw": false,
      "is_spoiler": true,
      "flair": "Updated Flair",
      "tags": ["updated", "tags"],
      "awards": [],
      "user_vote": null
    }
  }
}
```

#### Error Responses
- `403` - Access denied:
  ```json
  {
    "success": false,
    "message": "Access denied",
    "error": {
      "code": "POST_ACCESS_DENIED",
      "message": "Only the author can update this post"
    }
  }
  ```

---

### 5. Delete Post

**DELETE** `/posts/{post_id}`

Xóa post (soft delete, chỉ author mới có thể xóa).

#### Headers
```
X-User-ID: user_1234567890_abcdef12  # Must be the post author
```

#### Path Parameters
- **post_id**: ID của post cần xóa

#### Success Response (200)
```json
{
  "success": true,
  "message": "Post deleted successfully"
}
```

#### Error Responses
- `403` - Access denied:
  ```json
  {
    "success": false,
    "message": "Access denied",
    "error": {
      "code": "POST_ACCESS_DENIED",
      "message": "Only the author can delete this post"
    }
  }
  ```

---

### 6. Vote Post

**POST** `/posts/{post_id}/vote`

Vote cho post (upvote, downvote, hoặc remove vote).

#### Headers
```
Content-Type: application/json
X-User-ID: user_1234567890_abcdef12
```

#### Path Parameters
- **post_id**: ID của post cần vote

#### Request Body
```json
{
  "vote_type": "upvote"  // "upvote", "downvote", or "remove"
}
```

#### Success Response (200)
```json
{
  "success": true,
  "message": "Vote recorded successfully",
  "data": {
    "stats": {
      "post_id": "post_1757473451_1f984949",
      "score": 1,
      "upvotes": 1,
      "downvotes": 0,
      "comment_count": 0,
      "view_count": 0
    }
  }
}
```

#### Error Responses
- `400` - Invalid vote type:
  ```json
  {
    "success": false,
    "message": "Validation error",
    "error": {
      "code": "POST_VALIDATION_ERROR",
      "message": "Invalid vote type"
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
| `POST_NOT_FOUND` | Post not found |
| `POST_ACCESS_DENIED` | Access denied to post operation |
| `POST_VALIDATION_ERROR` | Post validation failed |
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

### v2.0.0 (2025-09-10)
- **Posts System**: Complete CRUD operations for posts
- **Post Types**: Support for text, link, image, video, and poll posts
- **Voting System**: Upvote, downvote, and remove vote functionality
- **Filtering & Sorting**: Advanced filtering by subreddit, author, type, and NSFW status
- **Pagination**: Support for limit/offset pagination
- **Post Attributes**: Tags, flair, NSFW/Spoiler flags
- **Database**: Added Posts and Subreddits DynamoDB tables with GSI indexes

### v1.0.0 (2025-09-08)
- Initial API release
- User registration and login
- Password reset functionality
- JWT token authentication
- CORS support
