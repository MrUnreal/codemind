"""Test find_configuration_inconsistencies tool"""
import json
import re
import os
from pathlib import Path

PROJECT_ROOT = Path(".").resolve()
CONFIG = {"project_root": "./", "watched_extensions": [".py", ".js", ".ts"], "max_file_size_kb": 500}

def find_configuration_inconsistencies_test(include_examples=True):
    """Test configuration analysis"""
    try:
        project_root = PROJECT_ROOT
        
        # Configuration file patterns
        config_patterns = {
            'json': ['*.json', 'config/*.json', '.vscode/*.json'],
            'yaml': ['*.yml', '*.yaml', 'config/*.yml', 'config/*.yaml'],
            'env': ['.env', '.env.*', '*.env'],
            'ini': ['*.ini', '*.cfg', 'setup.cfg'],
            'py': ['config.py', 'settings.py', '**/config.py', '**/settings.py']
        }
        
        # Find all config files
        config_files = {}
        for file_type, patterns in config_patterns.items():
            config_files[file_type] = []
            for pattern in patterns:
                for fp in project_root.glob(pattern):
                    if fp.is_file() and not any(p.startswith('.git') for p in fp.parts):
                        try:
                            config_files[file_type].append(str(fp.relative_to(project_root)))
                        except ValueError:
                            pass
        
        # Parse configuration values
        all_configs = {}
        secret_patterns = re.compile(r'(api[_-]?key|secret|password|token|auth|credential|private[_-]?key)', re.IGNORECASE)
        
        for file_type, files in config_files.items():
            for config_file in files:
                full_path = project_root / config_file
                try:
                    with open(full_path, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    config_data = {}
                    
                    if file_type == 'json':
                        try:
                            data = json.loads(content)
                            if isinstance(data, dict):
                                config_data = {k: str(v) for k, v in data.items() if not isinstance(v, (dict, list))}
                        except json.JSONDecodeError:
                            pass
                    
                    if config_data:
                        all_configs[config_file] = config_data
                
                except Exception as e:
                    print(f"Error parsing {config_file}: {e}")
        
        # Detect hardcoded secrets and security risks
        hardcoded_secrets = []
        security_risks = []
        
        for filename, config_data in all_configs.items():
            for key, value in config_data.items():
                # Check for hardcoded secrets
                if secret_patterns.search(key) and value and not value.startswith('$'):
                    if len(value) > 5 and value.lower() not in ['none', 'null', 'false', 'true']:
                        masked_value = value[:3] + '***' if len(value) > 6 else '***'
                        hardcoded_secrets.append({
                            'file': filename,
                            'key': key,
                            'value': masked_value,
                            'risk': 'HIGH' if 'prod' in filename.lower() else 'MEDIUM'
                        })
                
                # Check for security risks
                if key.upper() == 'DEBUG' and value.lower() in ['true', '1', 'yes']:
                    env_type = 'production' if 'prod' in filename.lower() else 'development'
                    if env_type == 'production':
                        security_risks.append({
                            'file': filename,
                            'issue': 'DEBUG=true in production',
                            'risk': 'HIGH'
                        })
        
        # Build result
        result = [""]
        result.append("=" * 70)
        result.append("🔧 CONFIGURATION ANALYSIS")
        result.append("=" * 70)
        result.append("")
        
        result.append("📁 **CONFIGURATION FILES**")
        total_files = sum(len(files) for files in config_files.values())
        result.append(f"  Total Files: {total_files}")
        for file_type, files in config_files.items():
            if files:
                result.append(f"  {file_type.upper()}: {len(files)} files")
                for f in files[:3]:
                    result.append(f"    • {f}")
                if len(files) > 3:
                    result.append(f"    ... and {len(files) - 3} more")
        result.append("")
        
        result.append("🚨 **SECURITY RISKS**")
        if security_risks:
            result.append(f"  Found: {len(security_risks)} issues")
            for risk in security_risks:
                result.append(f"  ⚠️  {risk['file']}: {risk['issue']}")
        else:
            result.append(f"  ✅ No security risks detected")
        result.append("")
        
        result.append("🔐 **HARDCODED SECRETS**")
        if hardcoded_secrets:
            result.append(f"  Found: {len(hardcoded_secrets)} potential secrets")
            for secret in hardcoded_secrets[:5]:
                result.append(f"  {secret['risk']} RISK: {secret['file']}")
                result.append(f"    Key: {secret['key']}")
                if include_examples:
                    result.append(f"    Value: {secret['value']}")
            if len(hardcoded_secrets) > 5:
                result.append(f"  ... and {len(hardcoded_secrets) - 5} more")
        else:
            result.append(f"  ✅ No hardcoded secrets detected")
        result.append("")
        
        result.append("=" * 70)
        
        return "\n".join(result)
        
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    print("Testing find_configuration_inconsistencies...")
    print(find_configuration_inconsistencies_test(include_examples=True))
