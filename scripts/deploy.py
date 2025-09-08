#!/usr/bin/env python3
"""Deployment script for Reddit Clone Backend."""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, cwd: Path = None) -> int:
    """Run a shell command and return the exit code."""
    print(f"🔧 Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    return result.returncode


def check_prerequisites() -> bool:
    """Check if all prerequisites are installed."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        return False
    print("✅ Python version OK")
    
    # Check if AWS CLI is configured
    if run_command("aws sts get-caller-identity > /dev/null 2>&1") != 0:
        print("❌ AWS CLI is not configured. Please run 'aws configure' first.")
        return False
    print("✅ AWS CLI configured")
    
    # Check if CDK is installed
    if run_command("cdk --version > /dev/null 2>&1") != 0:
        print("❌ AWS CDK is not installed. Installing...")
        if run_command("npm install -g aws-cdk") != 0:
            print("❌ Failed to install AWS CDK")
            return False
    print("✅ AWS CDK available")
    
    return True


def create_virtual_environment() -> bool:
    """Create and activate virtual environment."""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / ".venv"
    
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        if run_command(f"python -m venv {venv_path}", cwd=project_root) != 0:
            print("❌ Failed to create virtual environment")
            return False
    
    print("✅ Virtual environment ready")
    return True


def install_dependencies() -> bool:
    """Install Python dependencies."""
    project_root = Path(__file__).parent.parent
    
    print("📦 Installing dependencies...")
    
    # Activate virtual environment and install dependencies
    if os.name == "nt":  # Windows
        activate_cmd = f".\\.venv\\Scripts\\activate && pip install -r requirements.txt"
    else:  # Unix/Linux/macOS
        activate_cmd = f"source .venv/bin/activate && pip install -r requirements.txt"
    
    if run_command(activate_cmd, cwd=project_root) != 0:
        print("❌ Failed to install dependencies")
        return False
    
    print("✅ Dependencies installed")
    return True


def run_tests() -> bool:
    """Run the test suite."""
    project_root = Path(__file__).parent.parent
    
    print("🧪 Running tests...")
    
    # Activate virtual environment and run tests
    if os.name == "nt":  # Windows
        test_cmd = f".\\.venv\\Scripts\\activate && python -m pytest tests/ -v"
    else:  # Unix/Linux/macOS
        test_cmd = f"source .venv/bin/activate && python -m pytest tests/ -v"
    
    if run_command(test_cmd, cwd=project_root) != 0:
        print("❌ Tests failed")
        return False
    
    print("✅ All tests passed")
    return True


def run_linting() -> bool:
    """Run code linting and formatting."""
    project_root = Path(__file__).parent.parent
    
    print("🔍 Running code quality checks...")
    
    # Activate virtual environment and run linting
    if os.name == "nt":  # Windows
        lint_cmd = f".\\.venv\\Scripts\\activate && python -m black --check src/ && python -m flake8 src/ && python -m mypy src/"
    else:  # Unix/Linux/macOS
        lint_cmd = f"source .venv/bin/activate && python -m black --check src/ && python -m flake8 src/ && python -m mypy src/"
    
    if run_command(lint_cmd, cwd=project_root) != 0:
        print("⚠️ Code quality checks failed. Run 'python -m black src/' to fix formatting.")
        # Don't fail deployment for linting issues, just warn
    else:
        print("✅ Code quality checks passed")
    
    return True


def bootstrap_cdk() -> bool:
    """Bootstrap CDK if needed."""
    print("🌍 Checking CDK bootstrap status...")
    
    # Check if CDK bootstrap stack exists
    if run_command("aws cloudformation describe-stacks --stack-name CDKToolkit > /dev/null 2>&1") != 0:
        print("🔧 Bootstrapping CDK...")
        if run_command("cdk bootstrap") != 0:
            print("❌ Failed to bootstrap CDK")
            return False
        print("✅ CDK bootstrapped successfully")
    else:
        print("✅ CDK already bootstrapped")
    
    return True


def synthesize_cdk() -> bool:
    """Synthesize CDK template."""
    project_root = Path(__file__).parent.parent
    
    print("📋 Synthesizing CDK template...")
    
    # Activate virtual environment and synthesize
    if os.name == "nt":  # Windows
        synth_cmd = f".\\.venv\\Scripts\\activate && cdk synth"
    else:  # Unix/Linux/macOS
        synth_cmd = f"source .venv/bin/activate && cdk synth"
    
    if run_command(synth_cmd, cwd=project_root) != 0:
        print("❌ Failed to synthesize CDK template")
        return False
    
    print("✅ CDK template synthesized")
    return True


def deploy_stack() -> bool:
    """Deploy the CDK stack."""
    project_root = Path(__file__).parent.parent
    
    print("🚀 Deploying to AWS...")
    
    # Activate virtual environment and deploy
    if os.name == "nt":  # Windows
        deploy_cmd = f".\\.venv\\Scripts\\activate && cdk deploy --require-approval never"
    else:  # Unix/Linux/macOS
        deploy_cmd = f"source .venv/bin/activate && cdk deploy --require-approval never"
    
    if run_command(deploy_cmd, cwd=project_root) != 0:
        print("❌ Deployment failed")
        return False
    
    print("✅ Deployment completed successfully!")
    return True


def print_next_steps():
    """Print next steps after successful deployment."""
    print("""
🎉 Deployment completed successfully!

🔗 Your API endpoints:
   - Check CloudFormation outputs for API Gateway URL
   - Cognito User Pool and Client IDs are in the outputs

📝 Next steps:
   1. Test the authentication endpoints
   2. Set up monitoring and logging
   3. Configure custom domain (optional)
   4. Set up CI/CD pipeline

📚 Documentation:
   - API documentation is in the README.md
   - Database schema is in docs/database-schema.md
""")


def main():
    """Main deployment function."""
    print("🚀 Starting Reddit Clone Backend Deployment...")
    
    # Change to project root directory
    os.chdir(Path(__file__).parent.parent)
    
    steps = [
        ("Checking prerequisites", check_prerequisites),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Running tests", run_tests),
        ("Running code quality checks", run_linting),
        ("Bootstrapping CDK", bootstrap_cdk),
        ("Synthesizing CDK template", synthesize_cdk),
        ("Deploying stack", deploy_stack),
    ]
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        if not step_function():
            print(f"❌ {step_name} failed. Aborting deployment.")
            sys.exit(1)
    
    print_next_steps()
    return 0


if __name__ == "__main__":
    sys.exit(main())
