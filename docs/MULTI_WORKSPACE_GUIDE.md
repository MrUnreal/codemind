# CodeMind v2.0 - Multi-Workspace Usage Guide

## Overview

CodeMind v2.0 introduces workspace-aware tools that can work with multiple projects simultaneously. Each tool now accepts an optional `workspace_root` parameter.

## Basic Usage

### Single Workspace (Default)

When working with a single project, no changes needed! All tools default to current directory:

```python
# These all work on current directory
search_existing_code("authentication")
get_file_context("src/main.py")
find_dependencies("utils.py")
```

### Multiple Workspaces

To work with multiple projects, pass the `workspace_root` parameter:

```python
# Search in Project A
search_existing_code("authentication", workspace_root="/path/to/project-a")

# Search in Project B
search_existing_code("authentication", workspace_root="/path/to/project-b")

# Get metrics for Project A
get_code_metrics_summary(workspace_root="/path/to/project-a")

# Get metrics for Project B
get_code_metrics_summary(workspace_root="/path/to/project-b")
```

## Workspace Isolation

Each workspace maintains:
- ✅ **Separate Database**: `.codemind/<workspace_hash>/memory.db`
- ✅ **Independent Configuration**: Loaded from workspace root
- ✅ **Cached Resources**: DB connections, configs, embeddings
- ✅ **No Cross-Contamination**: Results never mixed between workspaces

## Real-World Examples

### Example 1: Compare Implementations Across Projects

```python
# Find authentication in frontend
frontend_auth = search_existing_code(
    "authentication",
    workspace_root="/home/user/projects/frontend"
)

# Find authentication in backend
backend_auth = search_existing_code(
    "authentication",
    workspace_root="/home/user/projects/backend"
)

# Compare approaches
print("Frontend:", frontend_auth)
print("Backend:", backend_auth)
```

### Example 2: Multi-Project Quality Analysis

```python
# Analyze codebase A
metrics_a = get_code_metrics_summary(
    workspace_root="/home/user/projects/service-a"
)

# Analyze codebase B
metrics_b = get_code_metrics_summary(
    workspace_root="/home/user/projects/service-b"
)

# Compare quality metrics
```

### Example 3: Dependency Analysis Across Microservices

```python
# Check dependencies in each microservice
auth_deps = find_dependencies(
    "auth.py",
    workspace_root="/home/user/microservices/auth-service"
)

user_deps = find_dependencies(
    "user.py",
    workspace_root="/home/user/microservices/user-service"
)
```

### Example 4: Track Decisions Across Projects

```python
# Record decision in Project A
record_decision(
    description="Switched to JWT for authentication",
    reasoning="Better scalability and stateless design",
    workspace_root="/home/user/projects/api-v2",
    affected_files=["auth.py", "middleware.py"]
)

# Record decision in Project B
record_decision(
    description="Migrated from REST to GraphQL",
    reasoning="Client flexibility and reduced over-fetching",
    workspace_root="/home/user/projects/mobile-app",
    affected_files=["api/index.ts"]
)

# Query decisions per project
decisions_a = list_all_decisions(workspace_root="/home/user/projects/api-v2")
decisions_b = list_all_decisions(workspace_root="/home/user/projects/mobile-app")
```

## Configuration

### Per-Workspace Configuration

Each workspace can have its own `codemind_config.json`:

```
/home/user/projects/
├── project-a/
│   ├── codemind_config.json  # Config for Project A
│   └── src/...
└── project-b/
    ├── codemind_config.json  # Config for Project B
    └── src/...
```

**project-a/codemind_config.json:**
```json
{
  "watched_extensions": [".py", ".js"],
  "embedding_model": "all-MiniLM-L6-v2"
}
```

**project-b/codemind_config.json:**
```json
{
  "watched_extensions": [".ts", ".tsx", ".js"],
  "embedding_model": "all-mpnet-base-v2"
}
```

### VS Code Multi-Workspace Setup

**settings.json** (VS Code multi-root workspace):
```json
{
  "mcpServers": {
    "codemind-project-a": {
      "command": "python",
      "args": ["D:/Projects/Python/CodeMind/codemind.py"],
      "env": {
        "CODEMIND_WORKSPACE": "D:/Projects/ProjectA"
      }
    },
    "codemind-project-b": {
      "command": "python",
      "args": ["D:/Projects/Python/CodeMind/codemind.py"],
      "env": {
        "CODEMIND_WORKSPACE": "D:/Projects/ProjectB"
      }
    }
  }
}
```

## Performance Considerations

### Resource Caching

CodeMind caches resources per workspace for performance:

```python
_workspace_dbs = {}      # SQLite connections cached
_workspace_configs = {}  # Configs loaded once
_workspace_embeddings = {} # Models loaded once
```

### Memory Usage

- **Small Projects** (<1000 files): ~50MB per workspace
- **Medium Projects** (1000-5000 files): ~100-200MB per workspace
- **Large Projects** (>5000 files): ~300-500MB per workspace

Embedding models are **shared** between workspaces using the same model, saving memory.

### Lazy Loading

Workspaces are scanned on first use:

```python
# First call triggers scan
search_existing_code("pattern", workspace_root="/path/to/project")
# Database: ❌ Empty → ✅ Scans all files → ✅ Indexed

# Subsequent calls use cache
get_file_context("file.py", workspace_root="/path/to/project")
# Database: ✅ Already indexed → ✅ Fast lookup
```

## Migration from v1.x

### No Changes Required!

Your existing code works unchanged:

```python
# v1.x code (still works)
search_existing_code("pattern")
get_file_context("file.py")
```

### Opt-In to Multi-Workspace

When you need it, add the parameter:

```python
# v2.0 with explicit workspace
search_existing_code("pattern", workspace_root="/path/to/project")
get_file_context("file.py", workspace_root="/path/to/other/project")
```

## Troubleshooting

### Issue: "File not found" with workspace_root

**Cause:** File path relative to different workspace

**Solution:** Use paths relative to specified workspace:

```python
# ❌ Wrong - absolute path from different workspace
get_file_context(
    "/home/user/project-a/src/main.py",
    workspace_root="/home/user/project-b"
)

# ✅ Correct - relative to workspace
get_file_context(
    "src/main.py",
    workspace_root="/home/user/project-b"
)
```

### Issue: Changes not reflected

**Cause:** Database cached from previous scan

**Solution:** Force re-index:

```python
force_reindex(workspace_root="/path/to/project")
```

### Issue: High memory usage

**Cause:** Multiple large workspaces loaded

**Solution:** 
1. Close unused workspace connections (restart server)
2. Use smaller embedding models
3. Configure `max_file_size_kb` to skip large files

## Best Practices

1. **Use Relative Paths**: Always use paths relative to workspace_root
2. **One Config Per Project**: Each project should have its own codemind_config.json
3. **Explicit workspace_root**: In multi-project scenarios, always specify workspace_root
4. **Lazy Loading**: First query triggers scan, be patient for large projects
5. **Periodic Re-indexing**: Run `force_reindex()` after major changes

## API Reference

All 20 tools support `workspace_root` parameter:

### Search & Discovery
- `search_existing_code(query, workspace_root=".", limit=5)`
- `check_functionality_exists(feature_description, workspace_root=".", confidence_threshold=0.7)`
- `search_by_export(export_name, workspace_root=".", limit=10)`
- `get_similar_files(file_path, workspace_root=".", limit=5)`

### Context & History
- `get_file_context(file_path, workspace_root=".")`
- `query_recent_changes(workspace_root=".", hours=24)`
- `record_decision(description, reasoning, workspace_root=".", affected_files=None)`
- `list_all_decisions(workspace_root=".", keyword=None, limit=10)`

### Dependency Analysis
- `find_dependencies(file_path, workspace_root=".")`
- `get_import_graph(workspace_root=".", include_external=False)`
- `get_call_tree(function_name, workspace_root=".", file_path=None, depth=2)`

### Code Analysis
- `get_code_metrics_summary(workspace_root=".", detailed=False)`
- `find_configuration_inconsistencies(workspace_root=".", include_examples=True)`

### Refactoring Safety
- `check_breaking_changes(function_name, file_path, workspace_root=".")`
- `find_usage_examples(function_name, workspace_root=".", file_path=None, limit=5)`
- `get_test_coverage(file_path, workspace_root=".")`

### Index Management
- `force_reindex(workspace_root=".")`
- `index_file(file_path, workspace_root=".")`
- `find_todo_and_fixme(workspace_root=".", tag_type="TODO", search_term=None, limit=20)`
- `get_file_history_summary(file_path, workspace_root=".", days_back=90)`

---

**Happy Multi-Workspace Coding! 🚀**
