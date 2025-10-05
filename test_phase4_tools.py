"""
Test Phase 4 Tools - Refactoring Safety & Quality Metrics

Tests the 5 new tools:
1. check_breaking_changes - Refactoring impact analysis
2. find_usage_examples - Real usage pattern finder
3. find_todo_and_fixme - Technical debt markers
4. get_file_history_summary - Git history analysis
5. get_test_coverage - Test coverage estimation
"""

import asyncio
import json
import sys
from pathlib import Path

# Direct imports for testing
sys.path.insert(0, str(Path(__file__).parent))
import codemind

async def test_check_breaking_changes():
    """Test 1: Check breaking changes for scan_project"""
    print("\n" + "="*70)
    print("TEST 1: Check Breaking Changes for scan_project()")
    print("="*70)
    
    # Test checking a critical function
    result = codemind.check_breaking_changes(
        function_name="scan_project",
        file_path="codemind.py"
    )
    
    print(result)
    
    # Verify it contains key info
    assert "Breaking Change Analysis" in result
    assert "scan_project" in result
    assert "Call Sites" in result or "Severity" in result
    print("✅ Breaking change analysis working!")

async def test_find_usage_examples():
    """Test 2: Find usage examples of init_database"""
    print("\n" + "="*70)
    print("TEST 2: Find Usage Examples for init_database()")
    print("="*70)
    
    result = codemind.find_usage_examples(
        function_name="init_database",
        file_path="codemind.py",
        limit=3
    )
    
    print(result)
    
    assert "Usage Examples" in result
    assert "init_database" in result
    print("✅ Usage examples working!")

async def test_find_todo_fixme():
    """Test 3: Search for TODO comments"""
    print("\n" + "="*70)
    print("TEST 3: Find TODO Comments")
    print("="*70)
    
    result = codemind.find_todo_and_fixme(
        tag_type="TODO",
        limit=10
    )
    
    print(result)
    
    assert "TODO" in result
    # May or may not find TODOs - that's OK
    print("✅ TODO search working!")

async def test_file_history():
    """Test 4: Get file history summary"""
    print("\n" + "="*70)
    print("TEST 4: File History Summary for codemind.py")
    print("="*70)
    
    result = codemind.get_file_history_summary(
        file_path="codemind.py",
        days_back=30
    )
    
    print(result)
    
    assert "Git History" in result
    # Git may or may not be available
    if "Git not available" in result:
        print("⚠️ Git not available - skipping validation")
    else:
        assert "Commits" in result or "commits" in result.lower()
    print("✅ File history analysis working!")

async def test_test_coverage():
    """Test 5: Check test coverage for codemind.py"""
    print("\n" + "="*70)
    print("TEST 5: Test Coverage for codemind.py")
    print("="*70)
    
    result = codemind.get_test_coverage(
        file_path="codemind.py"
    )
    
    print(result)
    
    assert "Test Coverage Analysis" in result
    assert "Coverage" in result or "Tested" in result
    print("✅ Test coverage analysis working!")

async def test_all_tools():
    """Run all Phase 4 tool tests"""
    print("\n" + "🚀 " + "="*66)
    print("PHASE 4 TOOLS TEST SUITE")
    print("Testing 5 new tools: Breaking Changes, Usage Examples, TODO/FIXME,")
    print("File History, and Test Coverage")
    print("="*68 + "\n")
    
    try:
        await test_check_breaking_changes()
        await test_find_usage_examples()
        await test_find_todo_fixme()
        await test_file_history()
        await test_test_coverage()
        
        print("\n" + "="*70)
        print("✅ ALL PHASE 4 TESTS PASSED!")
        print("="*70)
        print("\n📊 Summary:")
        print("  • check_breaking_changes: ✅ Working")
        print("  • find_usage_examples: ✅ Working")
        print("  • find_todo_and_fixme: ✅ Working")
        print("  • get_file_history_summary: ✅ Working")
        print("  • get_test_coverage: ✅ Working")
        print("\n🎉 All 5 Phase 4 tools validated!")
        print("📈 Total tools: 17 (340% of minimum requirement)\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_all_tools())
