#!/usr/bin/env python3
"""
Script to build Lambda deployment package with dependencies.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_lambda_package():
    """Build Lambda deployment package."""
    project_root = Path(__file__).parent.parent
    build_dir = project_root / "lambda_build"
    
    # Clean build directory
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    print("🔨 Building Lambda deployment package...")
    
    # Copy source code
    print("📁 Copying source code...")
    shutil.copytree(project_root / "src", build_dir / "src")
    
    # Copy lambda handler
    shutil.copy2(project_root / "lambda_handler.py", build_dir / "lambda_handler.py")
    
    # Copy requirements
    shutil.copy2(project_root / "requirements-lambda.txt", build_dir / "requirements.txt")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "-r", str(build_dir / "requirements.txt"),
        "-t", str(build_dir)
    ], check=True)
    
    # Create deployment zip
    print("📦 Creating deployment package...")
    shutil.make_archive(
        str(project_root / "lambda-deployment"),
        'zip',
        str(build_dir)
    )
    
    print("✅ Lambda package built successfully!")
    print(f"📦 Package: {project_root / 'lambda-deployment.zip'}")
    
    # Clean up build directory
    shutil.rmtree(build_dir)
    print("🧹 Cleaned up build directory")

if __name__ == "__main__":
    build_lambda_package()
