# Contributing to CodeMind 🧠

Thank you for your interest in contributing to CodeMind! This guide will help you get started with contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

---

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for everyone. By participating, you agree to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards others

Please report unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating a bug report:
1. **Check existing issues** to avoid duplicates
2. **Use the latest version** to ensure the bug hasn't been fixed
3. **Collect information** about your environment

When creating a bug report, include:
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, CodeMind version)
- Log files from `.codemind/logs/` if applicable
- Screenshots or error messages

**Example:**
```
Title: search_existing_code returns empty results on Windows

Environment:
- Windows 11
- Python 3.11.5
- CodeMind v2.0.1

Steps to Reproduce:
1. Install CodeMind on Windows
2. Run search_existing_code("authentication")
3. Returns empty list despite files existing

Expected: Should find auth-related files
Actual: Returns []

Log: [attach .codemind/logs/session_*.log]
```

### 💡 Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- Clear use case explaining why this would be useful
- Detailed description of the proposed feature
- Examples of how it would work
- Potential implementation approach (optional)

### 📝 Improving Documentation

Documentation improvements are highly valued:
- Fix typos or unclear explanations
- Add missing examples
- Improve code comments
- Create tutorials or guides
- Translate documentation

### 💻 Contributing Code

We welcome code contributions for:
- New tools or features
- Bug fixes
- Performance improvements
- Code quality enhancements
- Test coverage improvements

---

## Getting Started

### Prerequisites

- **Python 3.8 or higher** (3.10+ recommended) (check: `python --version`)
- **Git** (check: `git --version`)
- **Text editor** (VS Code recommended)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/codemind.git
   cd codemind
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/MrUnreal/codemind.git
   ```

### Set Up Development Environment

1. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies** (optional):
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

5. **Verify installation**:
   ```bash
   python codemind.py
   # Should start MCP server without errors
   ```

---

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Changes

- **Keep changes focused** - One feature or fix per branch
- **Write clear commit messages** - Explain what and why
- **Test as you go** - Run tests frequently
- **Update documentation** - If you change behavior

### 3. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add semantic search for TypeScript files"
```

**Good commit messages:**
- `Add support for Java file parsing`
- `Fix unicode handling in Windows paths`
- `Improve search performance for large codebases`
- `Update documentation for multi-workspace setup`

**Bad commit messages:**
- `fix bug`
- `update stuff`
- `WIP`

### 4. Keep Your Branch Updated

Regularly sync with upstream:

```bash
git fetch upstream
git rebase upstream/master
```

### 5. Run Tests

Before submitting, ensure all tests pass:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=codemind --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_01_basic.py -v
```

All tests should pass ✅

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Choose your branch
4. Fill in the PR template with:
   - Description of changes
   - Related issue number (if applicable)
   - Testing performed
   - Screenshots (if UI changes)

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

```python
# ✅ Good
def search_existing_code(query: str, workspace_root: str = ".") -> List[dict]:
    """
    Search for existing code matching the query.
    
    Args:
        query: Search query string
        workspace_root: Root directory of workspace
        
    Returns:
        List of matching files with scores
    """
    results = perform_search(query, workspace_root)
    return format_results(results)

# ❌ Bad
def search(q, ws="."):
    r = do_search(q, ws)
    return r
```

### Key Guidelines

1. **Type hints** - Use type hints for all function parameters and returns
2. **Docstrings** - Write clear docstrings for all public functions
3. **Line length** - Maximum 100 characters
4. **Naming**:
   - Functions: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_CASE`
   - Private: `_leading_underscore`

5. **Imports** - Group and sort imports:
   ```python
   # Standard library
   import os
   import sys
   
   # Third-party
   from sentence_transformers import SentenceTransformer
   
   # Local
   from codemind.workspace import get_workspace_db
   ```

### Code Formatting

We use **Black** for consistent formatting:

```bash
# Format all Python files
black codemind/ tests/

# Check formatting without changes
black --check codemind/ tests/
```

### Linting

We use **flake8** for linting:

```bash
flake8 codemind/ tests/
```

### Type Checking

We use **mypy** for static type checking:

```bash
mypy codemind/
```

---

## Testing Guidelines

### Test Structure

Tests are organized in `tests/` directory:

```
tests/
├── test_01_basic.py          # Basic tool functionality (19 tests)
├── test_02_chains.py          # Multi-tool workflows (6 scenarios)
├── test_03_complex.py         # Edge cases and stress tests (30 tests)
├── test_comprehensive.py      # Infrastructure validation
├── test_curveballs.py         # Advanced edge cases (35 tests)
└── final_validation.py        # Production readiness check
```

### Writing Tests

```python
import pytest
from codemind.tools.search import search_existing_code

def test_search_existing_code_basic():
    """Test basic semantic search functionality."""
    # Arrange
    workspace_root = "."
    query = "authentication"
    
    # Act
    results = search_existing_code(query, workspace_root)
    
    # Assert
    assert isinstance(results, list)
    assert len(results) > 0
    assert "file_path" in results[0]
    assert "score" in results[0]

def test_search_empty_query():
    """Test search with empty query returns helpful error."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        search_existing_code("", ".")
```

### Test Coverage Requirements

- **New features**: Must have tests covering main functionality
- **Bug fixes**: Include test that would have caught the bug
- **Edge cases**: Test boundary conditions
- **Error handling**: Test failure modes

Aim for >80% code coverage for new code.

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_01_basic.py -v

# Specific test function
python -m pytest tests/test_01_basic.py::test_search_existing_code_basic -v

# With coverage report
python -m pytest tests/ --cov=codemind --cov-report=html
```

---

## Documentation Guidelines

### Where to Document

1. **README.md** - Quick start and overview
2. **USAGE_GUIDE.md** - Detailed usage examples
3. **docs/TOOLS.md** - Tool reference documentation
4. **docs/EXAMPLES.md** - Real-world scenarios
5. **Docstrings** - In-code documentation

### Writing Documentation

**Be clear and concise:**
```markdown
✅ Good:
## Installation
Install CodeMind using pip:
```bash
pip install mcp-codemind
```

❌ Bad:
## Installation
You can install this software package by using the pip command.
```

**Include examples:**
```markdown
✅ Good:
Use `search_existing_code` to find files:
```python
results = search_existing_code("JWT authentication")
# Returns: [{"file_path": "auth/jwt.py", "score": 0.95}]
```

❌ Bad:
Use search_existing_code to search for code.
```

**Update docs when changing code:**
- If you change a function signature, update docstrings
- If you add a feature, update relevant documentation
- If you fix a bug, consider adding troubleshooting note

---

## Submitting Changes

### Before Submitting

**Checklist:**
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Added tests for new functionality
- [ ] Updated documentation
- [ ] Commit messages are clear
- [ ] Branch is up to date with master

### Pull Request Process

1. **Create Pull Request** on GitHub
2. **Fill in PR template** completely
3. **Wait for review** - Be patient, maintainers review as time permits
4. **Address feedback** - Respond to comments and make requested changes
5. **Keep PR updated** - Resolve conflicts if master changes

### Review Process

**What reviewers look for:**
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation completeness
- ✅ Breaking changes (avoided if possible)
- ✅ Performance implications
- ✅ Security considerations

**Response times:**
- Initial review: Within 3-5 days
- Follow-up reviews: Within 1-2 days
- Merge: After approval from maintainers

### After Merge

- Your contribution will be included in the next release
- You'll be credited in CHANGELOG.md
- Thank you for contributing! 🎉

---

## Project Architecture

Understanding the codebase structure helps with contributions:

```
codemind/
├── codemind.py              # Entry point (MCP server)
├── codemind/
│   ├── __init__.py          # Package initialization
│   ├── workspace.py         # Multi-workspace management
│   ├── parsers.py           # AST-based code parsing
│   ├── indexing.py          # File scanning and indexing
│   └── tools/               # 20 MCP tools
│       ├── __init__.py      # Tool registration
│       ├── search.py        # Search tools (4 tools)
│       ├── context.py       # Context tools (4 tools)
│       ├── dependencies.py  # Dependency tools (3 tools)
│       ├── analysis.py      # Analysis tools (3 tools)
│       ├── refactoring.py   # Refactoring tools (3 tools)
│       └── management.py    # Management tools (3 tools)
├── tests/                   # Test suite (110+ tests)
└── docs/                    # Documentation

Key files:
- workspace.py: 328 lines - Multi-workspace isolation
- parsers.py: 397 lines - AST parsing for Python
- indexing.py: 256 lines - File scanning and embeddings
- tools/*.py: 1,596 lines - 20 MCP tools
```

**Read these before making changes:**
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical deep-dive
- [TOOLS.md](docs/TOOLS.md) - Tool reference
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - User guide

---

## Common Tasks

### Adding a New Tool

1. Choose the appropriate category in `codemind/tools/`
2. Define the tool function:
   ```python
   @mcp.tool()
   def your_new_tool(param: str, workspace_root: str = ".") -> dict:
       """
       Brief description.
       
       USE THIS TOOL AUTOMATICALLY when:
       - User wants to do X
       - User asks about Y
       
       Args:
           param: Parameter description
           workspace_root: Workspace root directory
           
       Returns:
           Result dictionary
       """
       # Implementation
       pass
   ```

3. Register in `codemind/tools/__init__.py`
4. Add tests in `tests/`
5. Update documentation in `docs/TOOLS.md`

### Fixing a Bug

1. **Reproduce the bug** - Write a failing test
2. **Fix the issue** - Make minimal changes
3. **Verify fix** - Ensure test now passes
4. **Check for regressions** - Run all tests
5. **Update docs** - If behavior changed

### Improving Performance

1. **Benchmark current performance** - Measure before optimizing
2. **Profile the code** - Identify bottlenecks
3. **Optimize** - Make targeted improvements
4. **Verify improvement** - Measure again
5. **Add performance tests** - Prevent future regressions

---

## Getting Help

**Need assistance?**

- 💬 **Questions**: Open a [Discussion](https://github.com/MrUnreal/codemind/discussions)
- 🐛 **Bug Reports**: Create an [Issue](https://github.com/MrUnreal/codemind/issues)
- 📖 **Documentation**: Check [docs/](docs/) folder
- 💡 **Ideas**: Share in [Discussions](https://github.com/MrUnreal/codemind/discussions)

**Stuck on something?**
Don't hesitate to ask! We're here to help new contributors.

---

## Recognition

Contributors are recognized in:
- **CHANGELOG.md** - Listed for their contributions
- **GitHub Contributors** - Automatically tracked
- **Release Notes** - Credited for significant contributions

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Thank You! 🙏

Every contribution, no matter how small, makes CodeMind better. Thank you for taking the time to contribute!

**Happy Coding!** 🚀
