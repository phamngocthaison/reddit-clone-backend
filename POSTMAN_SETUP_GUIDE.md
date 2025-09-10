# 🚀 Postman Setup Guide - Auto Bearer Token

## 📋 Tổng quan

Postman collection đã được cập nhật với tính năng **Auto Bearer Token** - tự động đăng nhập và lưu token để test các API endpoints.

## 🔧 Setup Instructions

### 1. **Tạo Environment trong Postman**

1. Mở Postman
2. Click **Environments** tab (bên trái)
3. Click **Create Environment**
4. Đặt tên: `Reddit Clone Backend`

### 2. **Thêm Environment Variables**

Trong environment vừa tạo, thêm các variables sau:

| Variable Name | Initial Value | Current Value |
|---------------|---------------|---------------|
| `base_url` | `https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod` | `https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod` |
| `test_email` | `test@example.com` | `test@example.com` |
| `test_password` | `TestPass123` | `TestPass123` |
| `access_token` | (để trống) | (sẽ được auto-populate) |

### 3. **Import Collection**

1. Click **Import** button
2. Chọn file `docs/postman-collection.json`
3. Click **Import**

### 4. **Select Environment**

1. Click dropdown environment ở góc trên bên phải
2. Chọn `Reddit Clone Backend`

## 🎯 Cách sử dụng

### **Tự động (Recommended)**

1. **Chạy bất kỳ request nào** - Collection sẽ tự động:
   - Kiểm tra xem có token không
   - Nếu không có, tự động login
   - Lưu token vào environment
   - Sử dụng token cho request

2. **Không cần setup gì thêm** - Chỉ cần chạy request!

### **Manual Login (Optional)**

1. Vào folder **Authentication (AuthLambda)**
2. Chạy request **User Login - Valid (Email)**
3. Token sẽ được tự động lưu
4. Tất cả requests khác sẽ sử dụng token này

## 🔍 Kiểm tra Auto-Login

### **Console Logs**
Mở **Console** trong Postman để xem logs:
- `No token found, attempting auto-login...`
- `Auto-login successful, token saved`
- `Token found: eyJhbGciOiJIUzI1NiIs...`

### **Environment Variables**
Kiểm tra trong **Environments** tab:
- `access_token` sẽ có giá trị sau khi login thành công

## 📚 Collection Structure

```
Reddit Clone Backend API v2.1.0
├── Authentication (AuthLambda)
│   ├── User Registration - Valid
│   ├── User Login - Valid (Email) ← Auto-saves token
│   ├── User Login - Valid (Username)
│   ├── User Login - Both Email and Username
│   ├── User Login - Validation Error
│   ├── User Login - Invalid Credentials
│   ├── User Logout
│   ├── Forgot Password
│   └── Reset Password
├── Posts (AuthLambda)
│   ├── Create Post - Text
│   ├── Create Post - Link
│   ├── Create Post - Invalid Data
│   ├── Get Posts - All
│   ├── Get Posts - With Filters
│   ├── Get Post by ID
│   ├── Update Post
│   ├── Vote Post - Upvote
│   ├── Vote Post - Downvote
│   ├── Delete Post
│   └── Delete Post - Access Denied
└── Comments (CommentsLambda)
    ├── Create Comment
    ├── Get Comments
    ├── Get Comment by ID
    ├── Update Comment
    ├── Vote Comment
    └── Delete Comment
```

## 🛠️ Troubleshooting

### **Auto-login không hoạt động**
1. Kiểm tra environment variables đã đúng chưa
2. Kiểm tra `base_url` có đúng không
3. Kiểm tra Console logs để xem lỗi

### **Token hết hạn**
1. Chạy lại bất kỳ request nào
2. Collection sẽ tự động login lại
3. Hoặc chạy manual login request

### **401 Unauthorized**
1. Kiểm tra `access_token` trong environment
2. Nếu trống, chạy login request
3. Nếu có token, có thể đã hết hạn - chạy lại request

## 🎉 Features

- ✅ **Auto-login**: Tự động login khi cần
- ✅ **Token Management**: Tự động lưu và sử dụng token
- ✅ **Environment Variables**: Dễ dàng thay đổi config
- ✅ **Comprehensive Tests**: Mỗi request có test cases
- ✅ **Error Handling**: Xử lý lỗi authentication
- ✅ **Flexible Login**: Hỗ trợ email hoặc username

## 📞 Support

Nếu có vấn đề gì, kiểm tra:
1. Console logs trong Postman
2. Environment variables
3. API response trong Tests tab
4. Network tab để xem request/response details
