# Testing CodeMind MCP Connection

## How to Verify CodeMind is Working:

### Method 1: Check MCP Status (if available in your VS Code version)
1. Press `Ctrl+Shift+P`
2. Look for commands starting with "MCP:"
   - `MCP: Show Servers`
   - `MCP: Restart Servers`
   - `MCP: View Logs`

### Method 2: Test with Copilot Chat
After reloading VS Code, open Copilot Chat and ask:

```
Can you search for existing code in this project?
```

or

```
What tools do you have access to from CodeMind?
```

If CodeMind is working, Copilot should mention having access to tools like:
- search_existing_code
- get_file_context
- find_dependencies
- etc.

### Method 3: Check for Server Logs
After reloading, look for these files:
- `.codemind/logs/session_YYYYMMDD_HHMMSS.log`

If the file appears, the server started successfully!

### Method 4: Check VS Code Output
1. Press `Ctrl+Shift+U` (Output panel)
2. Look for dropdown at top right
3. Select "GitHub Copilot" or "MCP" if available
4. Look for messages about CodeMind server starting

---

## Troubleshooting:

### If CodeMind doesn't connect:

1. **Check settings.json path**
   - Settings file location: `.vscode/settings.json`
   - Python path should be absolute: `e:\\Projects\\Python\\codemind\\codemind.py`

2. **Check GitHub Copilot is installed and active**
   - Extensions → GitHub Copilot should be enabled
   - You should see Copilot icon in status bar

3. **Try running server manually to see errors:**
   ```bash
   python codemind.py
   ```
   (Press Ctrl+C to stop)

4. **Check VS Code version supports MCP**
   - MCP is a newer feature
   - Make sure you have latest VS Code
   - GitHub Copilot extension should be updated
