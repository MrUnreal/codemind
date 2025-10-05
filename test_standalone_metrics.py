"""Standalone test for get_code_metrics_summary logic"""
import re
import os
from pathlib import Path
import math

# Configuration
PROJECT_ROOT = Path(".").resolve()
WATCHED_EXTENSIONS = [".py", ".js", ".ts"]
MAX_FILE_SIZE_KB = 500

def get_code_metrics_summary_test(detailed=False):
    """Test the metrics logic"""
    try:
        # Initialize counters
        total_files = 0
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        total_functions = 0
        total_classes = 0
        function_lengths = []
        
        files_with_docstrings = 0
        high_complexity_files = []
        long_functions = []
        code_smells = {
            "magic_numbers": 0,
            "long_parameter_lists": 0,
            "deep_nesting": 0,
            "dead_imports": 0,
            "long_lines": 0
        }
        
        file_metrics = []
        
        # Scan all files
        for ext in WATCHED_EXTENSIONS:
            for fp in PROJECT_ROOT.rglob(f"*{ext}"):
                if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                    try:
                        if fp.stat().st_size // 1024 > MAX_FILE_SIZE_KB:
                            continue
                        
                        with open(fp, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                        
                        total_files += 1
                        file_total_lines = len(lines)
                        total_lines += file_total_lines
                        
                        # Classify lines
                        file_code_lines = 0
                        file_comment_lines = 0
                        file_blank_lines = 0
                        file_has_docstring = False
                        
                        in_multiline_comment = False
                        for line in lines:
                            stripped = line.strip()
                            
                            if not stripped:
                                file_blank_lines += 1
                                blank_lines += 1
                            elif stripped.startswith('"""') or stripped.startswith("'''"):
                                file_comment_lines += 1
                                comment_lines += 1
                                file_has_docstring = True
                                if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                                    in_multiline_comment = not in_multiline_comment
                            elif in_multiline_comment:
                                file_comment_lines += 1
                                comment_lines += 1
                            elif stripped.startswith('#'):
                                file_comment_lines += 1
                                comment_lines += 1
                            elif stripped.startswith('//') or stripped.startswith('/*'):
                                file_comment_lines += 1
                                comment_lines += 1
                            else:
                                file_code_lines += 1
                                code_lines += 1
                                
                                # Check for long lines
                                if len(line) > 120:
                                    code_smells["long_lines"] += 1
                        
                        if file_has_docstring:
                            files_with_docstrings += 1
                        
                        # Extract functions and complexity
                        file_functions = 0
                        file_classes = 0
                        file_complexity = 0
                        
                        # Find functions (Python, JS, TS)
                        function_pattern = r'(?:def|function)\s+(\w+)\s*\('
                        for match in re.finditer(function_pattern, content):
                            file_functions += 1
                            total_functions += 1
                            
                            # Get function body to analyze
                            func_start = match.start()
                            func_content = content[func_start:func_start + 2000]
                            
                            # Count parameters
                            param_match = re.search(r'\((.*?)\)', func_content)
                            if param_match:
                                params = [p.strip() for p in param_match.group(1).split(',') if p.strip() and p.strip() != 'self']
                                param_count = len(params)
                                if param_count > 5:
                                    code_smells["long_parameter_lists"] += 1
                            
                            # Estimate function length
                            func_lines = len(func_content.split('\n'))
                            function_lengths.append(min(func_lines, 50))
                            
                            if func_lines > 100:
                                long_functions.append({
                                    "file": str(fp.relative_to(PROJECT_ROOT)),
                                    "function": match.group(1) if match.groups() else "unknown",
                                    "lines": func_lines
                                })
                            
                            # Estimate complexity
                            complexity = len(re.findall(r'\b(if|elif|else|for|while|and|or|try|except|case)\b', func_content))
                            file_complexity += complexity
                            
                            # Check for deep nesting
                            max_indent = 0
                            for line in func_content.split('\n'):
                                if line.strip():
                                    indent = len(line) - len(line.lstrip())
                                    max_indent = max(max_indent, indent)
                            if max_indent > 16:
                                code_smells["deep_nesting"] += 1
                        
                        # Find classes
                        class_pattern = r'class\s+(\w+)'
                        file_classes = len(re.findall(class_pattern, content))
                        total_classes += file_classes
                        
                        # Find magic numbers
                        magic_numbers = re.findall(r'\b(?<!\.)\d{2,}\b(?!\.)', content)
                        code_smells["magic_numbers"] += len([n for n in magic_numbers if n not in ['0', '1', '2', '10', '100']])
                        
                        # Find dead imports (Python only)
                        if fp.suffix == '.py':
                            import_pattern = r'(?:from\s+[\w.]+\s+)?import\s+([\w\s,]+)'
                            for match in re.finditer(import_pattern, content):
                                imports = [i.strip() for i in match.group(1).split(',')]
                                for imp in imports:
                                    imp_name = imp.split()[0] if imp else ''
                                    if imp_name and content.count(imp_name) == 1:
                                        code_smells["dead_imports"] += 1
                        
                        # Calculate file complexity
                        if file_functions > 0:
                            avg_complexity = file_complexity / file_functions
                        else:
                            avg_complexity = 0
                        
                        if avg_complexity > 10 or file_complexity > 30:
                            high_complexity_files.append({
                                "file": str(fp.relative_to(PROJECT_ROOT)),
                                "complexity": file_complexity,
                                "functions": file_functions
                            })
                        
                        file_metrics.append({
                            "file": str(fp.relative_to(PROJECT_ROOT)),
                            "lines": file_total_lines,
                            "code": file_code_lines,
                            "comments": file_comment_lines,
                            "functions": file_functions,
                            "classes": file_classes,
                            "complexity": file_complexity
                        })
                        
                    except Exception as e:
                        print(f"Error analyzing {fp}: {e}")
        
        # Calculate maintainability index
        avg_complexity = (sum(f["complexity"] for f in file_metrics) / len(file_metrics)) if file_metrics else 0
        avg_file_size = total_lines / total_files if total_files > 0 else 0
        
        maintainability = max(0, min(100, 
            171 - 0.23 * avg_complexity - 16.2 * math.log(max(1, avg_file_size))
        ))
        
        # Build result
        result = [" "]
        result.append("=" * 70)
        result.append("📊 CODE METRICS SUMMARY")
        result.append("=" * 70)
        result.append("")
        
        # Project Statistics
        result.append("📁 **PROJECT STATISTICS**")
        result.append(f"  Total Files:    {total_files:,}")
        result.append(f"  Total Lines:    {total_lines:,}")
        result.append(f"  Code Lines:     {code_lines:,} ({100*code_lines/max(1,total_lines):.1f}%)")
        result.append(f"  Comment Lines:  {comment_lines:,} ({100*comment_lines/max(1,total_lines):.1f}%)")
        result.append(f"  Blank Lines:    {blank_lines:,} ({100*blank_lines/max(1,total_lines):.1f}%)")
        result.append("")
        
        # Complexity
        result.append("🔥 **COMPLEXITY METRICS**")
        result.append(f"  Average per File: {avg_complexity:.1f}")
        if file_metrics:
            complexities = [f["complexity"] for f in file_metrics]
            result.append(f"  Median:           {sorted(complexities)[len(complexities)//2]}")
            result.append(f"  Max:              {max(complexities)}")
        
        if high_complexity_files:
            result.append(f"\n  ⚠️  High Complexity Files ({len(high_complexity_files)}):")
            for fc in sorted(high_complexity_files, key=lambda x: x["complexity"], reverse=True)[:5]:
                result.append(f"    • {fc['file']}: complexity={fc['complexity']}, functions={fc['functions']}")
            if len(high_complexity_files) > 5:
                result.append(f"    ... and {len(high_complexity_files) - 5} more")
        result.append("")
        
        # Function Statistics
        result.append("⚙️  **FUNCTION STATISTICS**")
        result.append(f"  Total Functions: {total_functions:,}")
        result.append(f"  Total Classes:   {total_classes:,}")
        if function_lengths:
            avg_length = sum(function_lengths) / len(function_lengths)
            result.append(f"  Avg Length:      {avg_length:.1f} lines")
            result.append(f"  Median Length:   {sorted(function_lengths)[len(function_lengths)//2]} lines")
        
        if long_functions:
            result.append(f"\n  📏 Long Functions ({len(long_functions)}):")
            for lf in sorted(long_functions, key=lambda x: x["lines"], reverse=True)[:5]:
                result.append(f"    • {lf['file']}::{lf['function']} ({lf['lines']} lines)")
            if len(long_functions) > 5:
                result.append(f"    ... and {len(long_functions) - 5} more")
        result.append("")
        
        # Documentation
        result.append("📚 **DOCUMENTATION**")
        doc_coverage = (100 * files_with_docstrings / max(1, total_files))
        result.append(f"  Files with Docstrings: {files_with_docstrings}/{total_files} ({doc_coverage:.1f}%)")
        result.append(f"  Comment Ratio:         {100*comment_lines/max(1,code_lines):.1f}%")
        
        if doc_coverage < 60:
            result.append(f"  ⚠️  Low documentation coverage")
        elif doc_coverage >= 80:
            result.append(f"  ✅ Good documentation coverage")
        result.append("")
        
        # Code Smells
        result.append("🔍 **CODE SMELLS**")
        result.append(f"  Magic Numbers:        {code_smells['magic_numbers']}")
        result.append(f"  Long Parameter Lists: {code_smells['long_parameter_lists']} (>5 params)")
        result.append(f"  Deep Nesting:         {code_smells['deep_nesting']} (>4 levels)")
        result.append(f"  Dead Imports:         {code_smells['dead_imports']}")
        result.append(f"  Long Lines:           {code_smells['long_lines']} (>120 chars)")
        
        total_smells = sum(code_smells.values())
        if total_smells == 0:
            result.append(f"  ✅ No major code smells detected!")
        elif total_smells < 50:
            result.append(f"  ✓  Few code smells - good quality")
        elif total_smells < 200:
            result.append(f"  ⚠️  Moderate code smells - review recommended")
        else:
            result.append(f"  ❌ Many code smells - refactoring needed")
        result.append("")
        
        # Maintainability Index
        result.append("💯 **MAINTAINABILITY INDEX**")
        result.append(f"  Score: {maintainability:.1f}/100")
        if maintainability >= 80:
            result.append(f"  ✅ Excellent - Easy to maintain")
        elif maintainability >= 60:
            result.append(f"  ✓  Good - Reasonably maintainable")
        elif maintainability >= 40:
            result.append(f"  ⚠️  Fair - Maintenance challenges ahead")
        else:
            result.append(f"  ❌ Poor - Significant refactoring recommended")
        result.append("")
        
        result.append("=" * 70)
        
        return "\n".join(result)
        
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    print("Testing get_code_metrics_summary...")
    print(get_code_metrics_summary_test(detailed=False))
