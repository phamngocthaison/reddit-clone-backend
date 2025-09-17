#!/bin/bash

# Reddit Clone Backend - Test Runner Script
# This script runs different levels of tests after deployment

echo "🚀 Reddit Clone Backend - Test Runner"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Make scripts executable
chmod +x quick_test.py quick_test_simple.py

# Function to run tests with timeout
run_test() {
    local script_name=$1
    local test_name=$2
    local timeout_seconds=${3:-60}
    
    echo ""
    echo "🧪 Running $test_name..."
    echo "----------------------------------------"
    
    timeout $timeout_seconds python3 $script_name
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        echo "⏰ Test timed out after $timeout_seconds seconds"
        return 1
    elif [ $exit_code -eq 0 ]; then
        echo "✅ $test_name completed successfully"
        return 0
    else
        echo "❌ $test_name failed with exit code $exit_code"
        return 1
    fi
}

# Parse command line arguments
TEST_LEVEL="simple"
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --level)
            TEST_LEVEL="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --level LEVEL    Test level: simple, full (default: simple)"
            echo "  --verbose, -v    Verbose output"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Test Levels:"
            echo "  simple          Quick test of critical endpoints (30s timeout)"
            echo "  full            Comprehensive test of all endpoints (120s timeout)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set timeout based on test level
if [ "$TEST_LEVEL" = "full" ]; then
    TIMEOUT=120
    SCRIPT="quick_test.py"
    TEST_NAME="Full Test Suite"
else
    TIMEOUT=30
    SCRIPT="quick_test_simple.py"
    TEST_NAME="Simple Quick Test"
fi

echo "Test Level: $TEST_LEVEL"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Run the appropriate test
run_test $SCRIPT "$TEST_NAME" $TIMEOUT
EXIT_CODE=$?

echo ""
echo "======================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed! Deployment looks good."
else
    echo "💥 Some tests failed. Please check the deployment."
fi

exit $EXIT_CODE
