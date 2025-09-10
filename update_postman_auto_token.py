#!/usr/bin/env python3
"""
Script to update Postman collection with auto Bearer token setup
"""

import json

def update_postman_collection():
    """Update Postman collection with auto Bearer token setup"""
    
    # Read current collection
    with open('docs/postman-collection.json', 'r') as f:
        collection = json.load(f)
    
    # Update collection-level pre-request script
    collection['event'] = [
        {
            "listen": "prerequest",
            "script": {
                "type": "text/javascript",
                "exec": [
                    "// Auto-login if no token exists",
                    "const token = pm.environment.get('access_token');",
                    "if (!token) {",
                    "    console.log('No token found, attempting auto-login...');",
                    "    ",
                    "    // Auto-login request",
                    "    pm.sendRequest({",
                    "        url: pm.environment.get('base_url') + '/auth/login',",
                    "        method: 'POST',",
                    "        header: {",
                    "            'Content-Type': 'application/json'",
                    "        },",
                    "        body: {",
                    "            mode: 'raw',",
                    "            raw: JSON.stringify({",
                    "                email: pm.environment.get('test_email') || 'test@example.com',",
                    "                password: pm.environment.get('test_password') || 'TestPass123'",
                    "            })",
                    "        }",
                    "    }, function (err, response) {",
                    "        if (response && response.json() && response.json().data && response.json().data.access_token) {",
                    "            pm.environment.set('access_token', response.json().data.access_token);",
                    "            console.log('Auto-login successful, token saved');",
                    "        } else {",
                    "            console.log('Auto-login failed:', response ? response.json() : err);",
                    "        }",
                    "    });",
                    "} else {",
                    "    console.log('Token found:', token.substring(0, 20) + '...');",
                    "}"
                ]
            }
        }
    ]
    
    # Update login requests to save token
    for item in collection['item']:
        if item['name'] == 'Authentication (AuthLambda)':
            for auth_item in item['item']:
                if 'Login' in auth_item['name'] and 'Valid' in auth_item['name']:
                    # Add test script to save token
                    auth_item['event'] = [
                        {
                            "listen": "test",
                            "script": {
                                "type": "text/javascript",
                                "exec": [
                                    "pm.test('Status code is 200', function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});",
                                    "",
                                    "pm.test('Response has access token', function () {",
                                    "    const response = pm.response.json();",
                                    "    pm.expect(response.data).to.have.property('access_token');",
                                    "    ",
                                    "    // Save token to environment",
                                    "    if (response.data.access_token) {",
                                    "        pm.environment.set('access_token', response.data.access_token);",
                                    "        console.log('Token saved to environment');",
                                    "    }",
                                    "});",
                                    "",
                                    "pm.test('Response structure is correct', function () {",
                                    "    const response = pm.response.json();",
                                    "    pm.expect(response).to.have.property('success', true);",
                                    "    pm.expect(response).to.have.property('data');",
                                    "    pm.expect(response.data).to.have.property('user_id');",
                                    "});"
                                ]
                            }
                        }
                    ]
    
    # Update all requests to use Bearer token
    def update_requests_auth(items):
        for item in items:
            if 'request' in item:
                # Set Authorization header
                if 'header' not in item['request']:
                    item['request']['header'] = []
                
                # Remove existing Authorization header
                item['request']['header'] = [h for h in item['request']['header'] if h.get('key', '').lower() != 'authorization']
                
                # Add Bearer token header
                item['request']['header'].append({
                    "key": "Authorization",
                    "value": "Bearer {{access_token}}",
                    "type": "text",
                    "description": "JWT Bearer token for authentication"
                })
            
            # Recursively update nested items
            if 'item' in item:
                update_requests_auth(item['item'])
    
    update_requests_auth(collection['item'])
    
    # Update collection description
    collection['info']['description'] = """
# Reddit Clone Backend API Collection

## Auto Authentication Setup

This collection includes automatic Bearer token management:

1. **Environment Variables Required:**
   - `base_url`: API base URL (e.g., https://your-api.amazonaws.com/prod)
   - `test_email`: Test user email
   - `test_password`: Test user password
   - `access_token`: (Auto-populated) JWT access token

2. **Auto-Login:**
   - Collection automatically logs in if no token exists
   - Token is saved to environment variable
   - All requests use Bearer token authentication

3. **Manual Login:**
   - Run any Login request to get fresh token
   - Token is automatically saved to environment

## Usage:
1. Set up environment variables
2. Run any request - auto-login will happen if needed
3. All subsequent requests will use the saved token

## Architecture:
- **AuthLambda**: Handles authentication and posts
- **CommentsLambda**: Handles comments (separate function)
"""
    
    # Write updated collection
    with open('docs/postman-collection.json', 'w') as f:
        json.dump(collection, f, indent=2)
    
    print("✅ Postman collection updated with auto Bearer token setup")
    print("\n📋 Setup Instructions:")
    print("1. Create Environment in Postman")
    print("2. Add variables:")
    print("   - base_url: https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod")
    print("   - test_email: test@example.com")
    print("   - test_password: TestPass123")
    print("3. Import updated collection")
    print("4. Run any request - auto-login will happen!")

if __name__ == "__main__":
    update_postman_collection()
