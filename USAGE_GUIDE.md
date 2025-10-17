# CodeMind Usage Guide

Complete guide to using CodeMind with GitHub Copilot.

---

## 🎯 How CodeMind Works with Copilot

CodeMind tools are **automatically invoked** by GitHub Copilot based on your questions and requests. You don't need to explicitly call tool names - just ask naturally!

### The Magic of Proactive Tools

**Before Enhancement:**
```
User: "I want to add authentication"
Copilot: "Here's how to implement authentication..." ❌ Creates new code
```

**After Enhancement:**
```
User: "I want to add authentication"
Copilot: 🤔 "Let me check existing code first..."
         → Automatically calls: search_existing_code("authentication")
         → Finds: src/auth/jwt.py (95% match)
Copilot: "I found existing authentication in src/auth/jwt.py. 
         Should I extend it or create something different?" ✅
```

---

## 💬 Natural Prompts for Each Tool Category

### 🔍 Search & Discovery

#### Find Existing Code
**Just ask:**
- "Does this project have authentication?"
- "Search for database connection code"
- "Find existing email validation"
- "Show me payment processing code"
- "Do we have JWT token handling?"

**Copilot automatically uses:**
- `search_existing_code` - For semantic search
- `check_functionality_exists` - For quick yes/no checks

#### Locate Definitions
**Just ask:**
- "Where is UserModel defined?"
- "Find the SentenceTransformer class"
- "Which file exports APIClient?"
- "Show me where parse_file is implemented"

**Copilot automatically uses:**
- `search_by_export` - To find definitions

#### Find Similar Code
**Just ask:**
- "Show me files similar to user_service.py"
- "Find files with similar structure to this one"
- "What files follow the same pattern?"

**Copilot automatically uses:**
- `get_similar_files` - To find patterns

---

### 📝 Context & History

#### Understand Files
**Just ask:**
- "What does workspace.py do?"
- "Explain the purpose of indexing.py"
- "What is parsers.py responsible for?"

**Copilot automatically uses:**
- `get_file_context` - To understand file purposes

#### Track Changes
**Just ask:**
- "What changed recently?"
- "Show me recent modifications"
- "What files were edited today?"
- "What have we worked on this week?"

**Copilot automatically uses:**
- `query_recent_changes` - To show modification history

#### Decision History
**Just ask:**
- "Why did we choose JWT?"
- "What decisions have we made about authentication?"
- "Show me architecture decisions"
- "What's the rationale for using SQLite?"

**Copilot automatically uses:**
- `list_all_decisions` - To retrieve historical decisions

**Note:** To record a decision, be explicit:
```
"Record this decision: Using JWT for auth because it's stateless"
```

---

### 🔗 Dependencies & Relationships

#### Understand Dependencies
**Just ask:**
- "What does workspace.py import?"
- "What files depend on database.py?"
- "Show me the dependencies for utils.py"
- "What imports indexing.py?"

**Copilot automatically uses:**
- `find_dependencies` - For bidirectional dependency analysis

#### Visualize Project Structure
**Just ask:**
- "Show me the import graph"
- "What's the project structure?"
- "Are there circular dependencies?"
- "How are modules connected?"

**Copilot automatically uses:**
- `get_import_graph` - For full dependency visualization

#### Trace Call Trees
**Just ask:**
- "What calls search_existing_code?"
- "What does get_workspace_db call?"
- "Show me the call tree for parse_imports_ast"
- "What's the execution path for this function?"

**Copilot automatically uses:**
- `get_call_tree` - For function call hierarchies

---

### 📊 Code Analysis & Quality

#### Assess Code Quality
**Just ask:**
- "How's the code quality?"
- "What's the complexity of this project?"
- "Is the codebase maintainable?"
- "Show me code metrics"
- "What's the technical debt?"

**Copilot automatically uses:**
- `get_code_metrics_summary` - For comprehensive analysis

#### Find Configuration Issues
**Just ask:**
- "Check configuration consistency"
- "Are there config issues?"
- "Audit environment variables"
- "Find hardcoded secrets"
- "Compare dev vs prod config"

**Copilot automatically uses:**
- `find_configuration_inconsistencies` - For config auditing

---

### ⚠️ Refactoring Safety (CRITICAL)

#### Before Changing Code
**Just ask:**
- "What will break if I rename UserModel?"
- "Is it safe to change parse_file?"
- "What depends on this function?"
- "Check breaking changes for APIClient"

**Copilot automatically uses:**
- `check_breaking_changes` - **ALWAYS before refactoring**

#### Learn From Usage
**Just ask:**
- "How is get_workspace_db used?"
- "Show me examples of using search_existing_code"
- "What are the usage patterns for this function?"
- "How do we call this API?"

**Copilot automatically uses:**
- `find_usage_examples` - To show real-world usage

#### Test Coverage Check
**Just ask:**
- "Is this file tested?"
- "What's the test coverage?"
- "Are there tests for workspace.py?"
- "How well is this tested?"

**Copilot automatically uses:**
- `get_test_coverage` - To assess testing safety

---

### 🗂️ Index Management

#### Refresh Index
**Just ask:**
- "Reindex the project"
- "Refresh the CodeMind database"
- "Something's out of sync, rebuild the index"

**Copilot automatically uses:**
- `force_reindex` - For full project rescan

**When you create new files:**
Copilot automatically uses `index_file` to add them to the index.

#### Find Technical Debt
**Just ask:**
- "Show me all TODOs"
- "What needs fixing?"
- "Find all FIXMEs"
- "What's marked as HACK?"
- "List technical debt"

**Copilot automatically uses:**
- `find_todo_and_fixme` - To track code comments

#### Git History
**Just ask:**
- "Who worked on workspace.py?"
- "What's the change frequency for this file?"
- "Is this file stable or active?"
- "Show git history for indexing.py"

**Copilot automatically uses:**
- `get_file_history_summary` - For contributor analysis

---

## 🎨 Natural Workflow Examples

### Scenario 1: Adding a Feature

**Your prompt:**
```
"I need to add email validation to the user registration"
```

**What Copilot does automatically:**
1. Searches for existing email validation code
2. Checks if validation utilities exist
3. Finds similar validation patterns
4. Suggests modifying existing code vs creating new

**You get:**
```
"Found existing email validation in utils/validators.py.
I can extend validate_email() to add your requirements."
```

---

### Scenario 2: Refactoring

**Your prompt:**
```
"Let's rename the scan_project function to index_workspace"
```

**What Copilot does automatically:**
1. Checks breaking changes (what calls this function?)
2. Finds usage examples to understand call patterns
3. Checks test coverage for safety
4. Analyzes dependencies

**You get:**
```
"⚠️ scan_project is called in 7 files:
- codemind/workspace.py (3 times)
- tests/test_01_basic.py (2 times)
- ...

Test coverage: 85%

Safe to rename, but you'll need to update these locations."
```

---

### Scenario 3: Understanding Code

**Your prompt:**
```
"Explain how the workspace system works"
```

**What Copilot does automatically:**
1. Gets context for workspace.py
2. Finds dependencies (what it imports/exports)
3. Shows recent changes
4. Retrieves related architectural decisions

**You get:**
```
"workspace.py manages multi-workspace isolation:
- Creates per-workspace databases
- Caches embedding models
- Handles workspace-specific configs

Recently modified: Added workspace_root parameter support
Decision #15: Chose SQLite per workspace for data isolation"
```

---

### Scenario 4: Code Review

**Your prompt:**
```
"Review the recent changes to the tools/ directory"
```

**What Copilot does automatically:**
1. Queries recent changes
2. Gets code metrics
3. Checks for configuration issues
4. Finds TODO/FIXME comments

**You get:**
```
"Recent changes (last 7 days):
- tools/search.py: Enhanced docstrings (+450 lines)
- tools/context.py: Added proactive triggers (+380 lines)

Metrics: Maintainability 65/100 (Good)
TODOs: 3 items in tools/refactoring.py marked for optimization"
```

---

## 🚦 Best Practices

### ✅ DO: Use Natural Language

```
✅ "I want to add authentication"
✅ "What will break if I change this?"
✅ "Show me similar files"
✅ "How is this function used?"
```

### ❌ DON'T: Call Tools Explicitly

```
❌ "Run search_existing_code with query authentication"
❌ "Call check_breaking_changes for UserModel"
❌ "Execute find_dependencies on workspace.py"
```

Copilot knows when to use tools - you just need to ask your question naturally!

---

### ✅ DO: Be Specific When Needed

```
✅ "Does this project have JWT token refresh?"
✅ "What depends on the get_workspace_db function specifically?"
✅ "Show TODOs only in the tools/ directory"
```

### ❌ DON'T: Be Too Vague

```
❌ "Tell me about the code"
❌ "What's in this project?"
❌ "Show me stuff"
```

---

### ✅ DO: Ask Before Acting

```
✅ "Check if we have authentication before I create it"
✅ "What will break if I rename parse_file?"
✅ "Is this function tested before I modify it?"
```

### ❌ DON'T: Skip Safety Checks

```
❌ "Rename all occurrences of UserModel to User" (without checking)
❌ "Delete the workspace.py file" (without impact analysis)
```

---

## 🎯 Tool Invocation Triggers

Each tool has specific triggers in its docstring that Copilot uses to decide when to invoke it:

### Automatic Invocation Happens When:

- **Implementing/Adding Features** → Searches existing code
- **Refactoring/Renaming** → Checks breaking changes & test coverage
- **Asking "What/Where/How"** → Gets context and dependencies
- **Quality Questions** → Analyzes metrics
- **Deployment/Config Questions** → Audits configuration
- **File Mentions** → Gets file context automatically

### Manual Invocation (Explicit Request):

- **Recording Decisions** - Must explicitly ask to record
- **Force Reindex** - Must explicitly request full rescan

---

## 🔍 Troubleshooting

### "Copilot isn't using CodeMind tools"

**Solution:**
1. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Verify MCP server in settings: Check `.vscode/settings.json`
3. Be more specific in your questions
4. Check CodeMind logs: `.codemind/logs/`

### "Tools are returning empty results"

**Solution:**
1. First-time use: Wait for initial indexing (30-60 seconds)
2. Force reindex: "Reindex the project"
3. Check file extensions: Ensure your files are in `watched_extensions`
4. Verify workspace: Make sure you're in the right project directory

### "Too many tool calls / Slow responses"

**Solution:**
1. This is normal for complex questions
2. Be more specific to reduce unnecessary tool usage
3. Tools cache results for better performance
4. Consider smaller, focused questions

---

## 📊 Monitoring Tool Usage

### Check Logs

CodeMind logs all tool invocations:

```
.codemind/logs/codemind.log
```

### Successful Usage Indicators

You'll know tools are working when Copilot:

- References actual file names from your project
- Mentions specific line numbers or functions
- Warns about breaking changes before suggesting refactoring
- Suggests modifying existing code instead of creating new files
- Cites specific metrics (complexity, LOC, etc.)
- Shows awareness of your project structure

---

## 🎓 Learning Curve

### Week 1: Discovery
- Watch for Copilot automatically searching code
- Notice when it suggests existing code vs creating new
- See breaking change warnings

### Week 2: Trust
- Rely on automatic tool usage
- Ask more complex questions
- Leverage decision tracking

### Week 3: Mastery
- Natural conversation with Copilot about your codebase
- Seamless refactoring with safety checks
- Efficient code discovery and reuse

---

## 🚀 Advanced Tips

### Combine Multiple Concepts

```
"I need to add email notifications. Check if we have email utilities,
show me similar notification code, and verify no config issues."
```

Copilot will automatically:
1. Search for email utilities
2. Find similar notification patterns
3. Check configuration consistency

### Contextual Follow-ups

```
First: "What does workspace.py do?"
Then: "What depends on it?"
Then: "Is it safe to refactor?"
```

Copilot maintains context across the conversation.

### Decision Tracking Workflow

```
1. "Why did we choose JWT?" (retrieve past decision)
2. Make architectural change
3. "Record decision: Switched to OAuth2 for better third-party integration"
```

---

## ✨ Success Metrics

You're using CodeMind effectively when:

- ✅ Copilot finds existing code before suggesting new files
- ✅ You're warned about breaking changes before refactoring
- ✅ Copilot references specific files and functions by name
- ✅ You spend less time searching for code manually
- ✅ Architectural decisions are tracked and referenced
- ✅ Code reuse increases, duplication decreases

---

**Remember:** CodeMind works best when you forget it's there. Just talk to Copilot naturally about your code, and the tools will activate automatically! 🚀
