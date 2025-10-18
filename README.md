# CodeMind 🧠

> Give GitHub Copilot memory across all your projects

[![Tests](https://img.shields.io/badge/tests-110%2B%20passing-brightgreen)](https://github.com/MrUnreal/codemind/actions) [![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**CodeMind** is an MCP server that gives GitHub Copilot 20 specialized tools for understanding your codebase.

<!-- mcp-name: io.github.mrunreal/codemind -->

---

## Why CodeMind?

**Without it:**
- ❌ Copilot creates duplicate files
- ❌ Forgets decisions you just made
- ❌ Doesn't understand your project structure

**With it:**
- ✅ Finds existing code before creating new files
- ✅ Remembers architectural decisions
- ✅ Understands dependencies and relationships
- ✅ Warns about breaking changes

---

## Quick Start

**New to CodeMind?** See our [Getting Started Guide](GETTING_STARTED.md) for step-by-step instructions!

### For Experienced Users

**1. Install**
```bash
git clone https://github.com/MrUnreal/codemind.git
cd codemind
pip install -r requirements.txt
```

**2. Configure VS Code**

Add to your VS Code settings (Ctrl+Shift+P → "Preferences: Open User Settings (JSON)"):
```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["/full/path/to/codemind.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Replace `/full/path/to/codemind.py`** with the actual path to where you cloned CodeMind.

**3. Reload VS Code**

Press `Ctrl+Shift+P` → "Developer: Reload Window"

**4. Test It**

Open Copilot Chat and try:
```
Does this project have authentication?
```

Done! 🎉

**Need help?** Check our [Troubleshooting Guide](GETTING_STARTED.md#troubleshooting)

---

## What You Get

**20 AI Tools in 6 Categories:**

| Category | What It Does |
|----------|-------------|
| 🔍 Search | Find existing code, check if features exist |
| 📝 Context | Understand files, track changes, remember decisions |
| 🔗 Dependencies | See what imports what, visualize structure |
| 📊 Analysis | Code quality metrics, config auditing |
| ⚠️ Safety | Check breaking changes before refactoring |
| 🗂️ Management | Index files, find TODOs, git history |

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  You: "Add authentication"                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         v
┌─────────────────────────────────────────────────────────────┐
│  Copilot (with CodeMind):                                   │
│  🔍 Searching existing code...                              │
│  âś… Found: src/auth/jwt.py (95% match)                      │
│  💡 "I found existing JWT auth. Should I extend it?"        │
└─────────────────────────────────────────────────────────────┘

Without CodeMind:
❌ Creates duplicate auth files
❌ Doesn't know about existing code
❌ No context of your architecture
```

**You ask naturally** → **Copilot automatically uses CodeMind** → **Gets smart suggestions**

**No explicit tool calls needed!**

---

## Example Usage

```
💬 "Does this project have authentication?"
✅ Found in src/auth/jwt.py

💬 "What will break if I rename UserModel?"
⚠️ 7 files will be affected

💬 "What depends on database.py?"
📋 Used by: models/, auth/, tests/

💬 "Show me TODOs"
📝 Found 12 TODOs across 5 files
```

---

## Multi-Workspace Support

Work with multiple projects simultaneously:
- Each project gets its own database
- No cross-contamination
- Isolated configurations

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Getting Started](GETTING_STARTED.md) | **Start here!** Complete beginner's guide |
| [Usage Guide](USAGE_GUIDE.md) | How to use with Copilot |
| [Contributing](CONTRIBUTING.md) | How to contribute to CodeMind |
| [Tools Reference](docs/TOOLS.md) | All 20 tools explained |
| [Examples](docs/EXAMPLES.md) | Real-world scenarios |
| [FAQ](docs/FAQ.md) | Common questions |
| [Architecture](docs/ARCHITECTURE.md) | Technical details |
| [Changelog](CHANGELOG.md) | Version history |

---

## Requirements

- Python 3.8 or higher
- VS Code with GitHub Copilot
- ~80MB for embedding model (downloaded automatically on first use)
- ~1-5MB per project for database

---

## Status

- ✅ 20/20 tools operational
- ✅ 110+ tests passing (99%+ rate)
- ✅ Production ready
- ✅ Actively maintained

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

MIT - See [LICENSE](LICENSE)

---

**Built with**: Python, FastMCP, sentence-transformers, SQLite

*Making Copilot smarter, one project at a time* 🚀
