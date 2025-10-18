# Getting Started with CodeMind 🧠

**New to CodeMind?** This guide will walk you through everything step-by-step.

---

## What is CodeMind?

CodeMind gives GitHub Copilot a "memory" of your codebase. Instead of Copilot creating duplicate files or forgetting what you just discussed, CodeMind helps it:

- 🔍 **Find existing code** before creating new files
- 🧠 **Remember decisions** you've made
- đź"— **Understand relationships** between files
- ⚠️ **Warn about breaking changes** before refactoring

**Think of it as**: A smart assistant that knows your entire codebase and helps Copilot make better suggestions.

---

## Prerequisites Check

Before installing, make sure you have:

### 1. Python (Required)

Check if you have Python:
```bash
python --version
# or
python3 --version
```

**You need Python 3.8 or higher** (3.10+ recommended)

**Don't have Python?**
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: Install via Homebrew: `brew install python`
- **Linux**: Usually pre-installed, or: `sudo apt install python3 python3-pip`

### 2. VS Code (Required)

Check if you have VS Code:
```bash
code --version
```

**Don't have VS Code?**
- Download from [code.visualstudio.com](https://code.visualstudio.com/)

### 3. GitHub Copilot (Required)

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "GitHub Copilot"
4. Install if not already installed
5. Sign in with your GitHub account

**Don't have Copilot?**
- Sign up at [github.com/features/copilot](https://github.com/features/copilot)
- Free for students and open source maintainers!

### 4. Git (Optional, but recommended)

Check if you have Git:
```bash
git --version
```

**Don't have Git?**
- Download from [git-scm.com](https://git-scm.com/downloads)

---

## Installation

### Step 1: Download CodeMind

**Option A: Using Git** (Recommended)
```bash
# Clone the repository
git clone https://github.com/MrUnreal/codemind.git

# Go into the directory
cd codemind
```

**Option B: Download ZIP**
1. Go to [github.com/MrUnreal/codemind](https://github.com/MrUnreal/codemind)
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file
5. Open terminal in the extracted folder

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

**If you get "pip: command not found":**
- Try `pip3 install -r requirements.txt`
- Or `python -m pip install -r requirements.txt`

**This will download:**
- FastMCP (MCP protocol implementation)
- sentence-transformers (for semantic search)
- numpy (for math operations)
- radon (for code analysis)

**First install is ~150MB** (includes ML model for semantic search)

### Step 3: Verify Installation

Test that CodeMind works:
```bash
python codemind.py
```

**You should see:**
```
INFO - Session logging to: .codemind/logs/session_XXXXXXXXX.log
INFO - All 20 CodeMind tools registered successfully
INFO - Server ready - waiting for MCP client connections...
```

**Press Ctrl+C to stop** (we'll configure VS Code next)

**If you see errors:**
- Check [Troubleshooting](#troubleshooting) section below
- Make sure all dependencies installed successfully

---

## Configure VS Code

### Step 1: Open Settings File

1. Open VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "settings json"
4. Select "Preferences: Open User Settings (JSON)"

### Step 2: Add CodeMind Configuration

Add this to your settings.json file:

```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["C:/path/to/codemind/codemind.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Important:** Replace `C:/path/to/codemind/codemind.py` with the actual path where you downloaded CodeMind.

**Finding the path:**

**Windows:**
```bash
cd codemind
cd
# Copy the path shown, e.g., C:\Users\YourName\codemind
```

**macOS/Linux:**
```bash
cd codemind
pwd
# Copy the path shown, e.g., /home/yourname/codemind
```

**Example configurations:**

**Windows:**
```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["C:/Users/John/codemind/codemind.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**macOS:**
```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python3",
      "args": ["/Users/john/codemind/codemind.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Linux:**
```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python3",
      "args": ["/home/john/codemind/codemind.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Step 3: Reload VS Code

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "reload window"
3. Select "Developer: Reload Window"

---

## First Use

### Open a Project

1. Open any project folder in VS Code
2. Wait 30-60 seconds for CodeMind to index your files
3. You'll see a `.codemind` folder created (this is your project's database)

### Try It Out!

Open GitHub Copilot Chat (usually on the right side) and try these prompts:

**Test 1: Search for code**
```
Does this project have authentication code?
```

**Test 2: Understand a file**
```
What does the main.py file do?
```

**Test 3: Find dependencies**
```
What files depend on utils.py?
```

**Test 4: Check for duplicates**
```
I want to add email validation. Do we already have that?
```

**What you should see:**
- Copilot will automatically use CodeMind tools
- It will reference actual files from your project
- It will suggest modifying existing code instead of creating duplicates

---

## Understanding CodeMind

### What happens when you use it?

1. **First time:** CodeMind scans your project files
2. **Creates index:** Stores information in `.codemind/` folder
3. **Semantic search:** Understands what your code does (not just keyword matching)
4. **Helps Copilot:** Provides context when you ask questions

### What data is stored?

CodeMind stores **locally** in `.codemind/` folder:
- File names and paths
- What each file does (from docstrings/comments)
- Imports and dependencies
- Function names and signatures
- Code embeddings (semantic vectors)

**Privacy:** All data stays on your computer. Nothing is sent to the cloud.

### How much space does it use?

- Small project (100 files): ~1-2 MB
- Medium project (1000 files): ~3-5 MB
- Large project (10000 files): ~50 MB

### Can I delete it?

Yes! You can safely delete the `.codemind/` folder anytime:
```bash
# Windows
rmdir /s .codemind

# macOS/Linux
rm -rf .codemind
```

CodeMind will recreate it next time you use it.

---

## Common Use Cases

### 1. Before Adding a Feature

**Instead of:**
```
❌ "Create authentication for my app"
   → Copilot creates new auth files (maybe duplicating existing ones)
```

**Do this:**
```
✅ "I need authentication. Do we already have it?"
   → CodeMind checks existing code
   → Copilot suggests modifying existing auth or confirms none exists
```

### 2. Before Refactoring

**Instead of:**
```
❌ "Rename UserModel to User"
   → Changes one file, breaks imports elsewhere
```

**Do this:**
```
✅ "What will break if I rename UserModel?"
   → CodeMind shows all files that use UserModel
   → Copilot updates all necessary files
```

### 3. Understanding Code

**Instead of:**
```
❌ "What does this project do?"
   → Generic response
```

**Do this:**
```
✅ "Show me the project structure"
✅ "What does auth/jwt.py do?"
✅ "What files are in the authentication module?"
   → CodeMind provides specific information about YOUR code
```

---

## Tips for Success

### âś… DO:

1. **Be specific in your questions**
   - Good: "Do we have JWT token validation?"
   - Bad: "Tell me about auth"

2. **Let CodeMind work automatically**
   - Just ask natural questions
   - Copilot will use CodeMind tools automatically

3. **Check existing code first**
   - Before creating new files, ask if similar code exists

4. **Use it for refactoring safely**
   - Always ask "what will break?" before renaming

### ❌ DON'T:

1. **Don't explicitly call tool names**
   - Bad: "Run search_existing_code with query auth"
   - Good: "Does this project have authentication?"

2. **Don't commit `.codemind/` to git**
   - It's in `.gitignore` by default
   - Each developer should have their own index

3. **Don't worry about the first scan**
   - Initial indexing takes 30-60 seconds
   - Subsequent updates are instant

---

## Troubleshooting

### "CodeMind not responding"

**Check 1:** Is CodeMind running?
```bash
# In codemind folder
python codemind.py
# Should show "Server ready"
```

**Check 2:** Did you reload VS Code?
- Press Ctrl+Shift+P → "Developer: Reload Window"

**Check 3:** Is the path correct in settings.json?
- Open settings.json
- Verify the path to codemind.py exists

### "No module named 'sentence_transformers'"

**Solution:**
```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

### "Copilot not using CodeMind"

**Solution:**
1. Check CodeMind logs: `.codemind/logs/session_*.log`
2. Be more specific in your questions
3. Make sure you're in a project folder (not empty folder)
4. Try restarting VS Code completely

### "Empty results / Not finding my files"

**Solution:**
1. Wait for initial indexing to complete (30-60 seconds)
2. Force reindex by asking: "Reindex this project"
3. Check that your files are supported types (.py, .js, .ts, etc.)

### "Python not found"

**Windows:**
```bash
# Find where Python is installed
where python
# Use full path in settings.json, e.g.:
# "command": "C:\\Python311\\python.exe"
```

**macOS/Linux:**
```bash
# Find where Python is installed
which python3
# Use full path in settings.json, e.g.:
# "command": "/usr/bin/python3"
```

---

## Next Steps

### Learn More

- **[Usage Guide](USAGE_GUIDE.md)** - Detailed examples and natural language prompts
- **[Tools Reference](docs/TOOLS.md)** - All 20 tools explained
- **[Examples](docs/EXAMPLES.md)** - Real-world usage scenarios
- **[FAQ](docs/FAQ.md)** - Common questions answered

### Customize

- **[Configuration](docs/CONFIGURATION.md)** - Customize file types, size limits, etc.
- **[Multi-Workspace](docs/MULTI_WORKSPACE_GUIDE.md)** - Work with multiple projects

### Contribute

- **[Contributing](CONTRIBUTING.md)** - Help improve CodeMind
- **[Architecture](docs/ARCHITECTURE.md)** - Technical deep-dive

---

## Getting Help

**Still stuck?**

1. **Check logs:** `.codemind/logs/session_*.log`
2. **Search issues:** [GitHub Issues](https://github.com/MrUnreal/codemind/issues)
3. **Ask questions:** [GitHub Discussions](https://github.com/MrUnreal/codemind/discussions)
4. **Report bugs:** Create a new issue with:
   - Your OS and Python version
   - Error messages
   - Steps to reproduce

---

## Success Checklist

You'll know CodeMind is working when:

- ✅ Copilot mentions specific files from your project
- ✅ It suggests modifying existing code instead of creating duplicates
- ✅ It warns you about breaking changes before refactoring
- ✅ It can answer questions about your project structure
- ✅ You see references to actual function names and file paths

---

**Congratulations!** 🎉 You're ready to use CodeMind with GitHub Copilot!

**Pro tip:** The more you use it, the more natural it becomes. Within a week, you'll wonder how you ever coded without it!

---

*Have feedback on this guide? Let us know in [GitHub Discussions](https://github.com/MrUnreal/codemind/discussions)!*
