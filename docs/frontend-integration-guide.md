# Frontend Integration Guide - Reddit Clone Backend

## Tổng quan

Hướng dẫn này sẽ giúp Frontend developers tích hợp với Reddit Clone Backend API một cách hiệu quả và an toàn.

## Cấu hình cơ bản

### Base URL
```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod'
  : 'http://localhost:5000';
```

### Headers mặc định
```javascript
const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};
```

---

## 1. Authentication Service (JavaScript/TypeScript)

### 1.1 AuthService Class

```typescript
// services/AuthService.ts
interface User {
  userId: string;
  email: string;
  username: string;
  createdAt: string;
  isActive: boolean;
}

interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  idToken: string;
}

interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

class AuthService {
  private baseURL: string;
  private accessToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.accessToken = localStorage.getItem('accessToken');
  }

  // Helper method để gọi API
  private async apiCall<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      ...defaultHeaders,
      ...options.headers,
    };

    // Thêm Authorization header nếu có token
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error?.message || 'API call failed');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Đăng ký user mới
  async register(email: string, username: string, password: string): Promise<User> {
    const response = await this.apiCall<{ user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Registration failed');
    }

    return response.data.user;
  }

  // Đăng nhập
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await this.apiCall<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Login failed');
    }

    // Lưu token vào localStorage
    this.accessToken = response.data.accessToken;
    localStorage.setItem('accessToken', response.data.accessToken);
    localStorage.setItem('refreshToken', response.data.refreshToken);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  }

  // Đăng xuất
  async logout(): Promise<void> {
    try {
      await this.apiCall('/auth/logout', {
        method: 'POST',
        body: JSON.stringify({}),
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Xóa token khỏi localStorage
      this.accessToken = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    }
  }

  // Quên mật khẩu
  async forgotPassword(email: string): Promise<void> {
    const response = await this.apiCall('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });

    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to send reset email');
    }
  }

  // Reset mật khẩu
  async resetPassword(
    email: string, 
    confirmationCode: string, 
    newPassword: string
  ): Promise<void> {
    const response = await this.apiCall('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email, confirmationCode, newPassword }),
    });

    if (!response.success) {
      throw new Error(response.error?.message || 'Password reset failed');
    }
  }

  // Kiểm tra user đã đăng nhập chưa
  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  // Lấy thông tin user hiện tại
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // Lấy access token
  getAccessToken(): string | null {
    return this.accessToken;
  }
}

export default AuthService;
```

### 1.2 Sử dụng AuthService

```typescript
// main.ts hoặc App.tsx
import AuthService from './services/AuthService';

const authService = new AuthService(API_BASE_URL);

// Sử dụng trong component
const handleRegister = async (email: string, username: string, password: string) => {
  try {
    const user = await authService.register(email, username, password);
    console.log('User registered:', user);
    // Redirect to login page hoặc show success message
  } catch (error) {
    console.error('Registration failed:', error.message);
    // Show error message to user
  }
};

const handleLogin = async (email: string, password: string) => {
  try {
    const loginData = await authService.login(email, password);
    console.log('Login successful:', loginData.user);
    // Redirect to dashboard hoặc update UI
  } catch (error) {
    console.error('Login failed:', error.message);
    // Show error message to user
  }
};
```

---

## 2. React Integration Examples

### 2.1 Auth Context

```typescript
// contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import AuthService from '../services/AuthService';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (email: string, code: string, newPassword: string) => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const authService = new AuthService(API_BASE_URL);

  useEffect(() => {
    // Kiểm tra user đã đăng nhập chưa khi app khởi động
    const currentUser = authService.getCurrentUser();
    if (currentUser && authService.isAuthenticated()) {
      setUser(currentUser);
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const loginData = await authService.login(email, password);
      setUser(loginData.user);
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, username: string, password: string) => {
    try {
      const user = await authService.register(email, username, password);
      // Sau khi đăng ký thành công, tự động đăng nhập
      await login(email, password);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const forgotPassword = async (email: string) => {
    await authService.forgotPassword(email);
  };

  const resetPassword = async (email: string, code: string, newPassword: string) => {
    await authService.resetPassword(email, code, newPassword);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 2.2 Login Component

```typescript
// components/LoginForm.tsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      // Redirect sẽ được xử lý trong AuthProvider
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <h2>Đăng nhập</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="password">Mật khẩu:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
      </button>
    </form>
  );
};

export default LoginForm;
```

### 2.3 Registration Component

```typescript
// components/RegisterForm.tsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const RegisterForm: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Mật khẩu phải có ít nhất 8 ký tự');
      return false;
    }
    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      setError('Mật khẩu phải chứa chữ hoa, chữ thường và số');
      return false;
    }
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(formData.username)) {
      setError('Tên người dùng phải có 3-20 ký tự, chỉ chữ, số và dấu gạch dưới');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setLoading(true);

    try {
      await register(formData.email, formData.username, formData.password);
      // Redirect sẽ được xử lý trong AuthProvider
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      <h2>Đăng ký tài khoản</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="username">Tên người dùng:</label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="password">Mật khẩu:</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="confirmPassword">Xác nhận mật khẩu:</label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Đang đăng ký...' : 'Đăng ký'}
      </button>
    </form>
  );
};

export default RegisterForm;
```

---

## 3. Vue.js Integration Examples

### 3.1 Auth Store (Pinia)

```typescript
// stores/auth.ts
import { defineStore } from 'pinia';
import AuthService from '../services/AuthService';

interface User {
  userId: string;
  email: string;
  username: string;
  createdAt: string;
  isActive: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
  },

  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      this.error = null;

      try {
        const authService = new AuthService(API_BASE_URL);
        const loginData = await authService.login(email, password);
        this.user = loginData.user;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async register(email: string, username: string, password: string) {
      this.loading = true;
      this.error = null;

      try {
        const authService = new AuthService(API_BASE_URL);
        const user = await authService.register(email, username, password);
        // Auto login after registration
        await this.login(email, password);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        const authService = new AuthService(API_BASE_URL);
        await authService.logout();
        this.user = null;
      } catch (error) {
        console.error('Logout error:', error);
      }
    },

    async forgotPassword(email: string) {
      this.loading = true;
      this.error = null;

      try {
        const authService = new AuthService(API_BASE_URL);
        await authService.forgotPassword(email);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async resetPassword(email: string, code: string, newPassword: string) {
      this.loading = true;
      this.error = null;

      try {
        const authService = new AuthService(API_BASE_URL);
        await authService.resetPassword(email, code, newPassword);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
```

### 3.2 Login Component (Vue)

```vue
<!-- components/LoginForm.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="login-form">
    <h2>Đăng nhập</h2>
    
    <div v-if="error" class="error-message">{{ error }}</div>
    
    <div class="form-group">
      <label for="email">Email:</label>
      <input
        type="email"
        id="email"
        v-model="email"
        required
      />
    </div>
    
    <div class="form-group">
      <label for="password">Mật khẩu:</label>
      <input
        type="password"
        id="password"
        v-model="password"
        required
      />
    </div>
    
    <button type="submit" :disabled="loading">
      {{ loading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');

const handleSubmit = async () => {
  try {
    await authStore.login(email.value, password.value);
    // Redirect to dashboard
  } catch (error) {
    // Error is handled in store
  }
};
</script>
```

---

## 4. Error Handling Best Practices

### 4.1 Global Error Handler

```typescript
// utils/errorHandler.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const handleApiError = (error: any): ApiError => {
  if (error instanceof ApiError) {
    return error;
  }

  // Parse error from API response
  if (error.response?.data?.error) {
    const { code, message } = error.response.data.error;
    return new ApiError(message, code, error.response.status);
  }

  // Network or other errors
  return new ApiError(
    error.message || 'An unexpected error occurred',
    'UNKNOWN_ERROR',
    500
  );
};

// Usage in components
const handleApiCall = async () => {
  try {
    await someApiCall();
  } catch (error) {
    const apiError = handleApiError(error);
    
    switch (apiError.code) {
      case 'REGISTRATION_ERROR':
        showError('Đăng ký thất bại: ' + apiError.message);
        break;
      case 'LOGIN_ERROR':
        showError('Đăng nhập thất bại: ' + apiError.message);
        break;
      case 'UNAUTHORIZED':
        // Redirect to login
        router.push('/login');
        break;
      default:
        showError('Có lỗi xảy ra: ' + apiError.message);
    }
  }
};
```

### 4.2 Retry Logic

```typescript
// utils/retry.ts
export const retryApiCall = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx)
      if (error.statusCode >= 400 && error.statusCode < 500) {
        throw error;
      }
      
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }

  throw lastError;
};

// Usage
const loginWithRetry = async (email: string, password: string) => {
  return retryApiCall(() => authService.login(email, password));
};
```

---

## 5. Security Considerations

### 5.1 Token Management

```typescript
// utils/tokenManager.ts
class TokenManager {
  private static instance: TokenManager;
  private refreshPromise: Promise<string> | null = null;

  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager();
    }
    return TokenManager.instance;
  }

  // Kiểm tra token có hết hạn không
  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }

  // Refresh token
  async refreshAccessToken(): Promise<string> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.performRefresh();
    try {
      const newToken = await this.refreshPromise;
      return newToken;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async performRefresh(): Promise<string> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    // Call refresh endpoint
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    localStorage.setItem('accessToken', data.accessToken);
    return data.accessToken;
  }
}

export default TokenManager;
```

### 5.2 Request Interceptor

```typescript
// utils/requestInterceptor.ts
import TokenManager from './tokenManager';

const tokenManager = TokenManager.getInstance();

export const setupRequestInterceptor = () => {
  // Intercept fetch requests
  const originalFetch = window.fetch;
  
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input.toString();
    
    // Add auth header for API calls
    if (url.includes('/auth/') && !url.includes('/auth/register') && !url.includes('/auth/login')) {
      const token = localStorage.getItem('accessToken');
      
      if (token) {
        // Check if token is expired
        if (tokenManager.isTokenExpired(token)) {
          try {
            const newToken = await tokenManager.refreshAccessToken();
            init = {
              ...init,
              headers: {
                ...init?.headers,
                'Authorization': `Bearer ${newToken}`,
              },
            };
          } catch (error) {
            // Redirect to login if refresh fails
            window.location.href = '/login';
            throw error;
          }
        } else {
          init = {
            ...init,
            headers: {
              ...init?.headers,
              'Authorization': `Bearer ${token}`,
            },
          };
        }
      }
    }
    
    return originalFetch(input, init);
  };
};
```

---

## 6. Testing

### 6.1 Unit Tests

```typescript
// __tests__/AuthService.test.ts
import AuthService from '../services/AuthService';

// Mock fetch
global.fetch = jest.fn();

describe('AuthService', () => {
  let authService: AuthService;

  beforeEach(() => {
    authService = new AuthService('http://localhost:5000');
    (fetch as jest.Mock).mockClear();
  });

  describe('register', () => {
    it('should register user successfully', async () => {
      const mockResponse = {
        success: true,
        data: {
          user: {
            userId: 'user123',
            email: 'test@example.com',
            username: 'testuser',
            createdAt: '2025-09-08T17:01:52.011263Z',
            isActive: true,
          },
        },
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await authService.register('test@example.com', 'testuser', 'TestPass123');
      
      expect(result).toEqual(mockResponse.data.user);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5000/auth/register',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'test@example.com',
            username: 'testuser',
            password: 'TestPass123',
          }),
        })
      );
    });

    it('should handle registration error', async () => {
      const mockError = {
        success: false,
        error: {
          code: 'REGISTRATION_ERROR',
          message: 'User already exists',
        },
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve(mockError),
      });

      await expect(
        authService.register('test@example.com', 'testuser', 'TestPass123')
      ).rejects.toThrow('User already exists');
    });
  });
});
```

### 6.2 Integration Tests

```typescript
// __tests__/integration/auth.test.ts
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '../contexts/AuthContext';
import LoginForm from '../components/LoginForm';

const renderWithAuth = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  );
};

describe('Login Integration', () => {
  it('should login user successfully', async () => {
    renderWithAuth(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'TestPass123' },
    });
    
    fireEvent.click(screen.getByRole('button', { name: /đăng nhập/i }));
    
    await waitFor(() => {
      expect(screen.getByText('Đăng nhập thành công')).toBeInTheDocument();
    });
  });
});
```

---

## 7. Environment Configuration

### 7.1 Environment Variables

```bash
# .env.development
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_APP_NAME=Reddit Clone Dev

# .env.production
REACT_APP_API_BASE_URL=https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod
REACT_APP_APP_NAME=Reddit Clone
```

### 7.2 Configuration File

```typescript
// config/index.ts
interface Config {
  apiBaseUrl: string;
  appName: string;
  environment: 'development' | 'production' | 'test';
}

const config: Config = {
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000',
  appName: process.env.REACT_APP_APP_NAME || 'Reddit Clone',
  environment: process.env.NODE_ENV as 'development' | 'production' | 'test',
};

export default config;
```

---

## 8. Performance Optimization

### 8.1 Request Debouncing

```typescript
// hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Usage in search component
const SearchComponent = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearchTerm) {
      // Perform search API call
      searchUsers(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);
};
```

### 8.2 Caching

```typescript
// utils/cache.ts
class ApiCache {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private ttl = 5 * 60 * 1000; // 5 minutes

  set(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  clear(): void {
    this.cache.clear();
  }
}

export const apiCache = new ApiCache();
```

---

## 9. Monitoring và Analytics

### 9.1 Error Tracking

```typescript
// utils/errorTracking.ts
interface ErrorInfo {
  message: string;
  code: string;
  statusCode: number;
  url: string;
  timestamp: string;
  userAgent: string;
}

export const trackError = (error: ErrorInfo) => {
  // Send to error tracking service (Sentry, LogRocket, etc.)
  console.error('API Error:', error);
  
  // Example: Send to analytics
  if (window.gtag) {
    window.gtag('event', 'api_error', {
      error_code: error.code,
      error_message: error.message,
    });
  }
};
```

### 9.2 Performance Monitoring

```typescript
// utils/performance.ts
export const measureApiCall = async <T>(
  apiCall: () => Promise<T>,
  endpoint: string
): Promise<T> => {
  const startTime = performance.now();
  
  try {
    const result = await apiCall();
    const endTime = performance.now();
    
    // Track successful API call
    console.log(`API call to ${endpoint} took ${endTime - startTime}ms`);
    
    return result;
  } catch (error) {
    const endTime = performance.now();
    
    // Track failed API call
    console.error(`API call to ${endpoint} failed after ${endTime - startTime}ms`);
    
    throw error;
  }
};
```

---

## 10. Deployment Checklist

### 10.1 Pre-deployment

- [ ] Test all API endpoints
- [ ] Verify error handling
- [ ] Check CORS configuration
- [ ] Validate environment variables
- [ ] Test token refresh flow
- [ ] Verify security headers

### 10.2 Post-deployment

- [ ] Monitor API response times
- [ ] Check error rates
- [ ] Verify authentication flow
- [ ] Test with different browsers
- [ ] Validate mobile compatibility

---

### Support

Nếu có câu hỏi hoặc cần hỗ trợ, vui lòng liên hệ team backend hoặc tạo issue trong repository.
