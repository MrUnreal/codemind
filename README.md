# CodeMind 🧠# CodeMind 🧠# CodeMind 🧠# CodeMind - Multi-Workspace MCP Memory Server



> **Give GitHub Copilot memory across all your projects**



CodeMind is a Model Context Protocol (MCP) server that provides GitHub Copilot with 20 specialized tools for intelligent code search, analysis, and refactoring safety.> *Give GitHub Copilot memory across all your projects*



[![Tests](https://img.shields.io/badge/tests-110%2B%20passing-brightgreen)]() [![Python](https://img.shields.io/badge/python-3.10%2B-blue)]() [![License](https://img.shields.io/badge/license-MIT-blue)]()



---**CodeMind** is a Model Context Protocol (MCP) server that gives GitHub Copilot deep understanding of your codebase through 20 specialized AI tools for code search, analysis, and refactoring safety.> **Intelligent code memory for GitHub Copilot via MCP****Tagline:** *Give Copilot a memory across all your projects*



## 🎯 The Problem



Without project memory, GitHub Copilot:---

- ❌ Creates duplicate files when functionality already exists

- ❌ Forgets architectural decisions made minutes ago  

- ❌ Doesn't understand file relationships or purposes

- ❌ Suggests rewrites instead of targeted modifications## ⚡ Quick StartCodeMind gives GitHub Copilot deep understanding of your codebase through 20 specialized tools for code search, analysis, and refactoring safety.## Overview



## ✨ The Solution



CodeMind gives Copilot:```bash

- ✅ **Semantic Search** - Find existing functionality instantly

- ✅ **Project Memory** - Track decisions, changes, and context# 1. Install dependencies

- ✅ **Dependency Analysis** - Understand code relationships

- ✅ **Refactoring Safety** - Identify breaking changes before they happenpip install -r requirements.txt## 🚀 Quick StartCodeMind is a **workspace-aware** Model Context Protocol (MCP) server that gives GitHub Copilot queryable memory about your projects. It helps prevent Copilot from creating duplicate files, forgetting architectural decisions, and suggesting rewrites instead of modifications.



---



## ⚡ Quick Start# 2. Configure GitHub Copilot in VS Code



### 1. Install# Add to your .vscode/settings.json or user settings:

```bash

git clone https://github.com/MrUnreal/codemind.git{```bash### ✨ What's New in v2.0

cd codemind

pip install -r requirements.txt  "mcp.servers": {

```

    "codemind": {# Install

### 2. Configure VS Code

Add to `.vscode/settings.json`:      "command": "python",

```json

{      "args": ["d:/your/path/to/CodeMind/codemind.py"]pip install -r requirements.txt- **🎯 Multi-Workspace Support**: Work with multiple projects simultaneously - each with its own memory

  "mcp.servers": {

    "codemind": {    }

      "command": "python",

      "args": ["D:/Projects/Python/CodeMind/codemind.py"]  }- **📦 Modular Architecture**: Clean package structure with separate modules for better maintainability

    }

  }}

}

```# Configure VS Code MCP- **🔧 Workspace Parameter**: All tools accept `workspace_root` parameter for explicit project targeting



### 3. Restart Copilot# 3. Restart GitHub Copilot

Press `Ctrl+Shift+P` → "Copilot: Restart"

# Press Ctrl+Shift+P → "Copilot: Restart"# Add to .vscode/settings.json:- **🏗️ Production-Quality**: AST-based parsing and radon metrics for accurate analysis

🎉 **Done!** Copilot now has access to all 20 CodeMind tools.

```

---

{

## 🛠️ 20 MCP Tools

🎉 **That's it!** Copilot can now access all 20 CodeMind tools to understand your project.

```mermaid

graph TB  "mcp.servers": {### The Problem

    subgraph "🔍 Search & Discovery"

        A1[search_existing_code]---

        A2[check_functionality_exists]

        A3[search_by_export]    "codemind": {- 🔄 Copilot creates duplicate files when functionality already exists

        A4[get_similar_files]

    end## 🎯 Why CodeMind?

    

    subgraph "📝 Context & History"      "command": "python",- 🧠 Forgets architectural decisions made minutes ago

        B1[get_file_context]

        B2[query_recent_changes]GitHub Copilot is powerful, but without project memory it:

        B3[record_decision]

        B4[list_all_decisions]- ❌ Creates duplicate files when functionality already exists      "args": ["d:/Projects/Python/CodeMind/codemind.py"]- ❓ Doesn't know what files are for or how they relate

    end

    - ❌ Forgets architectural decisions made minutes ago

    subgraph "🔗 Dependencies"

        C1[find_dependencies]- ❌ Doesn't understand file purposes or relationships    }- 🔁 Suggests complete rewrites instead of targeted modifications

        C2[get_import_graph]

        C3[get_call_tree]- ❌ Suggests complete rewrites instead of targeted changes

    end

      }

    subgraph "📊 Code Analysis"

        D1[get_code_metrics_summary]**CodeMind solves this** by giving Copilot:

        D2[find_configuration_inconsistencies]

    end- ✅ **Semantic Search** - Find existing functionality instantly}### The Solution

    

    subgraph "⚠️ Refactoring Safety"- ✅ **Project Memory** - Track decisions, changes, and context

        E1[check_breaking_changes]

        E2[find_usage_examples]- ✅ **Real-time Indexing** - Auto-index as you work- 🔍 **Semantic Search**: Find existing functionality before creating new files

        E3[get_test_coverage]

    end- ✅ **Multi-Workspace** - Handle multiple projects with isolated databases

    

    subgraph "🗂️ Management"# Restart GitHub Copilot- 📝 **Project Memory**: Track file purposes, changes, and architectural decisions

        F1[force_reindex]

        F2[index_file]---

        F3[find_todo_and_fixme]

        F4[get_file_history_summary]```- ⚡ **Real-time Indexing**: Auto-index changes as you work

    end

    ## 🛠️ 20 MCP Tools for GitHub Copilot

    style A1 fill:#e1f5e1

    style B1 fill:#e1e5f5- 🎯 **Context-Aware**: Help Copilot understand your project structure

    style C1 fill:#f5e1e1

    style D1 fill:#f5f5e1### 🔍 Search & Discovery (4 tools)

    style E1 fill:#ffe1f5

    style F1 fill:#e1f5f5| Tool | Purpose |## ✨ Key Features

```

|------|---------|

### Tool Categories

| `search_existing_code` | Semantic search to find existing functionality |## Features

| Category | Count | Purpose |

|----------|-------|---------|| `check_functionality_exists` | Quick yes/no check if feature already exists |

| 🔍 **Search & Discovery** | 4 | Find existing code, check if features exist, locate definitions |

| 📝 **Context & History** | 4 | Understand files, track changes, record decisions || `search_by_export` | Find where functions/classes are defined |- **🔍 Smart Search**: Semantic code search with embeddings

| 🔗 **Dependencies** | 3 | Analyze imports, visualize relationships, trace call trees |

| 📊 **Code Analysis** | 2 | Measure complexity, detect configuration issues || `get_similar_files` | Discover files with similar patterns |

| ⚠️ **Refactoring Safety** | 3 | Check breaking changes, find usage patterns, estimate test coverage |

| 🗂️ **Management** | 4 | Index files, track TODOs, analyze git history |- **📊 Code Analysis**: Metrics, complexity, configuration checks### 🛠️ MCP Tools for Copilot (20 Total)



📚 **[Full Tool Documentation →](docs/TOOLS.md)**### 📝 Context & History (4 tools)



---| Tool | Purpose |- **🔗 Dependencies**: Import graphs, call trees, usage tracking



## 💡 How It Works|------|---------|



```mermaid| `get_file_context` | Understand what a file does and why it exists |- **⚠️ Refactoring Safety**: Breaking change detection, impact analysis#### Core Discovery Tools (5)

sequenceDiagram

    participant Dev as Developer| `query_recent_changes` | See what's been modified recently |

    participant Copilot as GitHub Copilot

    participant CodeMind as CodeMind MCP| `record_decision` | Store architectural decisions with rationale |- **📝 Context Awareness**: File history, recent changes, decisions1. **`search_existing_code`** - Semantic search for existing functionality

    participant DB as SQLite + Embeddings

    | `list_all_decisions` | Query decision history with keyword filtering |

    Dev->>Copilot: "Add JWT authentication"

    Copilot->>CodeMind: search_existing_code("JWT authentication")- **🎯 Multi-Workspace**: Isolated databases per project2. **`check_functionality_exists`** - Quick yes/no check if functionality exists

    CodeMind->>DB: Semantic search with embeddings

    DB-->>CodeMind: Found: src/auth/jwt.py (95% match)### 🔗 Dependencies (3 tools)

    CodeMind-->>Copilot: Returns existing implementation

    Copilot-->>Dev: "Found existing JWT auth in src/auth/jwt.py. Modify it?"| Tool | Purpose |3. **`search_by_export`** - Find where functions/classes are defined

    Dev->>Copilot: "Yes, add refresh tokens"

    Copilot->>CodeMind: find_usage_examples("JWTHandler")|------|---------|

    CodeMind-->>Copilot: Shows 5 real usage patterns

    Copilot->>CodeMind: check_breaking_changes("JWTHandler")| `find_dependencies` | Bidirectional dependency analysis |## 🛠️ 20 MCP Tools4. **`get_file_context`** - Understand what a file does and why it exists

    CodeMind-->>Copilot: "3 files will be affected"

    Copilot-->>Dev: Proposes safe modifications| `get_import_graph` | Visualize module relationships |

```

| `get_call_tree` | Function call graph (callers + callees) |5. **`query_recent_changes`** - See what's been modified recently

---



## 🏗️ Architecture

### 📊 Code Analysis (2 tools)| Category | Tools |

```mermaid

graph LR| Tool | Purpose |

    subgraph "CodeMind Server"

        A[codemind.py<br/>Entry Point] --> B[workspace.py<br/>Multi-Workspace]|------|---------||----------|-------|#### Enhanced Discovery Tools (4)

        B --> C[indexing.py<br/>File Scanner]

        B --> D[parsers.py<br/>AST Analysis]| `get_code_metrics_summary` | Complexity, maintainability, code smells |

        C --> E[(SQLite DB<br/>Per Workspace)]

        D --> E| `find_configuration_inconsistencies` | Detect config mismatches across environments || **Search & Discovery** | `search_existing_code`, `check_functionality_exists`, `search_by_export`, `get_similar_files` |6. **`get_similar_files`** - Find files with similar patterns/structure

        E --> F[tools/<br/>20 MCP Tools]

    end

    

    subgraph "VS Code"### ⚠️ Refactoring Safety (3 tools)| **Context & History** | `get_file_context`, `query_recent_changes`, `record_decision`, `list_all_decisions` |7. **`find_dependencies`** - Bidirectional dependency analysis

        G[GitHub Copilot] <--> |MCP Protocol| A

    end| Tool | Purpose |

    

    subgraph "Your Projects"|------|---------|| **Dependencies** | `find_dependencies`, `get_import_graph`, `get_call_tree` |8. **`list_all_decisions`** - Query decision history with keyword filtering

        H[Project A<br/>.codemind/] --> E

        I[Project B<br/>.codemind/] --> E| `check_breaking_changes` | Identify impact before refactoring |

        J[Project C<br/>.codemind/] --> E

    end| `find_usage_examples` | See real-world usage patterns || **Code Analysis** | `get_code_metrics_summary`, `find_configuration_inconsistencies` |9. **`record_decision`** - Store architectural decisions and rationale

    

    style A fill:#4CAF50| `get_test_coverage` | Estimate test coverage for files |

    style E fill:#2196F3

    style F fill:#FF9800| **Refactoring** | `check_breaking_changes`, `find_usage_examples`, `get_test_coverage` |

    style G fill:#9C27B0

```### 🗂️ Management (4 tools)



### Key Features| Tool | Purpose || **Management** | `force_reindex`, `index_file`, `find_todo_and_fixme`, `get_file_history_summary` |#### Indexing & Analysis Tools (3)



- **🎯 Multi-Workspace**: Isolated databases per project - no cross-contamination|------|---------|

- **⚡ Real-Time Indexing**: Auto-detects file changes and updates indexes

- **🧠 Semantic Search**: Uses sentence-transformers for intelligent code discovery| `force_reindex` | Manually trigger full project re-scan |10. **`force_reindex`** - Manually trigger full project re-scan

- **🔍 AST-Based**: Production-quality Python parsing, not regex hacks

- **📊 Zero-LLM Analysis**: Fast static analysis without API calls| `index_file` | Index specific file immediately |



---| `find_todo_and_fixme` | Track technical debt (TODO/FIXME/HACK) |## 📚 Documentation11. **`index_file`** - Index specific file immediately



## 🌟 What's New in v2.0| `get_file_history_summary` | Git commit history analysis |



| Feature | Description |12. **`get_call_tree`** - Function call graph (callers + callees)

|---------|-------------|

| 🎯 **Multi-Workspace Support** | Work with multiple projects simultaneously |---

| 📦 **Modular Architecture** | Clean package structure (11 modules, 2,577 lines) |

| 🔧 **Explicit Workspace Targeting** | All tools accept `workspace_root` parameter |- **[Full Documentation](docs/DOCS.md)** - Complete API reference

| 🏗️ **Production Quality** | AST-based parsing, comprehensive error handling |

| 🧪 **Fully Tested** | 110+ tests across 6 test suites (99%+ pass rate) |## 💡 Example Usage



📚 **[Migration Guide →](docs/MIGRATION_GUIDE.md)**- **[Multi-Workspace Guide](docs/MULTI_WORKSPACE_GUIDE.md)** - Managing multiple projects#### Refactoring Safety Tools (5)



---### Ask Copilot Chat:



## 📖 Example Usage```- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Common use cases13. **`check_breaking_changes`** - Identify impacted code before refactoring



### Before Creating New Files"Does this project already have user authentication?"

```

💬 "Does this project have user authentication?"→ Uses check_functionality_exists to search codebase- **[Testing Summary](docs/TESTING_SUMMARY.md)** - Test coverage details14. **`find_usage_examples`** - Real-world usage patterns

→ check_functionality_exists("user authentication")

✅ Found in src/auth/jwt.py - no need to create new file

```

"Show me how get_workspace_path is used"15. **`find_todo_and_fixme`** - Track technical debt (TODO/FIXME/HACK)

### Before Refactoring

```→ Uses find_usage_examples to find real usage patterns

💬 "What will break if I change the UserModel class?"

→ check_breaking_changes("UserModel", "models/user.py")## 🏗️ Architecture16. **`get_file_history_summary`** - Git commit history analysis

⚠️ 7 files will be affected: [list of impacted files]

```"What files depend on workspace.py?"



### Understanding Code Relationships→ Uses find_dependencies for impact analysis17. **`get_test_coverage`** - Estimate test coverage

```

💬 "What depends on database.py?"

→ find_dependencies("src/database.py")

📋 Imported by: models/user.py, models/post.py, auth/session.py"What decisions have we made about database schema?"```

```

→ Uses list_all_decisions to search decision history

### Finding Usage Patterns

``````CodeMind/#### Zero-LLM Static Analysis Tools (3) ⭐ NEW

💬 "How is the API client used in this codebase?"

→ find_usage_examples("APIClient")

📝 Shows 5 real-world usage examples with context

```### Natural Workflow:├── codemind/           # Core package18. **`get_code_metrics_summary`** - Comprehensive code metrics (LOC, complexity, maintainability)



📚 **[More Examples →](docs/EXAMPLES.md)**1. **Before creating a file**: "Search for existing authentication code"



---2. **Before refactoring**: "Check breaking changes for parse_imports_ast"│   ├── workspace.py    # Workspace management19. **`get_import_graph`** - Dependency visualization with circular detection



## 🧪 Testing3. **During code review**: "What are the recent changes to tools/ folder?"



```bash4. **Planning features**: "Show me similar files to user_service.py"│   ├── parsers.py      # AST parsing20. **`find_configuration_inconsistencies`** - Config analysis and secret detection

# Run all test suites

python tests/run_all_tests.py



# Individual test suites---│   ├── indexing.py     # File indexing

python tests/test_01_basic.py       # 19 tests - basic tool validation

python tests/test_02_chains.py      # 6 scenarios - tool chaining

python tests/test_03_complex.py     # 30 tests - edge cases & stress

```## ✨ What's New in v2.0│   └── tools/          # 20 MCP tools (6 categories)### 🚀 Auto-Indexing System



**Test Results:**

- ✅ 110+ tests across 6 suites

- ✅ 99%+ pass rate- 🎯 **Multi-Workspace Support** - Work with multiple projects simultaneously├── tests/              # Comprehensive test suite

- ✅ Security tested (SQL injection, path traversal)

- ✅ Stress tested (large queries, bulk operations)- 📦 **Modular Architecture** - Clean package structure (12 modules, 2,577 lines)



📚 **[Testing Guide →](docs/TESTING.md)**- 🔧 **Workspace Parameter** - All tools accept `workspace_root` for explicit targeting├── docs/               # Documentation- **File Watcher**: Automatically detects file changes



---- 🏗️ **Production Quality** - AST-based parsing, comprehensive error handling



## 📚 Documentation- 🧪 **100% Tested** - 110+ tests across 6 test suites with 99%+ pass rate├── configs/            # Configuration examples- **Smart Analysis**: Extracts file purpose from docstrings and comments



| Document | Description |

|----------|-------------|

| **[Tool Reference](docs/TOOLS.md)** | Complete documentation of all 20 tools |---└── codemind.py         # MCP server entry point- **Semantic Embeddings**: Uses sentence-transformers for semantic search

| **[Architecture](docs/ARCHITECTURE.md)** | System design and technical details |

| **[Multi-Workspace Guide](docs/MULTI_WORKSPACE_GUIDE.md)** | Working with multiple projects |

| **[Examples](docs/EXAMPLES.md)** | Real-world usage scenarios |

| **[Testing](docs/TESTING.md)** | Test suite details and validation |## 🏗️ Project Structure```- **SQLite Storage**: Lightweight, zero-maintenance database

| **[Configuration](docs/CONFIGURATION.md)** | Customization options |

| **[Migration Guide](docs/MIGRATION_GUIDE.md)** | Upgrading from v1.x |

| **[FAQ](docs/FAQ.md)** | Common questions and troubleshooting |

```

---

CodeMind/

## 🔧 Configuration

├── codemind/              # Core package (2,577 lines)## 🧪 Testing### ⚙️ Configuration

Create `codemind_config.json` in your project root:

│   ├── workspace.py       # Workspace & database management

```json

{│   ├── parsers.py         # AST parsing (imports, functions, calls)

  "watched_extensions": [".py", ".js", ".ts", ".tsx", ".jsx"],

  "max_file_size_kb": 500,│   ├── indexing.py        # File scanning & indexing

  "embedding_model": "all-MiniLM-L6-v2",

  "exclude_dirs": [".git", ".venv", "node_modules"]│   └── tools/             # 20 MCP tools (6 categories)```bash- **Zero Config**: Works out of the box for most projects

}

```│       ├── search.py      # 4 search & discovery tools



📚 **[Full Configuration Reference →](docs/CONFIGURATION.md)**│       ├── context.py     # 4 context & history tools# Run all tests- **Customizable**: Support for multiple programming languages



---│       ├── dependencies.py # 3 dependency analysis tools



## 📊 Status│       ├── analysis.py    # 2 code analysis toolspython -m pytest tests/ -v- **Performance Tuned**: Fast queries (<500ms) and efficient indexing



| Metric | Status |│       ├── refactoring.py # 3 refactoring safety tools

|--------|--------|

| **Tools** | ✅ 20/20 operational |│       └── management.py  # 4 management tools

| **Tests** | ✅ 110+ tests, 99%+ pass rate |

| **Type Safety** | ✅ Full type hints, Pylance compliant |├── tests/                 # Comprehensive test suite (110+ tests)

| **Documentation** | ✅ Comprehensive guides and API docs |

| **Production Ready** | ✅ Battle-tested on real projects |├── docs/                  # Full documentation# Individual test suites## Quick Start



---├── configs/               # Configuration examples



## 🤝 Contributing└── codemind.py            # MCP server entry pointpython tests/test_01_basic.py        # Basic tool validation



Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.```



### Development Setuppython tests/test_02_chains.py       # Tool chaining scenarios### Prerequisites

```bash

git clone https://github.com/MrUnreal/codemind.git---

cd codemind

pip install -r requirements.txtpython tests/test_03_complex.py      # Complex edge cases

python tests/run_all_tests.py

```## 📚 Documentation



---python tests/final_validation.py     # Production readiness- Python 3.10 or higher



## 📝 License| Document | Description |



MIT License - See [LICENSE](LICENSE) file for details.|----------|-------------|```- GitHub Copilot or compatible MCP client



---| **[API Reference](docs/DOCS.md)** | Complete tool documentation with examples |



## 💬 Support| **[Multi-Workspace Guide](docs/MULTI_WORKSPACE_GUIDE.md)** | Managing multiple projects |



- 🐛 **Issues**: [GitHub Issues](https://github.com/MrUnreal/codemind/issues)| **[Quick Reference](docs/QUICK_REFERENCE.md)** | Common use cases and patterns |

- 📧 **Contact**: Via GitHub

| **[Testing Summary](docs/TESTING_SUMMARY.md)** | Test coverage and validation |## 📊 Status### Installation

---

| **[Solution Organization](docs/SOLUTION_ORGANIZATION.md)** | Architecture and structure |

**Built with** ❤️ **using**: Python 3.10+, FastMCP, sentence-transformers, GitPython



*Making GitHub Copilot smarter, one project at a time* 🚀

---

- ✅ **20 Tools**: All operational and tested1. **Clone the repository**:

## 🧪 Testing

- ✅ **Test Coverage**: 95% tool functionality, 91% edge cases```bash

```bash

# Run all test suites (recommended)- ✅ **Type Safety**: Full type hints, passes Pylancegit clone https://github.com/yourusername/codemind.git

python tests/run_all_tests.py

- ✅ **Production Ready**: Validated and documentedcd codemind

# Run individual test suites

python tests/test_01_basic.py        # 19 tests - basic tool validation```

python tests/test_02_chains.py       # 6 scenarios - tool chaining

python tests/test_03_complex.py      # 30 tests - edge cases & stress## 🤝 Contributing

python tests/test_comprehensive.py   # Infrastructure validation

python tests/test_curveballs.py      # 35 advanced edge cases2. **Install dependencies**:

python tests/final_validation.py     # Production readiness check

```See [V2 Completion Report](docs/V2_COMPLETION_REPORT.md) for architecture details.```bash



**Test Results:**pip install -r requirements.txt

- ✅ 110+ tests across 6 test suites

- ✅ 99%+ pass rate## 📝 License```

- ✅ Edge cases: SQL injection, unicode, security tested

- ✅ Stress tests: Large queries, bulk operations validated



---MIT License - See LICENSE file for details.3. **Initialize your project**:



## 🚀 Features in Detail```bash



### 🔍 Semantic Search with Embeddings---python codemind.py

Uses sentence-transformers for intelligent code search:

- Find functionality by description, not just keywords```

- Similarity-based file discovery

- Context-aware code recommendations**Built with**: Python 3.10+, FastMCP, sentence-transformers, GitPython



### 📊 Production-Quality AnalysisThis will:

- **AST Parsing**: Accurate Python code analysis- Create a `.codemind/` directory in your project

- **Radon Metrics**: Complexity and maintainability scoring- Scan and index your existing files

- **Git Integration**: History and authorship tracking- Start the MCP server



### 🎯 Multi-Workspace Architecture### VS Code Setup

- Isolated SQLite databases per project

- No cross-project contaminationAdd CodeMind to your VS Code MCP settings. Create or update your VS Code settings file:

- Explicit workspace targeting via `workspace_root` parameter

**Windows**: `%APPDATA%\Code\User\settings.json`

### ⚡ Real-Time Indexing**macOS**: `~/Library/Application Support/Code/User/settings.json`

- Lazy workspace scanning on first use**Linux**: `~/.config/Code/User/settings.json`

- Incremental file indexing

- Efficient embedding generation```json

{

---  "mcp.servers": {

    "codemind": {

## 🔧 Configuration      "command": "python",

      "args": ["D:/path/to/CodeMind/codemind.py"],

### Basic Setup      "cwd": "D:/Projects/YourProject"

```json    }

// .vscode/settings.json  }

{}

  "mcp.servers": {```

    "codemind": {

      "command": "python",**Note**: With v2.0's multi-workspace support, you can work with any project by specifying the `workspace_root` parameter in tool calls. The `cwd` is just the default.

      "args": ["d:/path/to/CodeMind/codemind.py"]

    }## Multi-Workspace Support

  }

}### How It Works

```

Every CodeMind tool now accepts a `workspace_root` parameter (defaults to `"."`):

### Custom Configuration

```json```python

// .codemind/config.json (optional)# Search in current workspace

{search_existing_code("authentication")

  "lazy_scan": true,

  "exclude_dirs": [".git", ".venv", "node_modules"],# Search in specific project

  "enable_embeddings": true,search_existing_code("authentication", workspace_root="/path/to/project1")

  "auto_index_on_change": false

}# Work with multiple projects simultaneously

```search_existing_code("API client", workspace_root="/path/to/frontend")

find_dependencies("utils.py", workspace_root="/path/to/backend")

See [configs/example_config.json](configs/example_config.json) for all options.```



---### Workspace Isolation



## 📊 Status & QualityEach workspace gets its own:

- **Database**: `.codemind/memory.db` in that workspace

- ✅ **20 Tools**: All operational and tested- **Configuration**: `codemind_config.json` if present

- ✅ **Test Coverage**: 110+ tests, 99%+ pass rate- **Embedding Model**: Cached per workspace

- ✅ **Type Safety**: Full type hints, passes Pylance- **Session Logs**: Workspace-specific logs

- ✅ **Documentation**: Comprehensive API docs and guides

- ✅ **Production Ready**: Battle-tested on real projectsThis means:

✅ No cross-contamination between projects

---✅ Each project can have different settings

✅ Work with multiple codebases without conflicts

## 🤝 Contributing✅ Switch projects without restarting the server



CodeMind is designed to be extended. See [V2 Completion Report](docs/V2_COMPLETION_REPORT.md) for architecture details.## Configuration



### Key Extension Points:Create a `codemind_config.json` file in your project root to customize behavior:

- Add new tools in `codemind/tools/`

- Register tools in `codemind/tools/__init__.py````json

- Follow the modular architecture pattern{

  "project_root": "./",

---  "db_path": ".codemind/memory.db",

  "watched_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".java", ".cs", ".cpp", ".c", ".h", ".go", ".rs"],

## 📝 License  "scan_interval": 300,

  "max_file_size_kb": 500,

MIT License - See LICENSE file for details.  "embedding_model": "all-MiniLM-L6-v2",

  "max_files": 10000

---}

```

## 🛠️ Requirements

### Configuration Options

- **Python**: 3.10+

- **Dependencies**: fastmcp, sentence-transformers, GitPython, radon| Option | Default | Description |

- **VS Code**: Latest version with GitHub Copilot extension|--------|---------|-------------|

- **Git**: For history analysis features| `project_root` | `"./"` | Root directory to scan |

| `db_path` | `".codemind/memory.db"` | SQLite database location |

---| `watched_extensions` | `[".py", ".js", ...]` | File extensions to index |

| `scan_interval` | `300` | Seconds between full rescans |

## 💬 Support| `max_file_size_kb` | `500` | Maximum file size to index |

| `embedding_model` | `"all-MiniLM-L6-v2"` | Sentence transformer model |

- **Issues**: Use GitHub Issues for bugs and feature requests| `max_files` | `10000` | Maximum files to index |

- **Docs**: Check [docs/](docs/) folder for detailed guides

- **Examples**: See [Quick Reference](docs/QUICK_REFERENCE.md) for common patterns## Usage Examples



---### Before CodeMind

```

**Built with** ❤️ **using**: Python 3.10+, FastMCP, sentence-transformers, GitPython, radon👤 Developer: "Add JWT authentication"

🤖 Copilot: *creates auth/middleware.py*

*Making GitHub Copilot smarter, one project at a time.* 🚀🤖 Copilot: *creates auth/jwt_handler.py*  

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