# CodeMind - Multi-Workspace MCP Memory Server

**Tagline:** *Give Copilot a memory across all your projects*

## Overview

CodeMind is a **workspace-aware** Model Context Protocol (MCP) server that gives GitHub Copilot queryable memory about your projects. It helps prevent Copilot from creating duplicate files, forgetting architectural decisions, and suggesting rewrites instead of modifications.

### ✨ What's New in v2.0

- **🎯 Multi-Workspace Support**: Work with multiple projects simultaneously - each with its own memory
- **📦 Modular Architecture**: Clean package structure with separate modules for better maintainability
- **🔧 Workspace Parameter**: All tools accept `workspace_root` parameter for explicit project targeting
- **🏗️ Production-Quality**: AST-based parsing and radon metrics for accurate analysis

### The Problem
- 🔄 Copilot creates duplicate files when functionality already exists
- 🧠 Forgets architectural decisions made minutes ago
- ❓ Doesn't know what files are for or how they relate
- 🔁 Suggests complete rewrites instead of targeted modifications

### The Solution
- 🔍 **Semantic Search**: Find existing functionality before creating new files
- 📝 **Project Memory**: Track file purposes, changes, and architectural decisions
- ⚡ **Real-time Indexing**: Auto-index changes as you work
- 🎯 **Context-Aware**: Help Copilot understand your project structure

## Features

### 🛠️ MCP Tools for Copilot (20 Total)

#### Core Discovery Tools (5)
1. **`search_existing_code`** - Semantic search for existing functionality
2. **`check_functionality_exists`** - Quick yes/no check if functionality exists
3. **`search_by_export`** - Find where functions/classes are defined
4. **`get_file_context`** - Understand what a file does and why it exists
5. **`query_recent_changes`** - See what's been modified recently

#### Enhanced Discovery Tools (4)
6. **`get_similar_files`** - Find files with similar patterns/structure
7. **`find_dependencies`** - Bidirectional dependency analysis
8. **`list_all_decisions`** - Query decision history with keyword filtering
9. **`record_decision`** - Store architectural decisions and rationale

#### Indexing & Analysis Tools (3)
10. **`force_reindex`** - Manually trigger full project re-scan
11. **`index_file`** - Index specific file immediately
12. **`get_call_tree`** - Function call graph (callers + callees)

#### Refactoring Safety Tools (5)
13. **`check_breaking_changes`** - Identify impacted code before refactoring
14. **`find_usage_examples`** - Real-world usage patterns
15. **`find_todo_and_fixme`** - Track technical debt (TODO/FIXME/HACK)
16. **`get_file_history_summary`** - Git commit history analysis
17. **`get_test_coverage`** - Estimate test coverage

#### Zero-LLM Static Analysis Tools (3) ⭐ NEW
18. **`get_code_metrics_summary`** - Comprehensive code metrics (LOC, complexity, maintainability)
19. **`get_import_graph`** - Dependency visualization with circular detection
20. **`find_configuration_inconsistencies`** - Config analysis and secret detection

### 🚀 Auto-Indexing System

- **File Watcher**: Automatically detects file changes
- **Smart Analysis**: Extracts file purpose from docstrings and comments
- **Semantic Embeddings**: Uses sentence-transformers for semantic search
- **SQLite Storage**: Lightweight, zero-maintenance database

### ⚙️ Configuration

- **Zero Config**: Works out of the box for most projects
- **Customizable**: Support for multiple programming languages
- **Performance Tuned**: Fast queries (<500ms) and efficient indexing

## Quick Start

### Prerequisites

- Python 3.10 or higher
- GitHub Copilot or compatible MCP client

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/codemind.git
cd codemind
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize your project**:
```bash
python codemind.py
```

This will:
- Create a `.codemind/` directory in your project
- Scan and index your existing files
- Start the MCP server

### VS Code Setup

Add CodeMind to your VS Code MCP settings. Create or update your VS Code settings file:

**Windows**: `%APPDATA%\Code\User\settings.json`
**macOS**: `~/Library/Application Support/Code/User/settings.json`
**Linux**: `~/.config/Code/User/settings.json`

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["D:/path/to/CodeMind/codemind.py"],
      "cwd": "D:/Projects/YourProject"
    }
  }
}
```

**Note**: With v2.0's multi-workspace support, you can work with any project by specifying the `workspace_root` parameter in tool calls. The `cwd` is just the default.

## Multi-Workspace Support

### How It Works

Every CodeMind tool now accepts a `workspace_root` parameter (defaults to `"."`):

```python
# Search in current workspace
search_existing_code("authentication")

# Search in specific project
search_existing_code("authentication", workspace_root="/path/to/project1")

# Work with multiple projects simultaneously
search_existing_code("API client", workspace_root="/path/to/frontend")
find_dependencies("utils.py", workspace_root="/path/to/backend")
```

### Workspace Isolation

Each workspace gets its own:
- **Database**: `.codemind/memory.db` in that workspace
- **Configuration**: `codemind_config.json` if present
- **Embedding Model**: Cached per workspace
- **Session Logs**: Workspace-specific logs

This means:
✅ No cross-contamination between projects
✅ Each project can have different settings
✅ Work with multiple codebases without conflicts
✅ Switch projects without restarting the server

## Configuration

Create a `codemind_config.json` file in your project root to customize behavior:

```json
{
  "project_root": "./",
  "db_path": ".codemind/memory.db",
  "watched_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".java", ".cs", ".cpp", ".c", ".h", ".go", ".rs"],
  "scan_interval": 300,
  "max_file_size_kb": 500,
  "embedding_model": "all-MiniLM-L6-v2",
  "max_files": 10000
}
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `project_root` | `"./"` | Root directory to scan |
| `db_path` | `".codemind/memory.db"` | SQLite database location |
| `watched_extensions` | `[".py", ".js", ...]` | File extensions to index |
| `scan_interval` | `300` | Seconds between full rescans |
| `max_file_size_kb` | `500` | Maximum file size to index |
| `embedding_model` | `"all-MiniLM-L6-v2"` | Sentence transformer model |
| `max_files` | `10000` | Maximum files to index |

## Usage Examples

### Before CodeMind
```
👤 Developer: "Add JWT authentication"
🤖 Copilot: *creates auth/middleware.py*
🤖 Copilot: *creates auth/jwt_handler.py*  
🤖 Copilot: *creates utils/auth.py*
👤 Developer: "Wait, we already have this..."
```

### With CodeMind
```
🤖 Copilot: *calls search_existing_code("JWT authentication")*
🧠 CodeMind: "Found: src/auth/jwt.py (95% match) - handles JWT tokens"
🤖 Copilot: "I found existing JWT auth in src/auth/jwt.py. Should I modify it instead of creating new files?"
👤 Developer: "Perfect, yes!"
```

### Tool Usage Examples

#### 1. Search for Existing Code
```
Copilot calls: search_existing_code("user authentication")

Response:
Found 3 relevant files for 'user authentication':

1. src/auth/jwt.py (92% match)
   Purpose: JWT token generation and validation for user authentication

2. middleware/auth.py (87% match)  
   Purpose: Authentication middleware for protected routes

3. models/user.py (78% match)
   Purpose: User model with password hashing and validation
```

#### 2. Find Where Something is Defined ⭐ NEW
```
Copilot calls: search_by_export("UserModel")

Response:
Found 2 files exporting 'UserModel':

1. models/user.py
   Purpose: User model with password hashing and validation
   Exports: UserModel, validate_password, hash_password

2. models/__init__.py
   Purpose: Model exports for convenience imports
   Exports: UserModel, PostModel, CommentModel
```

#### 3. Analyze Dependencies ⭐ NEW
```
Copilot calls: find_dependencies("src/database.py")

Response:
Dependencies for src/database.py:

IMPORTS (what src/database.py depends on):
- typing, pathlib, sqlite3, contextlib

IMPORTED BY (what depends on src/database.py):
- src/models/user.py
- src/models/post.py
- src/auth/session.py
- tests/test_database.py

⚠️ Warning: This file has 4 dependents. Test thoroughly before modifying!
```

#### 4. Find Similar Files ⭐ NEW
```
Copilot calls: get_similar_files("tests/test_user.py")

Response:
Files similar to tests/test_user.py:

1. tests/test_post.py (78% similar)
   Purpose: Test suite for post model CRUD operations

2. tests/test_comment.py (65% similar)
   Purpose: Test suite for comment model and nested replies

3. tests/test_auth.py (58% similar)
   Purpose: Authentication flow integration tests
```

#### 5. Query Decision History ⭐ NEW
```
Copilot calls: list_all_decisions(keyword="authentication")

Response:
Found 3 decisions matching 'authentication':

Decision #12 (2025-01-15 14:30:00):
Description: Using JWT for authentication
Reasoning: Chose JWT over sessions for better scalability and mobile app support
Affected files: src/auth/jwt.py, middleware/auth.py

Decision #8 (2025-01-10 09:15:00):
Description: OAuth2 provider integration
Reasoning: Added Google and GitHub OAuth for easier user onboarding
Affected files: src/auth/oauth.py, config/providers.json

Decision #3 (2025-01-05 16:45:00):
Description: Password hashing with bcrypt
Reasoning: bcrypt preferred over SHA256 for better security against rainbow tables
Affected files: models/user.py, utils/security.py
```

#### 6. Get File Context
```
Copilot calls: get_file_context("src/utils/helpers.py")

Response:
File: src/utils/helpers.py
Purpose: Utility functions for data validation and formatting
Last scanned: 2025-10-04 10:30:15
Size: 23 KB
Key exports: validate_email, format_date, sanitize_input, generate_slug
```

#### 7. Record Decisions
```
Copilot calls: record_decision(
  description="Using JWT for authentication",
  reasoning="Chose JWT over sessions for better scalability and mobile app support",
  affected_files=["src/auth/jwt.py", "middleware/auth.py"]
)

Response:
Decision recorded (ID: 42)
Description: Using JWT for authentication
Reasoning: Chose JWT over sessions for better scalability and mobile app support
Affected files: src/auth/jwt.py, middleware/auth.py
```

## Architecture

### Database Schema

#### Files Table
- `path` - File path (primary key)
- `purpose` - What the file does (extracted from docstrings)
- `last_scanned` - When file was last indexed
- `embedding` - Vector representation for semantic search
- `key_exports` - Main functions/classes exported
- `file_hash` - MD5 hash for change detection
- `size_kb` - File size in kilobytes

#### Decisions Table
- `id` - Decision ID (auto-increment)
- `description` - Brief description
- `reasoning` - Detailed rationale
- `timestamp` - When decision was made
- `affected_files` - JSON array of file paths

#### Changes Table
- `id` - Change ID (auto-increment)
- `file_path` - Path of changed file
- `timestamp` - When change occurred
- `change_summary` - Description of change
- `embedding` - Vector representation of change

### Performance Characteristics

- **Query Time**: <500ms for semantic search
- **Initial Scan**: <30 seconds for 1000 files
- **Memory Usage**: <200MB for typical projects
- **Storage**: ~1-5MB database for most projects

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check Python version
python --version  # Should be 3.10+

# Install dependencies
pip install -r requirements.txt

# Check for permission issues
ls -la .codemind/
```

#### Files Not Being Indexed
1. Check file extensions in `codemind_config.json`
2. Verify file size is under `max_file_size_kb`
3. Check logs for indexing errors
4. Ensure files aren't in hidden directories

#### Slow Performance
1. Reduce `max_files` in configuration
2. Increase `max_file_size_kb` threshold
3. Use faster embedding model
4. Add more file extensions to ignore list

### Debug Mode

Run with debug logging:
```bash
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import codemind
import asyncio
asyncio.run(codemind.main())
"
```

## Development

### Package Structure (v2.0)
```
codemind/
├── codemind.py          # Entry point (63 lines)
├── codemind/            # Main package
│   ├── __init__.py      # Package exports
│   ├── workspace.py     # Multi-workspace management
│   ├── parsers.py       # AST-based code parsing
│   ├── indexing.py      # File scanning and indexing
│   └── tools/           # MCP tool implementations
│       ├── __init__.py  # Tool registration
│       ├── search.py    # Semantic search tools
│       ├── context.py   # Context & decision tools
│       ├── dependencies.py  # Dependency analysis
│       ├── analysis.py      # Code metrics
│       ├── refactoring.py   # Refactoring helpers
│       └── management.py    # Index management
├── requirements.txt     # Dependencies
├── README.md           # This file
├── example_config.json # Configuration template
└── .codemind/          # Generated per-workspace
    └── <workspace_hash>/
        └── memory.db   # SQLite database per workspace
```

**Key Modules:**
- **workspace.py**: Workspace isolation, DB/config/embedding caching
- **parsers.py**: Production-quality AST visitors for Python analysis
- **indexing.py**: File scanning with hash-based change detection
- **tools/**: 20 MCP tools organized by category

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

### Testing

```bash
# Run basic functionality test
python -c "
from codemind import CodeMindServer
import asyncio

async def test():
    server = CodeMindServer()
    await server.initialize()
    print('✅ Server initialized successfully')
    server.shutdown()

asyncio.run(test())
"
```

## Migration from v1.x to v2.0

**Good News:** v2.0 is fully backward compatible! Your existing setup will work unchanged.

### What Changed

- **Architecture**: Monolithic single file → Modular package structure
- **Multi-Workspace**: Each workspace gets isolated database and configuration
- **Tool Signatures**: All tools now accept optional `workspace_root` parameter

### For Single-Workspace Users

**No action needed!** All tools default to `workspace_root="."` (current directory). Your existing configuration works as-is.

### For Multi-Workspace Users

You can now work with multiple projects simultaneously:

```python
# In your AI assistant
"Check for authentication code in project A"
# → Uses workspace_root pointing to project A

"Search for similar patterns in project B"  
# → Uses workspace_root pointing to project B
```

Each workspace maintains:
- ✅ Separate database (no cross-contamination)
- ✅ Independent configuration
- ✅ Cached embedding models (shared if same model)

### Breaking Changes

**None!** Default behavior matches v1.x exactly.

## FAQ

### Q: Does this send my code to external services?
**A:** No! CodeMind runs entirely locally. Your code never leaves your machine.

### Q: How much storage does it use?
**A:** Typically 1-5MB for the SQLite database, even for large projects.

### Q: Does it slow down my editor?
**A:** No, CodeMind runs as a separate process and uses efficient indexing.

### Q: What languages are supported?
**A:** Python, JavaScript, TypeScript, Java, C#, C++, Go, Rust, and more via configuration.

### Q: Can I use this without GitHub Copilot?
**A:** Yes! Any MCP-compatible AI coding assistant can use CodeMind.

### Q: How does it compare to vector databases like Chroma?
**A:** CodeMind is simpler and lighter-weight, using SQLite + numpy for vector similarity. Perfect for single-developer projects.

## Roadmap

### Version 1.1
- [ ] Git integration for better change tracking
- [ ] Visual dashboard for browsing project memory
- [ ] Enhanced file relationship detection
- [ ] Performance optimizations

### Version 1.2
- [ ] Team collaboration features
- [ ] Conflict detection (duplicate functionality warnings)
- [ ] Learning from rejected suggestions
- [ ] Advanced AST-based code analysis

### Version 2.0
- [ ] Multi-project workspace support
- [ ] Cloud sync for team memory sharing
- [ ] Plugin system for custom analyzers
- [ ] Integration with popular IDEs

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/codemind/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/codemind/discussions)
- 📧 **Contact**: your.email@example.com

---

*CodeMind - Because AI should remember what it just built* 🧠✨