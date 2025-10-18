# Security Policy

## Supported Versions

We take security seriously and actively maintain the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.1.x   | :x:                |
| 1.0.x   | :x:                |

## Security Considerations

### Data Privacy

CodeMind is designed with privacy as a core principle:

- **100% Local Processing**: All data processing happens on your machine
- **No Network Calls**: CodeMind does not send data to external services
- **Local Storage Only**: Data is stored in `.codemind/` directory in your workspace
- **No Telemetry**: No usage tracking or analytics

### What Data is Stored Locally

CodeMind stores the following data in `.codemind/`:

1. **File Metadata**: File paths, sizes, and modification times
2. **Code Embeddings**: Semantic vectors for search functionality
3. **Parsed Information**: AST-derived data (imports, functions, exports)
4. **Decisions**: Architecture decisions you explicitly record
5. **Change History**: File modification tracking

**You can delete this data at any time** by removing the `.codemind/` directory.

### Database Security

- **SQLite Database**: Local file-based storage
- **No Authentication Required**: Data is only accessible to your user account
- **Parameterized Queries**: All database queries use parameter binding to prevent SQL injection
- **No Sensitive Data**: Passwords, secrets, and credentials are never stored

### File System Access

CodeMind only accesses:
- Files in the specified workspace directory
- `.codemind/` directory for its database and logs

CodeMind **never**:
- Modifies your source code files
- Accesses files outside the workspace
- Deletes files
- Executes code from your workspace

### Configuration Security

**Best Practices**:
- Add `.codemind/` to your `.gitignore`
- Don't commit workspace databases to version control
- Use environment variables for sensitive configuration (if any)

## Reporting a Vulnerability

We appreciate responsible disclosure of security vulnerabilities.

### How to Report

**For security vulnerabilities, please DO NOT create a public GitHub issue.**

Instead:

1. **Email the maintainers** via GitHub private message or:
   - Open a [Security Advisory](https://github.com/MrUnreal/codemind/security/advisories/new)
   - Or create a private issue marked as "Security"

2. **Include in your report**:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if you have one)
   - Your contact information

3. **Response Timeline**:
   - **Initial Response**: Within 48 hours
   - **Assessment**: Within 1 week
   - **Fix Development**: Depends on severity
   - **Disclosure**: After fix is released

### What to Expect

1. **Acknowledgment**: We'll confirm receipt of your report
2. **Assessment**: We'll evaluate severity and impact
3. **Fix Development**: We'll work on a fix (with your help if desired)
4. **Testing**: We'll verify the fix resolves the issue
5. **Release**: We'll release a patched version
6. **Disclosure**: We'll credit you (unless you prefer to remain anonymous)

### Severity Levels

**Critical** (Immediate attention):
- Remote code execution
- Data exfiltration
- Privilege escalation

**High** (Fix within 1 week):
- SQL injection
- Path traversal
- Denial of service

**Medium** (Fix within 2 weeks):
- Information disclosure
- Configuration vulnerabilities

**Low** (Fix in next regular release):
- Minor information leaks
- Non-exploitable bugs

## Security Best Practices for Users

### Installation Security

1. **Verify Source**: Only install from official sources
   ```bash
   # Official GitHub repository
   git clone https://github.com/MrUnreal/codemind.git
   
   # Official PyPI package (when available)
   pip install mcp-codemind
   ```

2. **Check Integrity**: Verify checksums for releases

3. **Use Virtual Environments**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

### Usage Security

1. **Workspace Isolation**: Each project should use its own workspace
2. **Sensitive Files**: Add sensitive files to `.gitignore`
3. **Regular Updates**: Keep CodeMind updated to get security patches
4. **Review Logs**: Periodically check `.codemind/logs/` for anomalies

### Configuration Security

**Secure configuration example**:
```json
{
  "watched_extensions": [".py", ".js", ".ts"],
  "exclude_dirs": [".git", ".env", "secrets/"],
  "max_file_size_kb": 500
}
```

**Avoid**:
- Storing credentials in configuration
- Including sensitive directories in watched paths
- Overly permissive file access

## Known Security Limitations

### Current Limitations

1. **Local File Access**: CodeMind can read any file in the workspace directory
   - **Mitigation**: Use `exclude_dirs` to skip sensitive directories

2. **Code Parsing**: AST parsing could potentially crash on malicious Python files
   - **Mitigation**: File size limits and graceful error handling

3. **Embedding Model**: Downloaded from Hugging Face on first run
   - **Mitigation**: Model checksum verification (planned)

### Not in Scope

The following are not considered security issues:
- Local denial of service (user can stop the process)
- Excessive disk usage (user controls workspace size)
- Performance issues
- Feature limitations

## Security Updates

Security updates are released as soon as possible after verification:

1. **Critical**: Immediate patch release
2. **High**: Within 1 week
3. **Medium**: Within 2 weeks
4. **Low**: Next regular release

**Update notifications**:
- GitHub Security Advisories
- Release notes in CHANGELOG.md
- GitHub releases page

## Security Checklist for Contributors

When contributing code, please ensure:

- [ ] No hardcoded credentials or secrets
- [ ] All database queries use parameterized queries
- [ ] File paths are validated before access
- [ ] User input is validated and sanitized
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies are from trusted sources
- [ ] New features have security considerations documented

## Third-Party Dependencies

CodeMind uses these dependencies:

| Package | Purpose | Security Notes |
|---------|---------|----------------|
| fastmcp | MCP protocol | Official MCP implementation |
| sentence-transformers | Embeddings | Popular, well-maintained |
| numpy | Numerical operations | Widely used, secure |
| radon | Code metrics | Static analysis only |
| GitPython | Git operations | Read-only usage |

**Dependency Security**:
- We regularly update dependencies for security patches
- We monitor security advisories for our dependencies
- We pin versions in `requirements.txt` for reproducibility

## Disclosure Policy

When security vulnerabilities are fixed:

1. **Patch First**: Fix is developed and tested privately
2. **Release**: Patched version is released
3. **Announce**: Security advisory is published
4. **Credit**: Reporter is credited (if desired)
5. **Details**: Technical details disclosed after users have time to update (typically 30 days)

## Contact

For security concerns:
- **Security Advisories**: [GitHub Security](https://github.com/MrUnreal/codemind/security)
- **Private Reporting**: Via GitHub private message
- **General Issues**: [GitHub Issues](https://github.com/MrUnreal/codemind/issues) (non-security only)

---

**Last Updated**: October 2024

Thank you for helping keep CodeMind secure! 🔒
