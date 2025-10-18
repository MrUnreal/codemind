# Publishing CodeMind MCP Server

This guide explains how to publish CodeMind to make it discoverable and installable through VS Code's MCP ecosystem.

## đź“¦ Publishing Options

### Option 1: PyPI Package (Recommended for Python MCP Servers)

CodeMind is a Python-based MCP server, so publishing to PyPI is the most natural approach.

#### 1. Prepare Package Structure

```bash
# Ensure you have proper package structure (already done!)
codemind/
â”śâ”€â”€ codemind.py          # Entry point
â”śâ”€â”€ codemind/            # Package directory
â”‚   â”śâ”€â”€ __init__.py
â”‚   â”śâ”€â”€ indexing.py
â”‚   â”śâ”€â”€ parsers.py
â”‚   â”śâ”€â”€ workspace.py
â”‚   â””â”€â”€ tools/
â”śâ”€â”€ setup.py             # Setup configuration (create this)
â”śâ”€â”€ pyproject.toml       # Modern Python packaging (create this)
â”śâ”€â”€ README.md
â”śâ”€â”€ LICENSE
â””â”€â”€ requirements.txt
```

#### 2. Create `pyproject.toml`

See the `pyproject.toml` file created in this directory.

#### 3. Create `setup.py` (for backward compatibility)

See the `setup.py` file created in this directory.

#### 4. Build and Publish to PyPI

```bash
# Install build tools
pip install build twine

# Build distribution packages
python -m build

# Test upload to TestPyPI first (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

#### 5. Users Install via pip

```bash
# Install globally
pip install mcp-codemind

# Or in a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install mcp-codemind
```

#### 6. VS Code Configuration

Users add to their VS Code settings (`settings.json`):

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["-m", "codemind"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Or with full path:

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "C:/Python311/python.exe",
      "args": ["-m", "codemind"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

---

### Option 2: NPM Package Wrapper

For better VS Code integration, you can create an npm wrapper that launches the Python server.

#### 1. Create `package.json`

See the `package.json` file created in this directory.

#### 2. Create Node.js Wrapper

See the `bin/codemind.js` file created in this directory.

#### 3. Publish to npm

```bash
# Login to npm
npm login

# Publish package
npm publish
```

#### 4. Users Install via npm

```bash
# Install globally
npm install -g mcp-codemind

# Or locally in project
npm install mcp-codemind
```

#### 5. VS Code Configuration

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "npx",
      "args": ["mcp-codemind"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

---

### Option 3: GitHub Releases + Manual Installation

For users who want to install from source:

#### 1. Create GitHub Release

```bash
# Tag version
git tag -a v2.0.1 -m "Release v2.0.1: Auto-reindex feature"
git push origin v2.0.1

# Create release on GitHub with:
# - Release notes
# - Changelog
# - Installation instructions
# - Pre-built .whl or .tar.gz files
```

#### 2. Installation Instructions

```bash
# Clone repository
git clone https://github.com/MrUnreal/codemind.git
cd codemind

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure VS Code
# Add to settings.json with full path to python.exe and codemind.py
```

---

## đźŽŻ Recommended Approach

**Use Option 1 (PyPI)** because:

- âś… Native Python distribution
- âś… No npm/Node.js dependency
- âś… Easy dependency management via pip
- âś… Users can install in virtual environments
- âś… Simple version updates (`pip install --upgrade mcp-codemind`)

**Add Option 2 (npm wrapper)** for convenience:

- âś… Easier discovery in npm ecosystem
- âś… Better VS Code integration
- âś… Familiar for JavaScript/TypeScript users
- âš ď¸Ź Requires both Python and Node.js

---

## đź“‹ Pre-Publishing Checklist

- [ ] **Version number** updated in all files
- [ ] **README.md** is comprehensive and up-to-date
- [ ] **CHANGELOG.md** includes latest changes
- [ ] **LICENSE** file exists (MIT recommended)
- [ ] **All tests pass** (`python tests/run_all_tests.py`)
- [ ] **Requirements.txt** has all dependencies
- [ ] **Documentation** is complete (USAGE_GUIDE.md, etc.)
- [ ] **Example configurations** provided
- [ ] **Git tags** created for version
- [ ] **GitHub repository** is public

---

## đź”§ Post-Publishing Tasks

1. **Update README badges**:

   - PyPI version badge
   - Download count
   - License badge
   - Build status

2. **Announce release**:

   - GitHub Discussions
   - Reddit (r/vscode, r/Python)
   - Twitter/X
   - Dev.to article

3. **Monitor issues**:

   - GitHub Issues for bug reports
   - Respond to installation questions

4. **Keep documentation updated**:
   - Update examples for new features
   - Maintain compatibility with VS Code updates

---

## đź“š Resources

- **PyPI**: https://pypi.org/
- **npm**: https://www.npmjs.com/
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **VS Code MCP Documentation**: https://code.visualstudio.com/docs/copilot/copilot-mcp
- **Python Packaging Guide**: https://packaging.python.org/

---

## đźš€ Quick Publish Commands

### PyPI (Python)

```bash
python -m build
twine upload dist/*
```

### npm (Node.js wrapper)

```bash
npm publish
```

### Both

```bash
# Publish to PyPI first
python -m build && twine upload dist/*

# Then npm
npm publish
```

---

## âš ď¸Ź Important Notes

1. **Package names**:

   - PyPI: `mcp-codemind` (check availability first!)
   - npm: `mcp-codemind` or `@mrunreal/codemind`

2. **Version sync**: Keep versions synchronized across:

   - `pyproject.toml`
   - `setup.py`
   - `package.json`
   - `codemind/__init__.py`

3. **Python version support**: Specify minimum Python version (3.8+)

4. **Dependencies**: Pin major versions but allow minor updates

   - `fastmcp>=0.2.0,<1.0.0`
   - `sentence-transformers>=2.2.0,<3.0.0`

5. **Entry point**: Ensure `codemind.py` can run as module (`python -m codemind`)

---

## đźŽ Making It Official

To be listed in VS Code's MCP server directory:

1. Publish to PyPI or npm
2. Create comprehensive documentation
3. Provide clear installation instructions
4. Submit to MCP server registry (if exists)
5. Ensure compatibility with latest VS Code and Copilot

---

**Ready to publish?** Start with PyPI, test thoroughly, then add npm wrapper for wider reach! đźš€

