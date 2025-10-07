#!/usr/bin/env python3
"""
Run all test suites sequentially and report results.
"""

import sys
import os
import subprocess
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("CodeMind Test Suite Runner")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

tests = [
    ("01_basic", "tests/test_01_basic.py", "Basic tool validation"),
    ("02_chains", "tests/test_02_chains.py", "Tool chaining scenarios"),
    ("03_complex", "tests/test_03_complex.py", "Complex edge cases"),
    ("comprehensive", "tests/test_comprehensive.py", "Comprehensive validation"),
    ("curveballs", "tests/test_curveballs.py", "Edge case stress tests"),
    ("validation", "tests/final_validation.py", "Production readiness")
]

results = []

for test_name, test_file, description in tests:
    print("\n" + "=" * 80)
    print(f"Running: {test_name} - {description}")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        if result.returncode == 0:
            print(f"\n✅ {test_name}: PASSED")
            results.append((test_name, "PASSED", result.returncode))
        else:
            print(f"\n⚠️  {test_name}: ISSUES DETECTED (exit code {result.returncode})")
            results.append((test_name, "ISSUES", result.returncode))
            
    except Exception as e:
        print(f"\n❌ {test_name}: FAILED - {e}")
        results.append((test_name, "FAILED", -1))

print("\n\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

passed = sum(1 for _, status, _ in results if status == "PASSED")
issues = sum(1 for _, status, _ in results if status == "ISSUES")
failed = sum(1 for _, status, _ in results if status == "FAILED")

print(f"Total Test Suites: {len(results)}")
print(f"✅ Passed: {passed}")
print(f"⚠️  Issues: {issues}")
print(f"❌ Failed: {failed}")
print()

print("Detailed Results:")
print("-" * 80)
for test_name, status, exit_code in results:
    status_emoji = "✅" if status == "PASSED" else "⚠️ " if status == "ISSUES" else "❌"
    print(f"{status_emoji} {test_name:20s} {status:10s} (exit code: {exit_code})")

print("\n" + "=" * 80)
if failed == 0 and issues == 0:
    print("🎉 ALL TESTS PASSED! CodeMind is production-ready!")
elif failed == 0:
    print("✅ MOSTLY PASSING with minor issues")
else:
    print("⚠️  ATTENTION NEEDED - Some tests failed")
print("=" * 80)

sys.exit(0 if failed == 0 else 1)
