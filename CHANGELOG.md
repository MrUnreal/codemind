# Changelog

All notable changes to CodeMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.1] - 2024-10-17

### Added

- Enhanced all 20 tool docstrings with "USE THIS TOOL AUTOMATICALLY when:" sections
- Proactive tool invocation - Copilot now automatically uses tools during reasoning
- Comprehensive usage guide (USAGE_GUIDE.md) with natural language prompts
- Enhancement completion report documenting the proactive feature implementation

### Changed

- Tools now trigger automatically based on user intent (no explicit tool requests needed)
- Improved Copilot integration with detailed trigger conditions in docstrings

### Documentation

- Consolidated documentation structure
- Created unified USAGE_GUIDE.md merging prompt guide and proactive usage
- Cleaned up README.md (removed corrupted duplicate content)
- Added CHANGELOG.md for version tracking

---

## [2.0.0] - 2024-10-15

### 🎉 Major Release - Complete Package Restructure

### Added

- **Multi-Workspace Support**: Work with multiple projects simultaneously

  - Each workspace gets isolated SQLite database
  - Independent configuration per workspace
  - Cached resources (DB, config, embeddings)
  - All tools accept `workspace_root` parameter

- **Modular Package Structure**: Refactored from monolithic file to clean modules

  - `codemind/workspace.py` - Workspace management (328 lines)
  - `codemind/parsers.py` - AST-based parsing (397 lines)
  - `codemind/indexing.py` - File scanning (256 lines)
  - `codemind/tools/` - 6 tool category modules (1,596 lines)

- **Production-Quality AST Parsing**: Integration with radon for accurate metrics

  - McCabe complexity
  - Maintainability index
  - Code smells detection

- **Zero-LLM Static Analysis Tools** (3 new):
  - `get_code_metrics_summary` - Comprehensive code metrics
  - `find_configuration_inconsistencies` - Config analysis and secret detection
  - `get_import_graph` - Dependency visualization with circular detection

### Changed

- **Entry Point**: Reduced from 2506 lines to 63 lines of clean bootstrap code
- **Tool Registration**: Centralized in `codemind/tools/__init__.py`
- **Database Management**: Workspace-aware with connection pooling
- **Configuration**: Per-workspace config loading with caching

### Improved

- **Test Coverage**: 110+ tests across 6 suites (99%+ pass rate)

  - `test_01_basic.py` - 19 tests for individual tool validation
  - `test_02_chains.py` - 6 scenarios for tool chaining
  - `test_03_complex.py` - 30 tests for edge cases
  - `test_comprehensive.py` - Infrastructure validation
  - `test_curveballs.py` - 35 advanced edge cases
  - `final_validation.py` - Production readiness check

- **Documentation**: Complete reorganization

  - Short, scannable README.md
  - Detailed docs in `/docs` directory
  - Architecture documentation
  - Multi-workspace guide
  - Migration guide from v1.x

- **VS Code Integration**: 8 debug configurations for all test scenarios

### Fixed

- Path resolution issues in multi-workspace scenarios
- Embedding model caching bugs
- SQL injection vulnerabilities (parameterized queries)
- Unicode handling in file parsing

### Breaking Changes

- **None!** Fully backward compatible with v1.x
- Default `workspace_root="."` maintains v1 behavior
- Existing configurations work unchanged

---

## [1.1.0] - 2024-10-01

### Added

- **Decision Tracking**: Store and query architectural decisions

  - `record_decision` - Store decisions with rationale
  - `list_all_decisions` - Query decision history

- **Enhanced Dependency Analysis**:

  - `find_dependencies` - Bidirectional import analysis
  - `get_call_tree` - Function call hierarchies

- **Refactoring Safety Tools**:
  - `check_breaking_changes` - Impact analysis before refactoring
  - `find_usage_examples` - Real-world usage patterns
  - `get_test_coverage` - Test coverage estimates

### Improved

- Semantic search accuracy (sentence-transformers v2.2.0)
- File indexing performance (50% faster)
- Database query optimization

---

## [1.0.0] - 2024-09-15

### 🎉 Initial Release

### Added

- **Core Functionality**:

  - Semantic code search with embeddings
  - File context extraction
  - Recent changes tracking
  - Workspace indexing

- **Search Tools** (4):

  - `search_existing_code` - Semantic search
  - `check_functionality_exists` - Quick existence check
  - `search_by_export` - Find definitions
  - `get_similar_files` - Similarity search

- **Context Tools** (4):

  - `get_file_context` - File metadata
  - `query_recent_changes` - Change history
  - `record_decision` - Store decisions
  - `list_all_decisions` - Query decisions

- **Management Tools** (4):

  - `force_reindex` - Full project rescan
  - `index_file` - Single file indexing
  - `find_todo_and_fixme` - Technical debt tracking
  - `get_file_history_summary` - Git history

- **Infrastructure**:
  - SQLite database for persistence
  - sentence-transformers for semantic search
  - FastMCP framework for MCP protocol
  - GitHub Copilot integration

### Technical Details

- **Language**: Python 3.10+
- **Dependencies**: fastmcp, sentence-transformers, GitPython
- **Database**: SQLite3 (1-5MB per project)
- **Embedding Model**: all-MiniLM-L6-v2 (~80MB)

---

## Version History Summary

| Version | Date       | Key Features                                          | Tools | Lines of Code |
| ------- | ---------- | ----------------------------------------------------- | ----- | ------------- |
| 2.0.1   | 2024-10-17 | Proactive tools, enhanced docs                        | 20    | ~2,600        |
| 2.0.0   | 2024-10-15 | Multi-workspace, modular structure, zero-LLM analysis | 20    | ~2,577        |
| 1.1.0   | 2024-10-01 | Decision tracking, refactoring safety                 | 16    | ~2,000        |
| 1.0.0   | 2024-09-15 | Initial release, core functionality                   | 12    | ~1,500        |

---

## Migration Guides

### Upgrading from v1.x to v2.x

**Good news**: Fully backward compatible! No changes required.

**To use new features**:

1. Specify `workspace_root` parameter for multi-workspace scenarios
2. Use new zero-LLM analysis tools (`get_code_metrics_summary`, etc.)
3. Leverage automatic tool invocation (v2.0.1+)

See [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) for details.

---

## Roadmap

### v2.1.0 (Planned)

- [ ] Enhanced git integration
- [ ] Visual dashboard for project insights
- [ ] Performance optimizations for large codebases
- [ ] Support for more programming languages

### v2.2.0 (Planned)

- [ ] Team collaboration features
- [ ] Conflict detection (duplicate functionality warnings)
- [ ] Learning from rejected suggestions
- [ ] Plugin system for custom analyzers

### v3.0.0 (Future)

- [ ] Cloud sync for team memory sharing
- [ ] Integration with popular IDEs beyond VS Code
- [ ] Advanced ML-based code analysis
- [ ] Real-time collaboration features

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/MrUnreal/codemind.git
cd codemind
pip install -r requirements.txt
python tests/run_all_tests.py
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built with ❤️ using:

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP protocol framework
- [sentence-transformers](https://www.sbert.net/) - Semantic embeddings
- [radon](https://radon.readthedocs.io/) - Code metrics
- [GitPython](https://gitpython.readthedocs.io/) - Git integration

---

_For detailed documentation, see [docs/](docs/) directory._
