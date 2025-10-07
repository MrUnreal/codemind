"""File indexing and scanning functionality."""
import hashlib
import logging
from datetime import datetime
from pathlib import Path

from .workspace import get_workspace_path, get_workspace_config, get_workspace_db, get_workspace_embedding
from .parsers import extract_purpose, extract_key_exports
import json

logger = logging.getLogger(__name__)


def _index_file_internal(file_path: str, conn, embedding_model=None):
    """Internal function to index a file - called by scan_project."""
    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        file_hash = hashlib.md5(content.encode()).hexdigest()
        cursor = conn.execute('SELECT file_hash FROM files WHERE path = ?', (file_path,))
        result = cursor.fetchone()
        if result and result[0] == file_hash:
            return  # Already indexed with same hash
        
        purpose = extract_purpose(content, file_path)
        key_exports = extract_key_exports(content, file_path)
        embedding_blob = None
        
        if embedding_model:
            embedding_blob = embedding_model.encode(purpose, convert_to_numpy=True).tobytes()
        
        conn.execute("""INSERT OR REPLACE INTO files 
            (path, purpose, last_scanned, embedding, key_exports, file_hash, size_kb) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (file_path, purpose, datetime.now(), embedding_blob, json.dumps(key_exports),
             file_hash, len(content.encode()) // 1024))
        conn.commit()
    except Exception as e:
        logger.debug(f"Error indexing {file_path}: {e}")


def scan_project(workspace_root: str) -> int:
    """Scan a workspace and index all files.
    
    Args:
        workspace_root: Path to the workspace to scan
        
    Returns:
        Number of files indexed
    """
    ws_path = get_workspace_path(workspace_root)
    config = get_workspace_config(workspace_root)
    conn = get_workspace_db(workspace_root)
    embedding_model = get_workspace_embedding(workspace_root)
    
    indexed = 0
    for ext in config["watched_extensions"]:
        for fp in ws_path.rglob(f"*{ext}"):
            if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                try:
                    if fp.stat().st_size // 1024 <= config["max_file_size_kb"]:
                        _index_file_internal(str(fp), conn, embedding_model)
                        indexed += 1
                except OSError:
                    pass
    
    logger.info(f"✓ Indexed {indexed} files in {ws_path}")
    return indexed
