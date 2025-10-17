# CodeMind - Prompt Guide for GitHub Copilot

## How to Get Copilot to Use CodeMind Tools

CodeMind provides 20 specialized tools. Here's how to phrase questions to trigger them:

---

## 🔍 Search & Discovery Tools

### Tool: `search_existing_code`
**Ask:** 
- "Search for code related to [topic]"
- "Find existing [functionality] code"
- "Do we have code that handles [feature]?"
- "Show me files about [concept]"

**Example:**
```
"Search for existing authentication code"
"Find database connection handling"
```

---

### Tool: `check_functionality_exists`
**Ask:**
- "Does this project have [feature]?"
- "Do we already implement [functionality]?"
- "Is there existing code for [task]?"

**Example:**
```
"Do we have JWT token handling?"
"Is there existing email validation?"
```

---

### Tool: `search_by_export`
**Ask:**
- "Where is [ClassName] defined?"
- "Find the definition of [function_name]"
- "Which file exports [symbol]?"

**Example:**
```
"Where is the SentenceTransformer class used?"
"Find the definition of get_workspace_db"
```

---

### Tool: `get_similar_files`
**Ask:**
- "Find files similar to [filename]"
- "What files are like [path]?"
- "Show similar patterns to [file]"

**Example:**
```
"Find files similar to test_installation.py"
"What files are similar to workspace.py?"
```

---

## 📝 Context & History Tools

### Tool: `get_file_context`
**Ask:**
- "What does [filename] do?"
- "Explain [filepath]"
- "Tell me about [file]"
- "What's the purpose of [file]?"

**Example:**
```
"What does workspace.py do?"
"Explain the parsers module"
```

---

### Tool: `query_recent_changes`
**Ask:**
- "What changed recently?"
- "Show recent file modifications"
- "What was modified in the last [N] hours?"

**Example:**
```
"What files changed in the last 24 hours?"
"Show recent changes"
```

---

### Tool: `record_decision`
**Ask:**
- "Record this decision: [description]"
- "Save architectural decision: [text]"
- "Document why we chose [approach]"

**Example:**
```
"Record decision: We're using SQLite for local storage because it's serverless and portable"
```

---

### Tool: `list_all_decisions`
**Ask:**
- "Show architectural decisions"
- "List all decisions about [topic]"
- "What decisions have been made?"

**Example:**
```
"Show all decisions about database"
"List architectural decisions"
```

---

## 🔗 Dependency Analysis Tools

### Tool: `find_dependencies`
**Ask:**
- "What depends on [file]?"
- "Show dependencies of [file]"
- "What imports [file]?"
- "What does [file] import?"

**Example:**
```
"What depends on workspace.py?"
"Show dependencies of indexing.py"
```

---

### Tool: `get_import_graph`
**Ask:**
- "Show the import graph"
- "Visualize project dependencies"
- "Show module relationships"
- "Are there circular dependencies?"

**Example:**
```
"Show the import graph for this project"
"Visualize dependencies"
```

---

### Tool: `get_call_tree`
**Ask:**
- "Show the call tree for [function]"
- "What does [function] call?"
- "What calls [function]?"
- "Show function call hierarchy"

**Example:**
```
"Show call tree for scan_project"
"What calls get_workspace_db?"
```

---

## 📊 Code Analysis Tools

### Tool: `get_code_metrics_summary`
**Ask:**
- "Analyze code quality"
- "Show code metrics"
- "What's the complexity of this project?"
- "Give me a code health report"

**Example:**
```
"Show code metrics for this project"
"What's the code quality?"
```

---

### Tool: `find_configuration_inconsistencies`
**Ask:**
- "Check configuration files"
- "Find config inconsistencies"
- "Are there config mismatches?"

**Example:**
```
"Check for configuration inconsistencies"
"Find config problems"
```

---

## ⚠️ Refactoring Safety Tools

### Tool: `check_breaking_changes`
**Ask:**
- "What would break if I modify [function]?"
- "Check impact of changing [symbol]"
- "Is it safe to rename [function]?"
- "What uses [function]?"

**Example:**
```
"What breaks if I rename get_workspace_db?"
"Check impact of modifying scan_project"
```

---

### Tool: `find_usage_examples`
**Ask:**
- "Show usage examples of [function]"
- "How is [function] used?"
- "Give me examples of [function] calls"

**Example:**
```
"Show usage examples of search_existing_code"
"How is get_file_context used?"
```

---

### Tool: `get_test_coverage`
**Ask:**
- "What's the test coverage for [file]?"
- "Is [file] tested?"
- "Show test coverage"

**Example:**
```
"What's the test coverage for workspace.py?"
"Is indexing.py tested?"
```

---

## 🗂️ Index Management Tools

### Tool: `force_reindex`
**Ask:**
- "Reindex the entire project"
- "Refresh the code index"
- "Rebuild the database"

**Example:**
```
"Reindex this project"
"Refresh the code index"
```

---

### Tool: `index_file`
**Ask:**
- "Index [filename]"
- "Add [file] to index"

**Example:**
```
"Index test_installation.py"
```

---

### Tool: `find_todo_and_fixme`
**Ask:**
- "Show all TODOs"
- "Find FIXME comments"
- "List pending tasks"

**Example:**
```
"Show all TODO comments"
"Find all FIXMEs in the project"
```

---

### Tool: `get_file_history_summary`
**Ask:**
- "Show git history for [file]"
- "Who modified [file]?"
- "Show commit history of [file]"

**Example:**
```
"Show git history for workspace.py"
"Who has been working on indexing.py?"
```

---

## 💡 Pro Tips

### Combine Multiple Tools:
```
"Search for authentication code, then show me its dependencies"
"Find all TODO comments and check if any relate to testing"
"Analyze code metrics and show me the most complex files"
```

### Be Specific:
```
❌ "Tell me about this codebase"
✅ "Search for existing error handling code and show me usage examples"
```

### Use Context:
```
"Before I create a new parser function, check if similar functionality exists"
"I want to refactor get_workspace_db - what would break?"
```

---

## 🎯 Common Workflows

### Before Creating New Code:
1. "Search for existing [feature] code"
2. "Check if [functionality] already exists"
3. "Find similar files to [reference]"

### Before Refactoring:
1. "Check breaking changes for [function]"
2. "Show usage examples of [function]"
3. "What's the test coverage?"

### Understanding Codebase:
1. "Show the import graph"
2. "Get code metrics summary"
3. "What are the most complex files?"

### Daily Development:
1. "What changed recently?"
2. "Show all TODOs"
3. "Find dependencies of [file]"
