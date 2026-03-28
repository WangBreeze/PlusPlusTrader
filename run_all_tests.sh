#!/bin/bash
# run_all_tests.sh - Run all PlusPlusTrader tests
# Created: 2026-03-15

echo "========================================"
echo "PlusPlusTrader Test Suite Runner"
echo "Date: $(date)"
echo "========================================"
echo ""

# Build directory
BUILD_DIR="build"
cd "$(dirname "$0")" || exit 1

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found: $BUILD_DIR"
    echo "Please run: mkdir build && cd build && cmake .."
    exit 1
fi

cd "$BUILD_DIR" || exit 1

# Run individual tests
TESTS=("test_mfi" "test_backtest_stats" "test_indicators" "test_backtest_units")
TOTAL_PASSED=0
TOTAL_FAILED=0
FAILED_TESTS=()

echo "Running all tests..."
echo ""

for TEST in "${TESTS[@]}"; do
    if [ ! -f "$TEST" ]; then
        echo "⚠️  Test executable not found: $TEST"
        continue
    fi
    
    echo "➡️  Running: $TEST"
    echo "----------------------------------------"
    
    if ./"$TEST"; then
        echo "✅ $TEST: PASSED"
        ((TOTAL_PASSED++))
    else
        echo "❌ $TEST: FAILED"
        ((TOTAL_FAILED++))
        FAILED_TESTS+=("$TEST")
    fi
    
    echo ""
done

# Summary
echo "========================================"
echo "Test Run Summary"
echo "========================================"
echo "Total tests run: ${#TESTS[@]}"
echo "Tests passed: $TOTAL_PASSED"
echo "Tests failed: $TOTAL_FAILED"
echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo "🎉 All tests passed successfully!"
    exit 0
else
    echo "❌ Failed tests:"
    for FAILED in "${FAILED_TESTS[@]}"; do
        echo "  - $FAILED"
    done
    echo ""
    echo "Please review the failed test output above."
    exit 1
fi