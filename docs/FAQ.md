# FAQ - Frequently Asked Questions

Common questions about CodeMind.

---

## General

### What is CodeMind?

CodeMind is a Model Context Protocol (MCP) server that gives GitHub Copilot memory and understanding of your codebase through 20 specialized tools for code search, analysis, and refactoring safety.

---

### How does it work?

```mermaid
graph LR
    A[You Ask Copilot] --> B[Copilot Uses CodeMind Tools]
    B --> C[CodeMind Analyzes Codebase]
    C --> D[Returns Context to Copilot]
    D --> E[Copilot Gives Smart Response]
    
    style B fill:#9C27B0
    style C fill:#4CAF50
```

CodeMind indexes your code, stores it in a local SQLite database with semantic embeddings, and provides tools that Copilot can call to understand your project.

---

### Is it free?

Yes! CodeMind is open-source (MIT License) and runs entirely on your machine. No subscriptions, no API calls, no data sent externally.

---

## Privacy & Security

### Does CodeMind send my code anywhere?

**No**. CodeMind runs 100% locally:
- ✅ All processing happens on your machine
- ✅ Database stored in your project (`.codemind/`)
- ✅ No network calls to external services
- ✅ No telemetry or analytics
- ✅ Your code never leaves your computer

---

### How is my data stored?

```
YourProject/
└── .codemind/
    ├── memory.db        # SQLite database (1-5MB)
    │   ├── File metadata
    │   ├── Semantic embeddings
    │   ├── Decisions
    │   └── Change history
    └── logs/            # Session logs (optional)
        └── session_*.log
```

**Storage**: 1-5MB for typical projects  
**Location**: Local filesystem only  
**Backup**: Add `.codemind/` to `.gitignore`

---

### Can I delete the `.codemind` directory?

Yes. CodeMind will recreate it and reindex when needed. You might want to delete it to:
- Free up disk space
- Start fresh
- Fix database corruption

```bash
rm -rf .codemind
# Next tool call will recreate and reindex
```

---

## Installation & Setup

### What are the requirements?

- **Python**: 3.8 or higher (3.10+ recommended)
- **VS Code**: Latest version
- **GitHub Copilot**: Extension installed
- **OS**: Windows, macOS, or Linux

---

### Why Python 3.8+?

CodeMind is compatible with Python 3.8+ for broader compatibility:
- Works on most modern systems
- Supports all major Python 3 features
- Type hints support
- Python 3.10+ recommended for best performance and latest features

---

### Do I need GitHub Copilot?

Not necessarily. CodeMind works with any MCP-compatible client:
- ✅ GitHub Copilot (primary target)
- ✅ Claude Desktop (via MCP)
- ✅ Other MCP clients

---

### How do I update CodeMind?

```bash
cd /path/to/CodeMind
git pull origin master
pip install -r requirements.txt
# Restart VS Code or server
```

---

## Usage

### Which languages does CodeMind support?

**Default support**:
- Python (best support - AST-based)
- JavaScript, TypeScript, JSX, TSX
- Java, C#, C++, C, Go, Rust

**Custom support**: Add any extension via configuration:
```json
{
  "watched_extensions": [".py", ".rb", ".php", ".kt"]
}
```

---

### How accurate is semantic search?

**Very accurate** for understanding intent:

| Query | Finds |
|-------|-------|
| "JWT authentication" | Files implementing JWT tokens |
| "database connection" | Files managing DB connections |
| "user validation" | Files validating user input |

**Accuracy**: ~90-95% for well-described queries  
**Technology**: sentence-transformers embeddings

---

### Can CodeMind detect code duplication?

Yes! Use `search_existing_code` before creating new files:

```
💬 "Does this project have authentication?"
→ search_existing_code("authentication")
✅ Found in src/auth/jwt.py (95% match)
```

Also use `get_similar_files` to find similar patterns.

---

### How does it handle multiple projects?

**Multi-workspace support** in v2.0:

```python
# Project A
search_existing_code("auth", workspace_root="/projects/api")

# Project B
search_existing_code("auth", workspace_root="/projects/frontend")
```

Each workspace gets:
- ✅ Isolated database
- ✅ Independent configuration
- ✅ Separate embeddings
- ✅ No cross-contamination

---

## Performance

### How much memory does it use?

**Typical usage**:
- Small project (100 files): ~50MB
- Medium project (1,000 files): ~150MB
- Large project (10,000 files): ~500MB

**Factors**:
- Embedding model size (~90MB)
- Indexed file count
- Embedding dimensions

---

### How long does indexing take?

| Project Size | Initial Index | Incremental Update |
|--------------|---------------|-------------------|
| 100 files | 2 seconds | 0.1 seconds |
| 1,000 files | 15 seconds | 0.5 seconds |
| 10,000 files | 3 minutes | 3 seconds |

**Incremental updates** are fast - only changed files are reindexed.

---

### Why is search slow?

**Potential causes**:

1. **First query**: Embedding model loads (~2 seconds)
2. **Large codebase**: 10k+ files (~1-2 seconds)
3. **No index**: Lazy scan triggered (~10-30 seconds)

**Solutions**:
```json
{
  "embedding_model": "paraphrase-MiniLM-L3-v2",  // Faster model
  "max_files": 5000,                              // Limit files
  "lazy_scan": false                              // Index at startup
}
```

---

### Can I speed up CodeMind?

Yes! Several optimizations:

```json
{
  "embedding_model": "paraphrase-MiniLM-L3-v2",  // Fastest model
  "max_file_size_kb": 300,                       // Skip large files
  "watched_extensions": [".py"],                 // Fewer extensions
  "exclude_dirs": [".git", ".venv", "node_modules"]  // Skip dirs
}
```

**Result**: 2-3x faster indexing and queries.

---

## Troubleshooting

### CodeMind isn't responding

**Checklist**:
1. Is the server running? Check terminal/logs
2. Did you restart Copilot? (`Ctrl+Shift+P` → "Copilot: Restart")
3. Check MCP settings in VS Code settings.json
4. Check logs: `.codemind/logs/session_*.log`

---

### Tools return empty results

**Common causes**:

1. **Not indexed yet**: Wait for initial scan or force reindex
   ```bash
   python -c "from codemind.tools import force_reindex; force_reindex()"
   ```

2. **Wrong workspace**: Specify correct `workspace_root`
   ```python
   search_existing_code("query", workspace_root="/correct/path")
   ```

3. **No matching files**: Query too specific or files not in `watched_extensions`

---

### Import errors when starting

**Error**:
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solution**:
```bash
pip install -r requirements.txt
```

---

### Database locked errors

**Error**:
```
sqlite3.OperationalError: database is locked
```

**Solutions**:
1. Close other CodeMind instances
2. Check for zombie processes
3. Delete `.codemind/memory.db` (will recreate)

---

### Unicode errors on Windows

**Error**:
```
UnicodeEncodeError: 'charmap' codec can't encode
```

**Solution**:
```powershell
$env:PYTHONIOENCODING='utf-8'
python codemind.py
```

Or add to your shell profile permanently.

---

## Features & Capabilities

### Can CodeMind modify my code?

**No**. CodeMind is **read-only**:
- ❌ Never modifies your files
- ❌ Never deletes files
- ✅ Only reads and analyzes
- ✅ Provides information to Copilot
- ✅ Copilot proposes changes (with your approval)

---

### Does it work offline?

**Yes**, after initial setup:
- ✅ Embedding model downloads once (~90MB)
- ✅ Then works completely offline
- ✅ No internet connection needed
- ✅ All processing local

**Only requires internet**: First run to download embedding model.

---

### Can it detect breaking changes?

Yes! Use `check_breaking_changes`:

```python
check_breaking_changes("UserModel", "models/user.py")
```

**Returns**:
- Number of call sites
- Affected files
- Severity rating
- Recommendations

---

### Does it understand my project architecture?

Yes! Several tools for architecture understanding:

- `get_import_graph()` - Visualize module relationships
- `find_dependencies()` - What imports what
- `get_call_tree()` - Function call chains
- `get_code_metrics_summary()` - Project statistics

---

### Can it track technical debt?

Yes! Use these tools:

- `find_todo_and_fixme()` - Find TODO/FIXME/HACK comments
- `get_code_metrics_summary()` - Complexity and code smells
- `find_configuration_inconsistencies()` - Config issues
- `list_all_decisions()` - Past architectural decisions

---

## Comparison

### How does it compare to GitHub Copilot Workspace?

| Feature | CodeMind | Copilot Workspace |
|---------|----------|-------------------|
| **Runs** | Locally | Cloud |
| **Privacy** | 100% private | Data sent to cloud |
| **Cost** | Free | Subscription |
| **Customization** | Highly customizable | Limited |
| **Languages** | Any (configurable) | Limited |
| **Offline** | Yes | No |

**CodeMind complements Copilot**, not replaces it.

---

### How does it compare to vector databases like Chroma?

| Feature | CodeMind | Chroma/Pinecone |
|---------|----------|-----------------|
| **Setup** | Zero config | Requires setup |
| **Storage** | SQLite | Separate DB |
| **Complexity** | Simple | More complex |
| **Use Case** | Single developer | Team/production |
| **Performance** | Fast for <50k files | Fast at any scale |

**CodeMind is simpler** for individual developers and small teams.

---

## Advanced Usage

### Can I add custom tools?

Yes! CodeMind is designed for extensibility:

1. Create new tool in `codemind/tools/`
2. Register in `codemind/tools/__init__.py`
3. Follow existing tool patterns

See **[Architecture Guide](ARCHITECTURE.md)** for details.

---

### Can I use different embedding models?

Yes! Configure via `embedding_model`:

```json
{
  "embedding_model": "all-mpnet-base-v2"  // Higher quality
}
```

**Available models**:
- `all-MiniLM-L6-v2` (default - balanced)
- `all-mpnet-base-v2` (best quality)
- `paraphrase-MiniLM-L3-v2` (fastest)
- `multi-qa-MiniLM-L6-cos-v1` (Q&A optimized)

---

### Can I contribute to CodeMind?

**Yes!** Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

See **[Architecture Guide](ARCHITECTURE.md)** for codebase overview.

---

### Can I deploy CodeMind for a team?

Yes, but consider:
- Each developer runs their own instance
- Databases are not shared (by design)
- Use `record_decision()` to share knowledge
- Consider exporting decisions to a wiki/docs

**Future**: Team collaboration features planned for v3.0.

---

## Best Practices

### Should I commit `.codemind/` to git?

**No**. Add to `.gitignore`:

```bash
echo ".codemind/" >> .gitignore
```

**Reasons**:
- Database is user-specific
- Embeddings are machine-specific
- Can be regenerated quickly

---

### How often should I reindex?

**Rarely**. CodeMind uses automatic incremental indexing:
- ✅ Detects file changes automatically
- ✅ Updates index in real-time
- ✅ Hash-based change detection

**Manual reindex**: Only after major changes or issues:
```bash
python -c "from codemind.tools import force_reindex; force_reindex()"
```

---

### What should I configure?

**Most users**: No configuration needed!

**Power users**: Consider customizing:
- `watched_extensions` - Relevant file types only
- `exclude_dirs` - Skip unnecessary directories
- `max_file_size_kb` - Adjust for your files

See **[Configuration Guide](CONFIGURATION.md)**.

---

## Getting Help

### Where can I find documentation?

**Comprehensive docs** in `docs/` folder:
- **[README](../README.md)** - Quick start
- **[Tool Reference](TOOLS.md)** - All 20 tools
- **[Examples](EXAMPLES.md)** - Real-world usage
- **[Architecture](ARCHITECTURE.md)** - Technical details
- **[Testing](TESTING.md)** - Test suite guide
- **[Configuration](CONFIGURATION.md)** - Customization
- **[Migration Guide](MIGRATION_GUIDE.md)** - Upgrading from v1.x

---

### How do I report a bug?

1. **Check logs**: `.codemind/logs/session_*.log`
2. **Search issues**: [GitHub Issues](https://github.com/MrUnreal/codemind/issues)
3. **Create issue**: Include:
   - Python version
   - CodeMind version
   - Error message
   - Steps to reproduce

---

### Where can I ask questions?

- 🐛 **Bugs**: [GitHub Issues](https://github.com/MrUnreal/codemind/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/MrUnreal/codemind/discussions)
- 📧 **Email**: Via GitHub

---

## Roadmap

### What's planned for future versions?

**v2.1** (Q1 2026):
- Cloud sync for decision sharing
- Team collaboration features
- Enhanced git integration
- Performance improvements

**v3.0** (Q2 2026):
- Multi-language support (beyond Python)
- Visual dashboard
- Plugin system
- Advanced analytics

---

## Still Have Questions?

Can't find your answer? 

- 📚 **Check docs**: [docs/](.) folder
- 💬 **Ask community**: [GitHub Discussions](https://github.com/MrUnreal/codemind/discussions)
- 🐛 **Report issue**: [GitHub Issues](https://github.com/MrUnreal/codemind/issues)

---

*Last updated: October 6, 2025*
