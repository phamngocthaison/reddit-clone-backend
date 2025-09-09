#!/usr/bin/env python3
"""
Download pre-built dependencies for Linux x86_64.
"""

import os
import subprocess
import sys
from pathlib import Path

def download_dependencies():
    """Download dependencies for Linux platform."""
    lambda_dir = Path(__file__).parent.parent / "lambda-deployment"
    
    print("📦 Downloading dependencies for Linux x86_64...")
    
    # Download pre-built wheels for Linux
    subprocess.run([
        sys.executable, "-m", "pip", "download",
        "-r", str(lambda_dir / "requirements.txt"),
        "-d", str(lambda_dir),
        "--platform", "linux_x86_64",
        "--python-version", "39",
        "--only-binary=:all:",
        "--no-deps"
    ], check=True)
    
    # Install dependencies
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "-r", str(lambda_dir / "requirements.txt"),
        "-t", str(lambda_dir),
        "--platform", "linux_x86_64",
        "--python-version", "39",
        "--only-binary=:all:",
        "--no-deps"
    ], check=True)
    
    print("✅ Dependencies downloaded successfully!")

if __name__ == "__main__":
    download_dependencies()
