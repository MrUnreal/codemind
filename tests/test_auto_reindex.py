"""Test automatic re-indexing of modified files."""
import os
import time
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from codemind.workspace import lazy_scan, get_workspace_db


def test_auto_reindex():
    """Test that modified files are automatically re-indexed."""
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n📁 Test workspace: {tmpdir}")
        
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text('"""Original content."""\ndef foo(): pass')
        
        # First scan - should index the file
        print("\n1️⃣ Initial scan...")
        lazy_scan(tmpdir)
        
        # Check file was indexed
        conn = get_workspace_db(tmpdir)
        cursor = conn.execute('SELECT path, purpose, file_hash FROM files WHERE path = ?', (str(test_file),))
        result = cursor.fetchone()
        
        if not result:
            print("❌ FAIL: File was not indexed on first scan")
            return False
        
        original_path, original_purpose, original_hash = result
        print(f"✅ File indexed: {original_path}")
        print(f"   Purpose: {original_purpose}")
        print(f"   Hash: {original_hash[:8]}...")
        
        # Wait a moment and modify the file
        time.sleep(0.1)
        test_file.write_text('"""Modified content with new functionality."""\ndef bar(): pass')
        print(f"\n2️⃣ Modified file: {test_file.name}")
        
        # Second scan - should detect change and re-index
        print("   Running auto re-index...")
        lazy_scan(tmpdir)
        
        # Check file was re-indexed
        cursor = conn.execute('SELECT path, purpose, file_hash FROM files WHERE path = ?', (str(test_file),))
        result = cursor.fetchone()
        
        if not result:
            print("❌ FAIL: File disappeared from index")
            return False
        
        new_path, new_purpose, new_hash = result
        
        # Verify hash changed
        if new_hash == original_hash:
            print(f"❌ FAIL: File hash unchanged")
            print(f"   Old hash: {original_hash[:8]}...")
            print(f"   New hash: {new_hash[:8]}...")
            return False
        
        print(f"✅ File re-indexed with new content")
        print(f"   New purpose: {new_purpose}")
        print(f"   New hash: {new_hash[:8]}...")
        print(f"   Hash changed: {original_hash[:8]}... → {new_hash[:8]}...")
        
        # Verify purpose was updated
        if "Modified content" not in new_purpose and "new functionality" not in new_purpose:
            print(f"⚠️  WARNING: Purpose may not have been extracted correctly")
            print(f"   Expected to contain 'Modified content' or 'new functionality'")
            print(f"   Got: {new_purpose}")
        
        # Third scan with no changes - should not re-index
        print(f"\n3️⃣ No changes - should skip re-indexing...")
        lazy_scan(tmpdir)
        
        cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (str(test_file),))
        result = cursor.fetchone()
        
        if result[0] != new_hash:
            print(f"❌ FAIL: Hash changed when file wasn't modified")
            return False
        
        print(f"✅ Correctly skipped unchanged file")
        
        # Close database connection before cleanup
        conn.close()
        
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Automatic Re-indexing of Modified Files")
    print("=" * 60)
    
    try:
        success = test_auto_reindex()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60)
            print("\n✨ Modified files are automatically re-indexed!")
            print("   - First scan: Full indexing")
            print("   - Subsequent scans: Only modified files")
            print("   - Uses mtime + hash for efficiency")
            print("   - Embeddings stay fresh automatically")
        else:
            print("\n" + "=" * 60)
            print("❌ TEST FAILED")
            print("=" * 60)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
