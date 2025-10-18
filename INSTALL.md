# CodeMind Installation Guide

Complete installation instructions for different platforms and use cases.

## đźš€ Quick Install

### Via pip (Recommended - when published to PyPI)

```bash
pip install mcp-codemind
```

### Via npm (when published to npm)

```bash
npm install -g mcp-codemind
```

### From Source (Development)

```bash
git clone https://github.com/yourusername/codemind.git
cd codemind
pip install -r requirements.txt
```

---

## đź“‹ Prerequisites

- **Python 3.8+** (required)
- **pip** (Python package manager)
- **Git** (for source installation)
- **Node.js 14+** (optional, only for npm installation)

---

## đź”§ Detailed Installation

### Option 1: PyPI Installation (Recommended)

Once published to PyPI, users can install directly:

```bash
# Install globally
pip install mcp-codemind

# Or in a virtual environment (recommended)
python -m venv codemind-env
source codemind-env/bin/activate  # Linux/Mac
codemind-env\Scripts\activate     # Windows
pip install mcp-codemind

# Verify installation
python -m codemind --version
```

### Option 2: npm Installation

Once published to npm, users can install via npm:

```bash
# Install globally
npm install -g mcp-codemind

# Verify installation
npx mcp-codemind --version
```

**Note**: npm installation will automatically install Python dependencies via postinstall script.

### Option 3: From Source (Development)

For developers or users who want the latest features:

```bash
# Clone repository
git clone https://github.com/yourusername/codemind.git
cd codemind

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify it works
python codemind.py
```

---

## âš™ď¸Ź VS Code Configuration

### Configuration Method 1: Settings UI

1. Open VS Code Settings (Ctrl+, or Cmd+,)
2. Search for "MCP"
3. Click "Edit in settings.json"
4. Add CodeMind configuration

### Configuration Method 2: Direct JSON Edit

Open VS Code settings (`settings.json`):

- **Windows**: `%APPDATA%\Code\User\settings.json`
- **Mac**: `~/Library/Application Support/Code/User/settings.json`
- **Linux**: `~/.config/Code/User/settings.json`

### For PyPI Installation

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

**With virtual environment** (full path):

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "C:/path/to/codemind-env/Scripts/python.exe",
      "args": ["-m", "codemind"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### For npm Installation

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

Or with global installation:

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "codemind",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### For Source Installation

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "E:/Projects/Python/codemind/.venv/Scripts/python.exe",
      "args": ["E:/Projects/Python/codemind/codemind.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

---

## âś… Verify Installation

### Test 1: Check Server Starts

```bash
# For PyPI
python -m codemind

# For npm
npx mcp-codemind

# For source
python codemind.py
```

You should see MCP server initialization messages in stderr.

### Test 2: VS Code Integration

1. Restart VS Code after configuration
2. Open a project folder
3. Open GitHub Copilot chat
4. Try a test prompt:
   ```
   @codemind search for "main function"
   ```

### Test 3: Check Logs

```bash
# Check session logs
ls .codemind/logs/

# View latest log
# Windows:
type .codemind\logs\session_*.log | more

# Linux/Mac:
tail -f .codemind/logs/session_*.log
```

---

## đź› Troubleshooting

### Issue: "Python not found"

**Solution**: Ensure Python is in your PATH

```bash
# Verify Python
python --version

# If not found, add to PATH or use full path in VS Code config
```

### Issue: "Module 'codemind' not found"

**Solution**: Install dependencies

```bash
pip install -r requirements.txt

# Or for PyPI
pip install mcp-codemind
```

### Issue: "MCP server not responding"

**Solution 1**: Check logs

```bash
cat .codemind/logs/session_*.log
```

**Solution 2**: Test server manually

```bash
python -m codemind
# Should show server initialization
```

**Solution 3**: Restart VS Code

```bash
# Completely quit and restart VS Code
```

### Issue: "ImportError: sentence-transformers"

**Solution**: Install with pip upgrade

```bash
pip install --upgrade sentence-transformers
```

### Issue: "Permission denied"

**Solution**: On Linux/Mac, make codemind.js executable

```bash
chmod +x bin/codemind.js
```

---

## đź”„ Updating

### PyPI Update

```bash
pip install --upgrade mcp-codemind
```

### npm Update

```bash
npm update -g mcp-codemind
```

### Source Update

```bash
cd codemind
git pull
pip install -r requirements.txt --upgrade
```

---

## đź—‘ď¸Ź Uninstallation

### PyPI

```bash
pip uninstall mcp-codemind
```

### npm

```bash
npm uninstall -g mcp-codemind
```

### Source

```bash
# Remove directory
rm -rf codemind/

# Remove VS Code configuration
# Edit settings.json and remove "codemind" entry
```

### Clean Up Databases

```bash
# Remove workspace databases (optional)
# Windows:
rmdir /s .codemind

# Linux/Mac:
rm -rf .codemind
```

---

## đźŚ Platform-Specific Notes

### Windows

- Use backslashes `\` or forward slashes `/` in paths
- Use `.venv\Scripts\activate` for virtual environments
- Use `python` command (usually works)
- PowerShell might require execution policy changes

### macOS

- Use `python3` command explicitly
- May need to install Xcode Command Line Tools
- Use `source .venv/bin/activate` for virtual environments

### Linux

- Use `python3` command
- May need `python3-venv` package: `sudo apt install python3-venv`
- Use `source .venv/bin/activate` for virtual environments

---

## đź“š Next Steps

After installation:

1. **Read Usage Guide**: See `USAGE_GUIDE.md` for example prompts
2. **Run Tests**: `python tests/run_all_tests.py`
3. **Try Examples**: See `docs/EXAMPLES.md`
4. **Configure**: Review `docs/CONFIGURATION.md`

---

## đź† Getting Help

- **GitHub Issues**: https://github.com/yourusername/codemind/issues
- **Documentation**: https://github.com/yourusername/codemind/blob/master/README.md
- **FAQ**: `docs/FAQ.md`

---

**Installation complete?** Start using CodeMind with natural language prompts in Copilot! đźŽ‰

