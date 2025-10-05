"""
Phase 4 Tool Implementations - Clean versions for testing
"""

import re
import json
from pathlib import Path

# Mock imports for standalone testing
CONFIG = {'project_root': Path(__file__).parent}

def check_breaking_changes(function_name: str, file_path: str, db_conn) -> str:
    """
    Analyze impact of modifying a function/class signature.
    Returns severity rating and list of affected files.
    """
    result = [f"🔍 Breaking Change Analysis for '{function_name}':\n"]
    
    # Check if it's exported (public API)
    is_public = False
    cursor = db_conn.execute(
        "SELECT key_exports FROM files WHERE path = ?",
        (file_path,)
    )
    row = cursor.fetchone()
    if row and row[0]:
        exports = json.loads(row[0])
        is_public = function_name in exports
    
    # Find all call sites
    call_sites = []
    cursor = db_conn.execute('SELECT path FROM files')
    
    for (path,) in cursor.fetchall():
        fpath = Path(CONFIG['project_root']) / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            # Find calls to this function
            pattern = rf'\b{re.escape(function_name)}\s*\('
            matches = list(re.finditer(pattern, content))
            
            if matches:
                # Get line numbers
                lines = content.split('\n')
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    # Get surrounding context
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 1)
                    context = '\n    '.join(lines[context_start:context_end])
                    
                    call_sites.append({
                        'file': path,
                        'line': line_num,
                        'context': context[:200]  # Limit context
                    })
        except:
            continue
    
    # Calculate severity
    num_sites = len(call_sites)
    if num_sites == 0:
        severity = "✅ SAFE"
        severity_desc = "No call sites found - safe to modify"
    elif num_sites <= 3:
        severity = "⚠️ LOW RISK"
        severity_desc = f"Only {num_sites} call sites - easy to fix"
    elif num_sites <= 10:
        severity = "⚠️ MODERATE RISK"
        severity_desc = f"{num_sites} call sites - needs careful review"
    else:
        severity = "🚨 HIGH RISK"
        severity_desc = f"{num_sites} call sites - significant refactoring needed"
    
    # Build report
    result.append(f"📊 **Call Sites Found**: {num_sites}")
    result.append(f"🔐 **Public API**: {'Yes - exported in module' if is_public else 'No - internal function'}")
    result.append(f"⚡ **Severity**: {severity}")
    result.append(f"📝 **Assessment**: {severity_desc}\n")
    
    if is_public:
        result.append("⚠️ WARNING: This is a public API. Changes may break external code!\n")
    
    if call_sites:
        # Group by file
        by_file = {}
        for site in call_sites:
            if site['file'] not in by_file:
                by_file[site['file']] = []
            by_file[site['file']].append(site)
        
        result.append(f"📁 **Affected Files** ({len(by_file)} files):\n")
        
        for file, sites in sorted(by_file.items())[:10]:  # Limit to 10 files
            result.append(f"  • {file} ({len(sites)} occurrences)")
            for site in sites[:2]:  # Show first 2 per file
                result.append(f"    Line {site['line']}")
        
        if len(by_file) > 10:
            result.append(f"\n  ... and {len(by_file) - 10} more files")
    else:
        result.append("✅ No call sites found - safe to modify or remove")
    
    result.append(f"\n💡 Tip: Use get_call_tree() for detailed call flow analysis")
    
    return "\n".join(result)


def find_usage_examples(function_name: str, file_path: str | None, limit: int, db_conn) -> str:
    """
    Find real usage examples of a function/class across the codebase.
    Returns examples with file, line number, and surrounding context.
    """
    result = [f"📚 Usage Examples for '{function_name}':\n"]
    
    examples = []
    cursor = db_conn.execute('SELECT path FROM files')
    
    # Skip the definition file if provided
    skip_file = file_path
    
    for (path,) in cursor.fetchall():
        if path == skip_file:
            continue  # Skip definition file, show usage elsewhere
            
        fpath = Path(CONFIG['project_root']) / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Find usage (not definition)
            pattern = rf'\b{re.escape(function_name)}\s*\('
            
            for i, line in enumerate(lines):
                # Skip if this is the definition line
                if re.match(rf'\s*(def|class)\s+{re.escape(function_name)}\b', line):
                    continue
                
                if re.search(pattern, line):
                    # Get surrounding context
                    context_start = max(0, i - 1)
                    context_end = min(len(lines), i + 2)
                    context_lines = lines[context_start:context_end]
                    
                    examples.append({
                        'file': path,
                        'line': i + 1,
                        'context': '\n'.join(context_lines),
                        'usage_line': line.strip()
                    })
                    
                    if len(examples) >= limit * 3:  # Collect more than needed
                        break
        except:
            continue
        
        if len(examples) >= limit * 3:
            break
    
    if not examples:
        result.append(f"❌ No usage examples found for '{function_name}'")
        result.append(f"\nPossible reasons:")
        result.append(f"  • Function is defined but not yet used")
        result.append(f"  • Function name is incorrect")
        result.append(f"  • Files haven't been indexed yet")
        result.append(f"\n💡 Try: search_by_export('{function_name}') to verify it exists")
        return "\n".join(result)
    
    # Show top examples
    for i, ex in enumerate(examples[:limit], 1):
        result.append(f"\n**Example {i}**: {ex['file']}:{ex['line']}")
        result.append(f"```")
        result.append(ex['context'])
        result.append(f"```")
    
    if len(examples) > limit:
        result.append(f"\n... found {len(examples) - limit} more examples")
        result.append(f"(use limit parameter to see more)")
    
    result.append(f"\n💡 Found {min(limit, len(examples))} of {len(examples)} total usages")
    
    return "\n".join(result)


def find_todo_and_fixme(tag_type: str, search_term: str | None, limit: int, db_conn) -> str:
    """
    Search all TODO, FIXME, HACK, XXX comments with context.
    Returns grouped comments with file, line, and context.
    """
    tag_type = tag_type.upper()
    valid_tags = ["TODO", "FIXME", "HACK", "XXX", "NOTE", "BUG"]
    
    if tag_type not in valid_tags:
        return f"❌ Invalid tag type. Use one of: {', '.join(valid_tags)}"
    
    result = [f"🔍 Searching for {tag_type} comments" + (f" matching '{search_term}'" if search_term else "") + ":\n"]
    
    findings = []
    cursor = db_conn.execute('SELECT path FROM files')
    
    for (path,) in cursor.fetchall():
        fpath = Path(CONFIG['project_root']) / path
        if not fpath.exists():
            continue
        
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Match comments with tag
            pattern = rf'#.*{tag_type}:?\s*(.+)$'
            
            for i, line in enumerate(lines):
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    comment_text = match.group(1).strip()
                    
                    # Filter by search term if provided
                    if search_term and search_term.lower() not in comment_text.lower():
                        continue
                    
                    # Get surrounding context (code being marked)
                    context_start = max(0, i - 1)
                    context_end = min(len(lines), i + 2)
                    context = '\n    '.join(lines[context_start:context_end])
                    
                    findings.append({
                        'file': path,
                        'line': i + 1,
                        'comment': comment_text,
                        'context': context[:300]  # Limit context
                    })
                    
                    if len(findings) >= limit * 2:
                        break
        except:
            continue
        
        if len(findings) >= limit * 2:
            break
    
    if not findings:
        result.append(f"✅ No {tag_type} comments found" + (f" matching '{search_term}'" if search_term else ""))
        result.append(f"\nThis could mean:")
        result.append(f"  • Clean codebase (good!)")
        result.append(f"  • Different tag conventions used")
        result.append(f"  • Files not yet indexed")
        return "\n".join(result)
    
    # Group by file
    by_file = {}
    for finding in findings:
        if finding['file'] not in by_file:
            by_file[finding['file']] = []
        by_file[finding['file']].append(finding)
    
    result.append(f"📊 Found {len(findings)} {tag_type} comments in {len(by_file)} files:\n")
    
    # Show findings grouped by file
    for file, items in sorted(by_file.items())[:limit]:
        result.append(f"\n📁 **{file}** ({len(items)} items):")
        for item in items[:3]:  # Show first 3 per file
            result.append(f"  • Line {item['line']}: {item['comment']}")
    
    if len(findings) > limit:
        result.append(f"\n... {len(findings) - limit} more {tag_type} comments found")
        result.append(f"(increase limit parameter to see more)")
    
    # Priority hints
    if tag_type == "FIXME":
        result.append(f"\n⚠️ FIXME comments indicate bugs or issues that need attention")
    elif tag_type == "HACK":
        result.append(f"\n⚠️ HACK comments indicate technical debt or workarounds")
    elif tag_type == "XXX":
        result.append(f"\n🚨 XXX comments often indicate critical issues")
    
    result.append(f"\n💡 Tip: Use search_term parameter to filter by keyword")
    
    return "\n".join(result)


def get_file_history_summary(file_path: str, days_back: int) -> str:
    """
    Git history analysis - who changes this file, how often, recent activity.
    Returns commit count, contributors, frequency, and risk rating.
    """
    result = [f"📜 Git History for '{file_path}' (last {days_back} days):\n"]
    
    fpath = Path(CONFIG['project_root']) / file_path
    if not fpath.exists():
        return f"❌ File not found: {file_path}"
    
    try:
        # Check if git is available
        import subprocess
        
        # Get commit count
        cmd_count = ['git', 'log', '--oneline', f'--since={days_back} days ago', '--', file_path]
        count_result = subprocess.run(
            cmd_count,
            cwd=CONFIG['project_root'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if count_result.returncode != 0:
            return f"❌ Git not available or not a git repository\n💡 This tool requires Git to be installed"
        
        commits = count_result.stdout.strip().split('\n')
        commit_count = len([c for c in commits if c])
        
        # Get contributors
        cmd_authors = ['git', 'log', '--format=%an', f'--since={days_back} days ago', '--', file_path]
        authors_result = subprocess.run(
            cmd_authors,
            cwd=CONFIG['project_root'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        authors = [a for a in authors_result.stdout.strip().split('\n') if a]
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get last modified date
        cmd_last = ['git', 'log', '-1', '--format=%ar', '--', file_path]
        last_result = subprocess.run(
            cmd_last,
            cwd=CONFIG['project_root'],
            capture_output=True,
            text=True,
            timeout=5
        )
        last_modified = last_result.stdout.strip() or "Unknown"
        
        # Calculate metrics
        months = days_back / 30
        commits_per_month = commit_count / months if months > 0 else 0
        
        # Risk rating
        if commits_per_month >= 10:
            risk = "🔴 HIGH"
            risk_desc = "Very frequently changed - high fragility risk"
        elif commits_per_month >= 5:
            risk = "🟡 MEDIUM"
            risk_desc = "Moderately active - some risk of conflicts"
        elif commits_per_month >= 1:
            risk = "🟢 LOW"
            risk_desc = "Stable with occasional updates"
        else:
            risk = "✅ VERY LOW"
            risk_desc = "Rarely changed - very stable"
        
        # Build report
        result.append(f"📊 **Commits** ({days_back} days): {commit_count}")
        result.append(f"📈 **Change Rate**: {commits_per_month:.1f} commits/month")
        result.append(f"🕐 **Last Modified**: {last_modified}")
        result.append(f"⚡ **Risk Level**: {risk}")
        result.append(f"📝 **Assessment**: {risk_desc}\n")
        
        if top_authors:
            result.append(f"👥 **Top Contributors**:")
            for author, count in top_authors:
                percentage = (count / commit_count * 100) if commit_count > 0 else 0
                result.append(f"  • {author}: {count} commits ({percentage:.0f}%)")
        
        result.append(f"\n💡 Expert to ask: {top_authors[0][0] if top_authors else 'Unknown'}")
        
        if commit_count == 0:
            result.append(f"\n✅ No recent commits - file is stable")
        
    except subprocess.TimeoutExpired:
        return f"❌ Git command timed out\n💡 Large repository - try shorter days_back"
    except FileNotFoundError:
        return f"❌ Git not found\n💡 Install Git to use this tool"
    except Exception as e:
        return f"❌ Error analyzing git history: {str(e)}"
    
    return "\n".join(result)


def get_test_coverage(file_path: str, db_conn) -> str:
    """
    Show test coverage for a specific file/module.
    Returns coverage estimate, test file locations, and recommendations.
    """
    result = [f"🧪 Test Coverage Analysis for '{file_path}':\n"]
    
    fpath = Path(CONFIG['project_root']) / file_path
    if not fpath.exists():
        return f"❌ File not found: {file_path}"
    
    try:
        # Read the file to get functions
        content = fpath.read_text(encoding='utf-8', errors='ignore')
        
        # Extract function/class names
        functions = re.findall(r'def\s+([a-zA-Z_]\w*)\s*\(', content)
        classes = re.findall(r'class\s+([a-zA-Z_]\w*)', content)
        
        # Filter out private functions
        public_functions = [f for f in functions if not f.startswith('_')]
        
        if not public_functions and not classes:
            return f"⚠️ No public functions or classes found in {file_path}"
        
        result.append(f"📦 **Found**:")
        if classes:
            result.append(f"  • {len(classes)} classes: {', '.join(classes[:5])}")
        if public_functions:
            result.append(f"  • {len(public_functions)} public functions: {', '.join(public_functions[:5])}")
        result.append("")
        
        # Find test files (heuristic approach)
        test_files = []
        cursor = db_conn.execute('SELECT path FROM files')
        
        base_name = Path(file_path).stem
        
        for (test_path,) in cursor.fetchall():
            # Look for test files that might test this file
            if 'test' in test_path.lower() and base_name.lower() in test_path.lower():
                test_files.append(test_path)
        
        # Count tested items by searching test files
        tested_items = set()
        
        for test_file in test_files:
            test_fpath = Path(CONFIG['project_root']) / test_file
            if not test_fpath.exists():
                continue
            
            try:
                test_content = test_fpath.read_text(encoding='utf-8', errors='ignore')
                
                # Check which functions/classes are referenced in tests
                for func in public_functions:
                    if re.search(rf'\b{re.escape(func)}\b', test_content):
                        tested_items.add(func)
                
                for cls in classes:
                    if re.search(rf'\b{re.escape(cls)}\b', test_content):
                        tested_items.add(cls)
            except:
                continue
        
        # Calculate coverage
        total_items = len(public_functions) + len(classes)
        tested_count = len(tested_items)
        coverage_pct = (tested_count / total_items * 100) if total_items > 0 else 0
        
        # Rating
        if coverage_pct >= 80:
            rating = "✅ EXCELLENT"
            color = "🟢"
        elif coverage_pct >= 60:
            rating = "👍 GOOD"
            color = "🟡"
        elif coverage_pct >= 40:
            rating = "⚠️ MODERATE"
            color = "🟠"
        else:
            rating = "🔴 LOW"
            color = "🔴"
        
        result.append(f"{color} **Estimated Coverage**: {coverage_pct:.0f}% ({tested_count}/{total_items} items)")
        result.append(f"📊 **Rating**: {rating}\n")
        
        if tested_items:
            result.append(f"✅ **Tested** ({len(tested_items)} items):")
            for item in sorted(tested_items)[:10]:
                result.append(f"  • {item}")
            if len(tested_items) > 10:
                result.append(f"  ... and {len(tested_items) - 10} more")
            result.append("")
        
        untested = set(public_functions + classes) - tested_items
        if untested:
            result.append(f"❌ **Untested** ({len(untested)} items):")
            for item in sorted(untested)[:10]:
                result.append(f"  • {item}")
            if len(untested) > 10:
                result.append(f"  ... and {len(untested) - 10} more")
            result.append("")
        
        if test_files:
            result.append(f"📁 **Test Files** ({len(test_files)}):")
            for tf in test_files[:5]:
                result.append(f"  • {tf}")
            if len(test_files) > 5:
                result.append(f"  ... and {len(test_files) - 5} more")
        else:
            result.append(f"⚠️ **No test files found**")
            result.append(f"  Suggestion: Create tests/test_{base_name}.py")
        
        # Recommendations
        result.append(f"\n💡 **Recommendations**:")
        if coverage_pct < 60:
            result.append(f"  • Add tests for untested functions")
            result.append(f"  • Target: 60%+ coverage for production code")
        if not test_files:
            result.append(f"  • Create test file: tests/test_{base_name}.py")
        if coverage_pct >= 80:
            result.append(f"  • Excellent coverage - maintain this level!")
        
    except Exception as e:
        return f"❌ Error analyzing coverage: {str(e)}"
    
    return "\n".join(result)


if __name__ == "__main__":
    print("✅ Phase 4 tool implementations loaded successfully!")
    print("5 tools ready:")
    print("  1. check_breaking_changes")
    print("  2. find_usage_examples")
    print("  3. find_todo_and_fixme")
    print("  4. get_file_history_summary")
    print("  5. get_test_coverage")
