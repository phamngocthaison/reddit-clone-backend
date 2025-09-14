#!/usr/bin/env python3
import subprocess
import json
import sys

def get_resource_methods(rest_api_id, resource_id):
    """Get methods for a specific resource"""
    try:
        result = subprocess.run([
            'aws', 'apigateway', 'get-resource',
            '--rest-api-id', rest_api_id,
            '--resource-id', resource_id,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        return data.get('resourceMethods', {})
    except subprocess.CalledProcessError as e:
        print(f"Error getting resource {resource_id}: {e}")
        return {}

def check_all_resources():
    """Check all resources for missing OPTIONS methods"""
    rest_api_id = 'ugn2h0yxwf'
    
    # Get all resources
    try:
        result = subprocess.run([
            'aws', 'apigateway', 'get-resources',
            '--rest-api-id', rest_api_id,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        resources = json.loads(result.stdout)['items']
    except subprocess.CalledProcessError as e:
        print(f"Error getting resources: {e}")
        return
    
    print("🔍 Checking all API endpoints for CORS support...")
    print("=" * 80)
    
    missing_options = []
    has_options = []
    
    for resource in resources:
        resource_id = resource['id']
        path = resource['path']
        path_part = resource.get('pathPart', '')
        
        # Skip root resource
        if path == '/':
            continue
            
        methods = get_resource_methods(rest_api_id, resource_id)
        
        if not methods:
            continue
            
        # Check if OPTIONS method exists
        if 'OPTIONS' in methods:
            has_options.append(path)
        else:
            # Check if this is a resource that might need CORS
            has_other_methods = any(method in methods for method in ['GET', 'POST', 'PUT', 'DELETE'])
            if has_other_methods:
                missing_options.append({
                    'path': path,
                    'methods': list(methods.keys()),
                    'resource_id': resource_id
                })
    
    print(f"✅ Resources WITH OPTIONS method ({len(has_options)}):")
    for path in sorted(has_options):
        print(f"   {path}")
    
    print(f"\n❌ Resources MISSING OPTIONS method ({len(missing_options)}):")
    for item in sorted(missing_options, key=lambda x: x['path']):
        print(f"   {item['path']} - Methods: {', '.join(item['methods'])}")
    
    print(f"\n📊 Summary:")
    print(f"   Total resources checked: {len(resources)}")
    print(f"   With OPTIONS: {len(has_options)}")
    print(f"   Missing OPTIONS: {len(missing_options)}")
    
    if missing_options:
        print(f"\n🚨 APIs that need CORS fix:")
        for item in missing_options:
            print(f"   - {item['path']} (ID: {item['resource_id']})")

if __name__ == "__main__":
    check_all_resources()
