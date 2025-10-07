"""CodeMind - MCP Memory Server for GitHub Copilot

A lightweight Model Context Protocol (MCP) server that gives GitHub Copilot 
queryable memory about your project.
"""
__version__ = "2.0.0"

from .workspace import (
    get_workspace_path,
    get_workspace_config,
    get_workspace_db,
    get_workspace_embedding,
    lazy_scan
)

from .parsers import (
    parse_imports_ast,
    parse_calls_ast,
    parse_functions_ast,
    extract_purpose,
    extract_key_exports
)

from .indexing import scan_project

__all__ = [
    'get_workspace_path',
    'get_workspace_config',
    'get_workspace_db',
    'get_workspace_embedding',
    'lazy_scan',
    'parse_imports_ast',
    'parse_calls_ast',
    'parse_functions_ast',
    'extract_purpose',
    'extract_key_exports',
    'scan_project',
]
