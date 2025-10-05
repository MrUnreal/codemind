"""Simple direct test of new functions"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import codemind

# Initialize
codemind.init_server()
codemind.lazy_scan()

print("=" * 70)
print("🧪 DIRECT TESTING OF NEW TOOLS")
print("=" * 70)

print("\nTEST 1: force_reindex()")
print("-" * 70)
try:
    # Call the implementation function directly
    result = codemind._force_reindex_impl()
    print(result)
    print("✅ TEST 1 PASSED")
except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")

print("\nTEST 2: index_file('codemind.py')")
print("-" * 70)
try:
    result = codemind._index_file_impl("codemind.py")
    print(result)
    print("✅ TEST 2 PASSED")
except Exception as e:
    print(f"❌ TEST 2 FAILED: {e}")

print("\nTEST 3: get_call_tree('init_database', 'codemind.py')")
print("-" * 70)
try:
    result = codemind._get_call_tree_impl("init_database", "codemind.py", 2)
    print(result)
    print("✅ TEST 3 PASSED")
except Exception as e:
    print(f"❌ TEST 3 FAILED: {e}")

print("\nTEST 4: get_call_tree('scan_project') - Auto-find")
print("-" * 70)
try:
    result = codemind._get_call_tree_impl("scan_project")
    print(result)
    print("✅ TEST 4 PASSED")
except Exception as e:
    print(f"❌ TEST 4 FAILED: {e}")

print("\n" + "=" * 70)
print("✅ ALL DIRECT TESTS COMPLETED")
print("=" * 70)
