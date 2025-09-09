#!/bin/bash

# Reddit Clone Backend API Testing Script
# Test real API deployed on AWS

API_URL="https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"
EMAIL="test@example.com"
USERNAME="testuser$(date +%s)"  # Add timestamp to make unique
PASSWORD="TestPass123"

echo "🚀 Testing Reddit Clone Backend API on AWS"
echo "📍 API URL: $API_URL"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print test results
print_result() {
    local status=$1
    local message=$2
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✅ $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Function to test endpoint with pretty JSON output
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    local expected_status=$5
    
    echo -e "\n${BLUE}🔄 $description${NC}"
    echo "Request: $method $API_URL$endpoint"
    
    if [ -n "$data" ]; then
        echo "Data: $data"
        response=$(curl -s -w "\n%{http_code}" -X $method \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method \
            -H "Content-Type: application/json" \
            "$API_URL$endpoint")
    fi
    
    # Extract HTTP status code (last line)
    http_code=$(echo "$response" | tail -n1)
    # Extract response body (all lines except last)
    response_body=$(echo "$response" | head -n -1)
    
    echo "Status: $http_code"
    echo "Response:"
    if command -v jq &> /dev/null; then
        echo "$response_body" | jq . 2>/dev/null || echo "$response_body"
    else
        echo "$response_body"
    fi
    
    if [ "$http_code" -eq "$expected_status" ]; then
        print_result 0 "$description - Status $http_code ✓"
        return 0
    else
        print_result 1 "$description - Expected $expected_status, got $http_code"
        return 1
    fi
}

# Test 1: CORS Preflight
test_endpoint "OPTIONS" "/auth/register" "" "CORS Preflight Request" 200

# Test 2: Invalid endpoint
test_endpoint "GET" "/invalid/endpoint" "" "Invalid Endpoint Test" 404

# Test 3: User Registration with invalid email
test_endpoint "POST" "/auth/register" '{"email": "invalid-email", "username": "testuser", "password": "TestPass123"}' "Registration with Invalid Email" 400

# Test 4: User Registration with weak password
test_endpoint "POST" "/auth/register" '{"email": "test@example.com", "username": "testuser", "password": "weak"}' "Registration with Weak Password" 400

# Test 5: User Registration with short username
test_endpoint "POST" "/auth/register" '{"email": "test@example.com", "username": "a", "password": "TestPass123"}' "Registration with Short Username" 400

# Test 6: User Registration with valid data
echo -e "\n${YELLOW}📝 Attempting user registration with valid data...${NC}"
test_endpoint "POST" "/auth/register" "{\"email\": \"$EMAIL\", \"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" "Valid User Registration" 200

# Test 7: Duplicate user registration (should fail)
test_endpoint "POST" "/auth/register" "{\"email\": \"$EMAIL\", \"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" "Duplicate User Registration" 400

# Test 8: Login with invalid credentials
test_endpoint "POST" "/auth/login" '{"email": "nonexistent@example.com", "password": "WrongPass123"}' "Login with Invalid Credentials" 400

# Test 9: Login with valid credentials
echo -e "\n${YELLOW}🔐 Attempting login...${NC}"
login_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
    "$API_URL/auth/login")

login_http_code=$(echo "$login_response" | tail -n1)
login_body=$(echo "$login_response" | head -n -1)

echo "Login Status: $login_http_code"
echo "Login Response:"
if command -v jq &> /dev/null; then
    echo "$login_body" | jq . 2>/dev/null || echo "$login_body"
else
    echo "$login_body"
fi

# Extract access token if login successful
if [ "$login_http_code" -eq 200 ]; then
    if command -v jq &> /dev/null; then
        ACCESS_TOKEN=$(echo "$login_body" | jq -r '.data.accessToken // empty' 2>/dev/null)
    fi
    
    if [ -n "$ACCESS_TOKEN" ] && [ "$ACCESS_TOKEN" != "null" ]; then
        print_result 0 "Login successful, token extracted"
        
        # Test 10: Logout with valid token
        test_endpoint "POST" "/auth/logout" '{}' "Logout with Valid Token" 200 \
            -H "Authorization: Bearer $ACCESS_TOKEN"
    else
        print_result 1 "Login successful but couldn't extract token"
    fi
else
    print_result 1 "Login failed with status $login_http_code"
fi

# Test 11: Logout without authorization header
test_endpoint "POST" "/auth/logout" '{}' "Logout without Auth Header" 401

# Test 12: Forgot password
test_endpoint "POST" "/auth/forgot-password" "{\"email\": \"$EMAIL\"}" "Forgot Password Request" 200

# Test 13: Reset password with invalid data
test_endpoint "POST" "/auth/reset-password" '{"email": "test@example.com", "confirmationCode": "invalid", "newPassword": "NewPass123"}' "Reset Password with Invalid Code" 400

# Test 14: Invalid JSON
test_endpoint "POST" "/auth/register" 'invalid json' "Invalid JSON Request" 400

echo -e "\n${GREEN}🏁 API Testing Complete!${NC}"
echo -e "\n📊 Summary:"
echo "• API Base URL: $API_URL"
echo "• Test User: $EMAIL"
echo "• Username: $USERNAME"
echo -e "\n💡 Note: Check CloudWatch logs for detailed error information"
echo "   aws logs tail /aws/lambda/RedditCloneStack-AuthLambda* --follow --region ap-southeast-1"
