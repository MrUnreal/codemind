#!/usr/bin/env node
/**
 * CodeMind MCP Server - Node.js Wrapper
 * 
 * This wrapper launches the Python-based CodeMind MCP server.
 * It handles Python environment detection and passes through stdio for MCP communication.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Find Python executable
function findPython() {
  const pythonCommands = process.platform === 'win32' 
    ? ['python', 'py', 'python3']
    : ['python3', 'python'];

  for (const cmd of pythonCommands) {
    try {
      const result = require('child_process').spawnSync(cmd, ['--version'], { 
        stdio: 'pipe',
        encoding: 'utf-8'
      });
      
      if (result.status === 0) {
        return cmd;
      }
    } catch (error) {
      // Command not found, try next
      continue;
    }
  }

  throw new Error('Python not found. Please install Python 3.8 or higher.');
}

// Get the CodeMind script path
function getCodemindPath() {
  // When installed via npm, codemind.py should be in the same directory as package.json
  const packageDir = path.dirname(__dirname);
  const codemindPath = path.join(packageDir, 'codemind.py');
  
  if (!fs.existsSync(codemindPath)) {
    throw new Error(`CodeMind script not found at: ${codemindPath}`);
  }
  
  return codemindPath;
}

// Main execution
async function main() {
  try {
    const pythonCmd = findPython();
    const codemindPath = getCodemindPath();
    
    // Spawn Python process with stdio inheritance for MCP communication
    const python = spawn(pythonCmd, [codemindPath], {
      stdio: 'inherit',
      cwd: process.cwd(),
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        FASTMCP_QUIET: '1'
      }
    });

    // Handle process exit
    python.on('exit', (code, signal) => {
      if (signal) {
        console.error(`CodeMind was killed with signal ${signal}`);
        process.exit(1);
      } else if (code !== 0) {
        console.error(`CodeMind exited with code ${code}`);
        process.exit(code);
      }
      process.exit(0);
    });

    // Handle errors
    python.on('error', (error) => {
      console.error(`Failed to start CodeMind: ${error.message}`);
      process.exit(1);
    });

    // Handle process termination signals
    process.on('SIGTERM', () => python.kill('SIGTERM'));
    process.on('SIGINT', () => python.kill('SIGINT'));

  } catch (error) {
    console.error(`Error: ${error.message}`);
    console.error('\nTroubleshooting:');
    console.error('1. Ensure Python 3.8+ is installed');
    console.error('2. Install dependencies: pip install -r requirements.txt');
    console.error('3. Check that codemind.py exists in the package directory');
    process.exit(1);
  }
}

// Run the wrapper
main();
