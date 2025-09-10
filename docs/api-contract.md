# Reddit Clone Backend - API Contract

## Base URL
```
Production: https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod
Local Development: http://localhost:5000
```

## Architecture Overview
API được chia thành 4 Lambda functions riêng biệt:
- **AuthLambda**: Xử lý Authentication và Posts APIs
- **CommentsLambda**: Xử lý Comments APIs
- **SubredditsLambda**: Xử lý Subreddit APIs
- **FeedsLambda**: Xử lý News Feed APIs

## Authentication
API sử dụng JWT tokens cho authentication. Tất cả protected endpoints yêu cầu `Authorization` header:
```
Authorization: Bearer <access_token>
```

**Note**: Hiện tại API sử dụng `X-User-ID` header cho testing purposes:
```
X-User-ID: user_1757485758_cde044d0
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

Đăng nhập user. Hỗ trợ đăng nhập bằng email hoặc username.

#### Request Body Options

**Option 1: Login with Email**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Option 2: Login with Username**
```json
{
  "username": "username123",
  "password": "SecurePass123"
}
```

**Option 3: Login with Both (Email takes priority)**
```json
{
  "email": "user@example.com",
  "username": "username123",
  "password": "SecurePass123"
}
```

#### Validation Rules
- **email**: Valid email format, optional (if username not provided)
- **username**: 3-20 characters, optional (if email not provided)
- **password**: Required
- **Note**: At least one of email or username must be provided

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
- `400` - Validation error (missing credentials):
  ```json
  {
    "success": false,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Validation failed",
      "additional_data": {
        "validation_errors": [
          "Either username or email must be provided"
        ]
      }
    }
  }
  ```
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
*Handled by AuthLambda*

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

## Comments Endpoints
*Handled by CommentsLambda*

### 1. Create Comment

**POST** `/comments/create`

Tạo comment mới.

#### Headers
```
Content-Type: application/json
X-User-ID: user_1234567890_abcdef12  # For testing purposes
```

#### Request Body
```json
{
  "post_id": "post_1757473451_1f984949",
  "content": "This is a great post! Thanks for sharing.",
  "parent_id": null,
  "comment_type": "comment",
  "is_nsfw": false,
  "is_spoiler": false,
  "flair": "Discussion",
  "tags": ["feedback", "positive"]
}
```

#### Request Fields
- **post_id** (required): ID của post
- **content** (required): Nội dung comment (1-10000 ký tự)
- **parent_id** (optional): ID của parent comment (cho replies)
- **comment_type** (optional): Loại comment ("comment" hoặc "reply")
- **is_nsfw** (optional): Comment có NSFW không (default: false)
- **is_spoiler** (optional): Comment có spoiler không (default: false)
- **flair** (optional): Flair của comment (max 50 ký tự)
- **tags** (optional): Tags của comment (max 5 tags, mỗi tag max 30 ký tự)

#### Success Response (201)
```json
{
  "success": true,
  "message": "Comment created successfully",
  "data": {
    "comment": {
      "comment_id": "comment_1757473451_1f984949",
      "post_id": "post_1757473451_1f984949",
      "author_id": "user_1757432106_d66ab80f40704b1",
      "parent_id": null,
      "content": "This is a great post! Thanks for sharing.",
      "comment_type": "comment",
      "score": 0,
      "upvotes": 0,
      "downvotes": 0,
      "reply_count": 0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "is_deleted": false,
      "is_edited": false,
      "is_locked": false,
      "is_sticky": false,
      "is_nsfw": false,
      "is_spoiler": false,
      "flair": "Discussion",
      "tags": ["feedback", "positive"],
      "awards": [],
      "user_vote": null,
      "replies": []
    }
  }
}
```

#### Error Responses
- `400` - Validation error:
  ```json
  {
    "success": false,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Content cannot be empty"
    }
  }
  ```

---

### 2. Get Comments

**GET** `/comments?post_id={post_id}&parent_comment_id={parent_comment_id}&sort_by={sort_by}&sort_order={sort_order}&limit={limit}&offset={offset}`

Lấy danh sách comments. Có thể filter theo post_id hoặc lấy tất cả comments.

#### Query Parameters
- **post_id** (optional): ID của post để filter comments
- **parent_comment_id** (optional): ID của parent comment (để lấy replies)
- **author_id** (optional): ID của author để filter comments
- **sort_by** (optional): Sắp xếp theo ("created_at", "score") (default: "created_at")
- **sort_order** (optional): Thứ tự sắp xếp ("asc", "desc") (default: "desc")
- **limit** (optional): Số lượng comments (1-100, default: 20)
- **offset** (optional): Số comments bỏ qua (default: 0)

#### Success Response (200)
```json
{
  "success": true,
  "message": "Comments retrieved successfully",
  "data": {
    "comments": [
      {
        "comment_id": "comment_1757509982_351caa27",
        "content": "Updated comment content",
        "author_id": "f9ba158c-b051-703e-da3e-5d3ed8522bb5",
        "author_username": "Unknown",
        "post_id": "post_1757508287_f8e2cbd7",
        "parent_comment_id": null,
        "comment_type": "comment",
        "media_urls": [],
        "score": 0,
        "upvotes": 0,
        "downvotes": 0,
        "reply_count": 0,
        "created_at": "2025-09-10T13:13:02.967836+00:00",
        "updated_at": "2025-09-10T13:57:24.760528+00:00",
        "is_deleted": false,
        "is_edited": true,
        "is_nsfw": false,
        "is_spoiler": true,
        "flair": "Updated Flair",
        "tags": ["updated", "feedback"],
        "awards": []
      }
    ],
    "total_count": 5,
    "has_more": false,
    "next_offset": null
  }
}
```

---

### 3. Get Comments by Post ID

**GET** `/posts/{post_id}/comments?parent_comment_id={parent_comment_id}&sort_by={sort_by}&sort_order={sort_order}&limit={limit}&offset={offset}`

Lấy danh sách comments của một post cụ thể.

#### Path Parameters
- **post_id** (required): ID của post

#### Query Parameters
- **parent_comment_id** (optional): ID của parent comment (để lấy replies)
- **author_id** (optional): ID của author để filter comments
- **sort_by** (optional): Sắp xếp theo ("created_at", "score") (default: "created_at")
- **sort_order** (optional): Thứ tự sắp xếp ("asc", "desc") (default: "desc")
- **limit** (optional): Số lượng comments (1-100, default: 20)
- **offset** (optional): Số comments bỏ qua (default: 0)

#### Success Response (200)
```json
{
  "success": true,
  "message": "Comments retrieved successfully",
  "data": {
    "comments": [
      {
        "comment_id": "comment_1757509982_351caa27",
        "content": "Updated comment content",
        "author_id": "f9ba158c-b051-703e-da3e-5d3ed8522bb5",
        "author_username": "Unknown",
        "post_id": "post_1757508287_f8e2cbd7",
        "parent_comment_id": null,
        "comment_type": "comment",
        "media_urls": [],
        "score": 0,
        "upvotes": 0,
        "downvotes": 0,
        "reply_count": 0,
        "created_at": "2025-09-10T13:13:02.967836+00:00",
        "updated_at": "2025-09-10T13:57:24.760528+00:00",
        "is_deleted": false,
        "is_edited": true,
        "is_nsfw": false,
        "is_spoiler": true,
        "flair": "Updated Flair",
        "tags": ["updated", "feedback"],
        "awards": []
      }
    ],
    "count": 5,
    "post_id": "post_1757508287_f8e2cbd7"
  }
}
```

---

### 4. Get Comment by ID

**GET** `/comments/{comment_id}`

Lấy chi tiết một comment.

#### Path Parameters
- **comment_id**: ID của comment

#### Success Response (200)
```json
{
  "success": true,
  "message": "Comment retrieved successfully",
  "data": {
    "comment": {
      "comment_id": "comment_1757473451_1f984949",
      "post_id": "post_1757473451_1f984949",
      "author_id": "user_1757432106_d66ab80f40704b1",
      "parent_id": null,
      "content": "This is a great post! Thanks for sharing.",
      "comment_type": "comment",
      "score": 15,
      "upvotes": 18,
      "downvotes": 3,
      "reply_count": 2,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "is_deleted": false,
      "is_edited": false,
      "is_locked": false,
      "is_sticky": false,
      "is_nsfw": false,
      "is_spoiler": false,
      "flair": "Discussion",
      "tags": ["feedback", "positive"],
      "awards": [],
      "user_vote": "upvote",
      "replies": []
    }
  }
}
```

#### Error Responses
- `404` - Comment not found:
  ```json
  {
    "success": false,
    "error": {
      "code": "COMMENT_NOT_FOUND",
      "message": "Comment not found"
    }
  }
  ```

---

### 4. Update Comment

**PUT** `/comments/{comment_id}`

Cập nhật comment (chỉ author mới có thể cập nhật).

#### Headers
```
Content-Type: application/json
X-User-ID: user_1234567890_abcdef12  # Must be the comment author
```

#### Path Parameters
- **comment_id**: ID của comment cần cập nhật

#### Request Body
```json
{
  "content": "Updated comment content",
  "is_nsfw": false,
  "is_spoiler": true,
  "flair": "Updated Flair",
  "tags": ["updated", "feedback"]
}
```

#### Request Fields
- **content** (optional): Nội dung comment mới (1-10000 ký tự)
- **is_nsfw** (optional): Comment có NSFW không
- **is_spoiler** (optional): Comment có spoiler không
- **flair** (optional): Flair của comment (max 50 ký tự)
- **tags** (optional): Tags của comment (max 5 tags, mỗi tag max 30 ký tự)

#### Success Response (200)
```json
{
  "success": true,
  "message": "Comment updated successfully",
  "data": {
    "comment": {
      "comment_id": "comment_1757473451_1f984949",
      "post_id": "post_1757473451_1f984949",
      "author_id": "user_1757432106_d66ab80f40704b1",
      "parent_id": null,
      "content": "Updated comment content",
      "comment_type": "comment",
      "score": 15,
      "upvotes": 18,
      "downvotes": 3,
      "reply_count": 2,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:35:00Z",
      "is_deleted": false,
      "is_edited": true,
      "is_locked": false,
      "is_sticky": false,
      "is_nsfw": false,
      "is_spoiler": true,
      "flair": "Updated Flair",
      "tags": ["updated", "feedback"],
      "awards": [],
      "user_vote": "upvote",
      "replies": []
    }
  }
}
```

#### Error Responses
- `403` - Access denied:
  ```json
  {
    "success": false,
    "error": {
      "code": "COMMENT_ACCESS_DENIED",
      "message": "Access denied"
    }
  }
  ```

---

### 5. Delete Comment

**DELETE** `/comments/{comment_id}`

Xóa comment (soft delete, chỉ author mới có thể xóa).

#### Headers
```
X-User-ID: user_1234567890_abcdef12  # Must be the comment author
```

#### Path Parameters
- **comment_id**: ID của comment cần xóa

#### Success Response (200)
```json
{
  "success": true,
  "message": "Comment deleted successfully"
}
```

#### Error Responses
- `403` - Access denied:
  ```json
  {
    "success": false,
    "error": {
      "code": "COMMENT_ACCESS_DENIED",
      "message": "Access denied"
    }
  }
  ```

---

### 6. Vote Comment

**POST** `/comments/{comment_id}/vote`

Vote cho comment (upvote, downvote, hoặc remove vote).

#### Headers
```
Content-Type: application/json
X-User-ID: user_1234567890_abcdef12
```

#### Path Parameters
- **comment_id**: ID của comment cần vote

#### Request Body
```json
{
  "vote_type": "upvote"
}
```

#### Request Fields
- **vote_type** (required): Loại vote ("upvote", "downvote", "remove")

#### Success Response (200)
```json
{
  "success": true,
  "message": "Vote processed successfully",
  "data": {
    "stats": {
      "comment_id": "comment_1757473451_1f984949",
      "score": 16,
      "upvotes": 19,
      "downvotes": 3,
      "reply_count": 2
    }
  }
}
```

#### Error Responses
- `400` - Validation error:
  ```json
  {
    "success": false,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Invalid vote type"
    }
  }
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
| `COMMENT_NOT_FOUND` | Comment not found |
| `COMMENT_ACCESS_DENIED` | Access denied to comment |
| `COMMENT_VALIDATION_ERROR` | Invalid comment data |
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

#### Login with Email
```bash
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

#### Login with Username
```bash
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "TestPass123"
  }'
```

#### Login Validation Error (No Credentials)
```bash
curl -X POST https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{
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

### v2.3.0 (2025-09-10)
- **Fixed Comment API**: Resolved issues with GET comments endpoints
- **GSI Optimization**: Implemented proper GSI usage instead of scan operations for better performance
- **Enhanced Filtering**: Improved filter expressions to handle missing fields (isDeleted, parentCommentId)
- **New Endpoint**: Added dedicated `/posts/{post_id}/comments` endpoint for better API organization
- **Better Error Handling**: Fixed null value handling in DynamoDB queries
- **Performance Improvement**: Comments retrieval now uses PostIndex GSI for faster queries

### v2.2.0 (2025-09-10)
- **Flexible Login**: Support both email and username for login
- **Enhanced Validation**: Improved validation error messages with detailed field information
- **Login Options**: Multiple login methods (email-only, username-only, both)
- **Better Error Handling**: Clear validation error responses for missing credentials
- **Updated Documentation**: Comprehensive API contract and Postman collection updates

### v2.1.0 (2025-09-10)
- **Comments System**: Complete CRUD operations for comments
- **Comment Types**: Support for comments and replies
- **Comment Voting**: Upvote, downvote, and remove vote functionality
- **Comment Filtering**: Advanced filtering and sorting options
- **Comment Pagination**: Cursor-based pagination for comments
- **Database**: Added Comments DynamoDB table with GSI indexes
- **API Gateway**: Added Comments endpoints with proper CORS configuration
- **Error Handling**: Added Comment-specific error codes

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

---

## Subreddit APIs

### 1. Create Subreddit
**POST** `/subreddits/create`

Tạo subreddit mới.

**Headers:**
```
Content-Type: application/json
X-User-ID: <user_id>
```

**Request Body:**
```json
{
  "name": "programming",
  "display_name": "Programming",
  "description": "Discussion about programming languages and frameworks",
  "rules": ["Be respectful", "No spam", "Use descriptive titles"],
  "primary_color": "#FF4500",
  "secondary_color": "#FFFFFF",
  "language": "en",
  "country": "US"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Subreddit created successfully",
  "data": {
    "subreddit_id": "subreddit_1757518063_01b8625d",
    "name": "programming",
    "display_name": "Programming",
    "description": "Discussion about programming languages and frameworks",
    "rules": ["Be respectful", "No spam", "Use descriptive titles"],
    "owner_id": "f9ba158c-b051-703e-da3e-5d3ed8522bb5",
    "moderators": ["f9ba158c-b051-703e-da3e-5d3ed8522bb5"],
    "subscriber_count": 1,
    "post_count": 0,
    "created_at": "2025-09-10T15:27:43.750119+00:00",
    "updated_at": "2025-09-10T15:27:43.750119+00:00",
    "is_private": false,
    "is_nsfw": false,
    "is_restricted": false,
    "banner_image": null,
    "icon_image": null,
    "primary_color": "#FF4500",
    "secondary_color": "#FFFFFF",
    "language": "en",
    "country": "US",
    "is_subscribed": null,
    "user_role": null
  }
}
```

### 2. Get Subreddits
**GET** `/subreddits`

Lấy danh sách subreddits.

**Query Parameters:**
- `sort` (optional): `new` | `popular` | `trending` (default: `new`)
- `search` (optional): Tìm kiếm theo tên hoặc mô tả
- `limit` (optional): Số lượng kết quả (default: 20)
- `offset` (optional): Vị trí bắt đầu (default: 0)

**Response:**
```json
{
  "success": true,
  "message": "Subreddits retrieved successfully",
  "data": {
    "subreddits": [
      {
        "subreddit_id": "subreddit_1757518063_01b8625d",
        "name": "programming",
        "display_name": "Programming",
        "description": "Discussion about programming languages and frameworks",
        "rules": ["Be respectful", "No spam", "Use descriptive titles"],
        "owner_id": "f9ba158c-b051-703e-da3e-5d3ed8522bb5",
        "moderators": ["f9ba158c-b051-703e-da3e-5d3ed8522bb5"],
        "subscriber_count": 2,
        "post_count": 0,
        "created_at": "2025-09-10T15:27:43.750119+00:00",
        "updated_at": "2025-09-10T15:27:43.750119+00:00",
        "is_private": false,
        "is_nsfw": false,
        "is_restricted": false,
        "banner_image": null,
        "icon_image": null,
        "primary_color": "#FF4500",
        "secondary_color": "#FFFFFF",
        "language": "en",
        "country": "US",
        "is_subscribed": true,
        "user_role": "subscriber"
      }
    ],
    "total_count": 1,
    "has_more": false,
    "next_offset": null
  }
}
```

### 3. Get Subreddit by ID
**GET** `/subreddits/{subreddit_id}`

Lấy thông tin chi tiết của subreddit.

**Headers:**
```
X-User-ID: <user_id> (optional)
```

**Response:**
```json
{
  "success": true,
  "message": "Subreddit retrieved successfully",
  "data": {
    "subreddit_id": "subreddit_1757518063_01b8625d",
    "name": "programming",
    "display_name": "Programming",
    "description": "Discussion about programming languages and frameworks",
    "rules": ["Be respectful", "No spam", "Use descriptive titles"],
    "owner_id": "f9ba158c-b051-703e-da3e-5d3ed8522bb5",
    "moderators": ["f9ba158c-b051-703e-da3e-5d3ed8522bb5"],
    "subscriber_count": 2,
    "post_count": 0,
    "created_at": "2025-09-10T15:27:43.750119+00:00",
    "updated_at": "2025-09-10T15:27:43.750119+00:00",
    "is_private": false,
    "is_nsfw": false,
    "is_restricted": false,
    "banner_image": null,
    "icon_image": null,
    "primary_color": "#FF4500",
    "secondary_color": "#FFFFFF",
    "language": "en",
    "country": "US",
    "is_subscribed": true,
    "user_role": "subscriber"
  }
}
```

### 4. Get Subreddit by Name
**GET** `/subreddits/name/{name}`

Lấy thông tin subreddit theo tên.

**Headers:**
```
X-User-ID: <user_id> (optional)
```

**Response:**
```json
{
  "success": true,
  "message": "Subreddit retrieved successfully",
  "data": {
    "subreddit_id": "subreddit_1757518063_01b8625d",
    "name": "programming",
    "display_name": "Programming",
    "description": "Discussion about programming languages and frameworks",
    "rules": ["Be respectful", "No spam", "Use descriptive titles"],
    "owner_id": "f9ba158c-b051-703e-da3e-5d3ed8522bb5",
    "moderators": ["f9ba158c-b051-703e-da3e-5d3ed8522bb5"],
    "subscriber_count": 2,
    "post_count": 0,
    "created_at": "2025-09-10T15:27:43.750119+00:00",
    "updated_at": "2025-09-10T15:27:43.750119+00:00",
    "is_private": false,
    "is_nsfw": false,
    "is_restricted": false,
    "banner_image": null,
    "icon_image": null,
    "primary_color": "#FF4500",
    "secondary_color": "#FFFFFF",
    "language": "en",
    "country": "US",
    "is_subscribed": true,
    "user_role": "subscriber"
  }
}
```

### 5. Update Subreddit
**PUT** `/subreddits/{subreddit_id}`

Cập nhật thông tin subreddit (chỉ owner và moderators).

**Headers:**
```
Content-Type: application/json
X-User-ID: <user_id>
```

**Request Body:**
```json
{
  "display_name": "Programming Community",
  "description": "A community for programmers to discuss coding, frameworks, and best practices",
  "rules": ["Be respectful and civil", "No spam or self-promotion", "Use descriptive titles", "Follow Reddit guidelines"],
  "primary_color": "#FF6B35",
  "secondary_color": "#F7F7F7",
  "is_private": false,
  "is_nsfw": false,
  "is_restricted": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Subreddit updated successfully",
  "data": {
    "subreddit_id": "subreddit_1757518063_01b8625d",
    "name": "programming",
    "display_name": "Programming Community",
    "description": "A community for programmers to discuss coding, frameworks, and best practices",
    "rules": ["Be respectful and civil", "No spam or self-promotion", "Use descriptive titles", "Follow Reddit guidelines"],
    "owner_id": "f9ba158c-b051-703e-da3e-5d3ed8522bb5",
    "moderators": ["f9ba158c-b051-703e-da3e-5d3ed8522bb5"],
    "subscriber_count": 2,
    "post_count": 0,
    "created_at": "2025-09-10T15:27:43.750119+00:00",
    "updated_at": "2025-09-10T15:33:37.435788+00:00",
    "is_private": false,
    "is_nsfw": false,
    "is_restricted": false,
    "banner_image": null,
    "icon_image": null,
    "primary_color": "#FF6B35",
    "secondary_color": "#F7F7F7",
    "language": "en",
    "country": "US",
    "is_subscribed": true,
    "user_role": "subscriber"
  }
}
```

### 6. Join Subreddit
**POST** `/subreddits/{subreddit_id}/join`

Tham gia subreddit.

**Headers:**
```
Content-Type: application/json
X-User-ID: <user_id>
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully joined subreddit",
  "data": {
    "subscription_id": "sub_1757518530_a664d7ee",
    "user_id": "user_1757485758_cde044d0",
    "subreddit_id": "subreddit_1757518523_88a4c527",
    "role": "subscriber",
    "joined_at": "2025-09-10T15:35:30.9",
    "is_active": true
  }
}
```

### 7. Leave Subreddit
**POST** `/subreddits/{subreddit_id}/leave`

Rời khỏi subreddit (không áp dụng cho owner).

**Headers:**
```
Content-Type: application/json
X-User-ID: <user_id>
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully left subreddit"
}
```

### 8. Get Subreddit Posts
**GET** `/subreddits/{subreddit_id}/posts`

Lấy danh sách posts trong subreddit.

**Query Parameters:**
- `limit` (optional): Số lượng posts (default: 20)
- `offset` (optional): Vị trí bắt đầu (default: 0)
- `sort` (optional): `new` | `hot` | `top` (default: `new`)

**Response:**
```json
{
  "success": true,
  "message": "Subreddit posts retrieved successfully",
  "data": {
    "posts": [],
    "count": 0,
    "subreddit_id": "subreddit_1757518063_01b8625d",
    "has_more": false,
    "next_offset": null
  }
}
```

### 9. Add Moderator
**POST** `/subreddits/{subreddit_id}/moderators`

Thêm moderator cho subreddit (chỉ owner).

**Headers:**
```
Content-Type: application/json
X-User-ID: <user_id>
```

**Request Body:**
```json
{
  "user_id": "user_1757485758_cde044d0",
  "action": "add",
  "role": "moderator"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Moderator added successfully"
}
```

### 10. Remove Moderator
**DELETE** `/subreddits/{subreddit_id}/moderators/{user_id}`

Xóa moderator khỏi subreddit (chỉ owner).

**Headers:**
```
X-User-ID: <user_id>
```

**Response:**
```json
{
  "success": true,
  "message": "Moderator removed successfully"
}
```

### 11. Delete Subreddit
**DELETE** `/subreddits/{subreddit_id}`

Xóa subreddit (chỉ owner).

**Headers:**
```
X-User-ID: <user_id>
```

**Response:**
```json
{
  "success": true,
  "message": "Subreddit deleted successfully"
}
```

## Error Codes

### Subreddit-specific Error Codes
- `SUBREDDIT_NOT_FOUND`: Subreddit không tồn tại
- `SUBREDDIT_NAME_EXISTS`: Tên subreddit đã được sử dụng
- `INSUFFICIENT_PERMISSIONS`: Không có quyền thực hiện hành động
- `ALREADY_SUBSCRIBED`: User đã tham gia subreddit
- `NOT_SUBSCRIBED`: User chưa tham gia subreddit
- `OWNER_CANNOT_LEAVE`: Owner không thể rời khỏi subreddit của mình

---

## News Feed APIs

### GET /feeds
Lấy personalized news feed cho user.

**Headers:**
- `Authorization: Bearer <access_token>`
- `X-User-ID: <user_id>`

**Query Parameters:**
- `limit` (optional): Số lượng items trả về (default: 20, max: 100)
- `offset` (optional): Offset cho pagination (default: 0)
- `sort` (optional): Loại sắp xếp - `new`, `hot`, `top`, `trending` (default: `new`)
- `includeNSFW` (optional): Bao gồm nội dung NSFW (default: false)
- `includeSpoilers` (optional): Bao gồm nội dung spoiler (default: false)
- `subredditId` (optional): Lọc theo subreddit ID
- `authorId` (optional): Lọc theo author ID

**Response:**
```json
{
  "success": true,
  "data": {
    "feeds": [
      {
        "feedId": "feed_user123_2025-09-10T10:30:00Z_post456",
        "postId": "post456",
        "subredditId": "subreddit789",
        "authorId": "user456",
        "postTitle": "Amazing post title",
        "postContent": "Post content preview...",
        "postImageUrl": "https://example.com/image.jpg",
        "subredditName": "r/programming",
        "authorName": "john_doe",
        "upvotes": 150,
        "downvotes": 5,
        "commentsCount": 23,
        "isPinned": false,
        "isNSFW": false,
        "isSpoiler": false,
        "tags": ["programming", "javascript"],
        "createdAt": "2025-09-10T10:30:00Z",
        "postScore": 145
      }
    ],
    "pagination": {
      "limit": 20,
      "offset": 0,
      "total": 150,
      "hasMore": true,
      "nextOffset": 20
    },
    "metadata": {
      "generatedAt": "2025-09-10T10:35:00Z",
      "sortType": "new",
      "cacheHit": false
    }
  },
  "message": "Feed retrieved successfully"
}
```

### POST /feeds/refresh
Refresh user feed sau khi có thay đổi.

**Headers:**
- `Authorization: Bearer <access_token>`
- `X-User-ID: <user_id>`

**Request Body:**
```json
{
  "reason": "subreddit_joined",
  "subredditId": "subreddit789",
  "userId": "user456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Feed refreshed successfully",
    "newItemsCount": 15,
    "refreshedAt": "2025-09-10T10:35:00Z"
  },
  "message": "Feed refreshed successfully"
}
```

### GET /feeds/stats
Lấy thống kê feed của user.

**Headers:**
- `Authorization: Bearer <access_token>`
- `X-User-ID: <user_id>`

**Response:**
```json
{
  "success": true,
  "data": {
    "totalSubscriptions": 25,
    "totalFollowing": 150,
    "feedItemsCount": 1250,
    "lastRefreshAt": "2025-09-10T10:30:00Z",
    "averageScore": 85.5,
    "topSubreddits": [
      {
        "subredditId": "subreddit789",
        "subredditName": "r/programming",
        "postCount": 45,
        "averageScore": 92.3
      }
    ],
    "topAuthors": [
      {
        "authorId": "user456",
        "authorName": "john_doe",
        "postCount": 12,
        "averageScore": 88.7
      }
    ]
  },
  "message": "Feed statistics retrieved successfully"
}
```

### Feed-specific Error Codes
- `FEED_GENERATION_FAILED`: Lỗi khi tạo feed
- `INVALID_SORT_TYPE`: Loại sắp xếp không hợp lệ
- `INVALID_FILTER_PARAMS`: Tham số lọc không hợp lệ
- `FEED_REFRESH_FAILED`: Lỗi khi refresh feed
- `STATS_RETRIEVAL_FAILED`: Lỗi khi lấy thống kê
- `CANNOT_JOIN_PRIVATE`: Không thể tham gia subreddit private mà không có lời mời
