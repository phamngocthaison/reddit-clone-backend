#!/usr/bin/env python3
"""
Deploy script with integrated API testing
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(cmd, description, timeout=300):
    """Run a command with timeout and error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, timeout=timeout, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Error in {description}: {e}")
        return False

def deploy_infrastructure():
    """Deploy CDK infrastructure"""
    print("🏗️  Deploying Infrastructure...")
    print("=" * 50)
    
    # Check if CDK is installed
    if not run_command("which cdk", "Checking CDK installation", 10):
        print("❌ CDK not found. Please install AWS CDK first.")
        return False
    
    # Deploy the stack
    if not run_command("cd infrastructure && cdk deploy --require-approval never", 
                      "Deploying CDK stack", 600):
        return False
    
    print("✅ Infrastructure deployed successfully!")
    return True

def run_api_tests():
    """Run API tests after deployment"""
    print("\n🧪 Running API Tests...")
    print("=" * 50)
    
    # Wait a bit for deployment to settle
    print("⏳ Waiting for deployment to settle...")
    time.sleep(30)
    
    # Run quick test first
    print("⚡ Running quick test...")
    if not run_command("python3 run_api_tests.py --quick", 
                      "Quick API test", 120):
        print("⚠️  Quick test failed, but continuing with full tests...")
    
    # Run full test suite
    print("\n🔬 Running full test suite...")
    if not run_command("python3 run_api_tests.py", 
                      "Full API test suite", 600):
        print("❌ Full test suite failed!")
        return False
    
    print("✅ All API tests passed!")
    return True

def main():
    """Main deployment function"""
    print("🚀 Reddit Clone Backend - Deploy with Tests")
    print("=" * 60)
    print(f"📅 Deploy Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Deploy infrastructure
    if not deploy_infrastructure():
        print("❌ Infrastructure deployment failed!")
        return 1
    
    # Step 2: Run API tests
    if not run_api_tests():
        print("❌ API tests failed!")
        print("🔧 Please check the API endpoints and try again.")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("✅ Infrastructure deployed")
    print("✅ API tests passed")
    print("🚀 Your Reddit Clone Backend is ready!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
