import re
import sys
from pathlib import Path


class SecretScanner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.findings = []
        
        self.secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{1,50}["\']', 'Hardcoded Password'),
            (r'api[_-]?key\s*=\s*["\'][^"\']{1,100}["\']', 'Hardcoded API Key'),
            (r'secret[_-]?key\s*=\s*["\'][^"\']{1,100}["\']', 'Hardcoded Secret Key'),
            (r'token\s*=\s*["\'][^"\']{1,100}["\']', 'Hardcoded Token'),
            (r'mongodb://[^:]+:[^@]+@', 'MongoDB Connection String with Credentials'),
            (r'mysql://[^:]+:[^@]+@', 'MySQL Connection String with Credentials'),
            (r'postgres://[^:]+:[^@]+@', 'PostgreSQL Connection String with Credentials'),
        ]
        
        self.weak_values = [
            ('secret', 'Weak Secret'),
            ('password', 'Weak Password'),
            ('12345', 'Weak Password'),
            ('admin', 'Default Admin Credential'),
            ('test', 'Test Credential'),
            ('changeme', 'Default Password'),
            ('default', 'Default Value'),
        ]
        
        self.exclude_dirs = {
            '__pycache__', 'venv', 'env', '.venv', '.env',
            'node_modules', '.git', 'dist', 'build',
            '.pytest_cache', 'htmlcov'
        }
        
        self.exclude_files = {
            'secret_scanner.py', 'endpoint_scanner.py',
            '.pyc', '.pyo', '.pyd'
        }
    
    def _mask_secret(self, text: str) -> str:
        import re
        masked = re.sub(r'(["\'][^"\']{0,3})[^"\']+([^"\']{0,3}["\'])', r'\1***MASKED***\2', text)
        masked = re.sub(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', 
                       r'\1=***MASKED***', masked, flags=re.IGNORECASE)
        return masked
    
    def should_scan_file(self, filepath: Path) -> bool:
        if any(excluded in filepath.parts for excluded in self.exclude_dirs):
            return False
        
        if filepath.name in self.exclude_files:
            return False
        
        if filepath.suffix in {'.pyc', '.pyo', '.pyd', '.so', '.dll'}:
            return False
        
        if filepath.name.startswith('.env'):
            return False
        
        return True
    
    def scan_file(self, filepath: Path) -> None:
        if not self.should_scan_file(filepath):
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for pattern, description in self.secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    line_content = lines[line_num - 1].strip()
                    if line_content.startswith('#'):
                        continue
                    
                    if 'example' in line_content.lower():
                        continue
                    
                    self.findings.append({
                        'severity': 'CRITICAL',
                        'type': description,
                        'file': str(filepath.relative_to(self.project_root)),
                        'line': line_num,
                        'preview': self._mask_secret(line_content[:80] if len(line_content) > 80 else line_content)
                    })
            
            for weak_value, description in self.weak_values:
                pattern = rf'["\'][^"\']*{re.escape(weak_value)}[^"\']*["\']'
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip()
                    
                    if line_content.startswith('#'):
                        continue
                    if 'example' in line_content.lower():
                        continue
                    if 'tests' in filepath.parts:
                        continue
                    
                    matched_text = match.group()
                    if len(matched_text) < 50 and weak_value in matched_text.lower():
                        self.findings.append({
                            'severity': 'HIGH',
                            'type': description,
                            'file': str(filepath.relative_to(self.project_root)),
                            'line': line_num,
                            'preview': self._mask_secret(line_content[:80])
                        })
        
        except UnicodeDecodeError:
            print(f"Warning: Could not decode {filepath}, skipping")
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
    
    def scan_project(self) -> None:
        all_files = []
        for ext in ('py', 'yaml', 'yml', 'json'):
            all_files.extend(self.project_root.glob(f'**/*.{ext}'))
        
        for filepath in set(all_files):
            self.scan_file(filepath)
    
    def generate_report(self) -> str:
        report = []
        report.append("=" * 80)
        report.append("SECRET SCANNING AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        critical = [f for f in self.findings if f['severity'] == 'CRITICAL']
        high = [f for f in self.findings if f['severity'] == 'HIGH']
        
        report.append(f"Total findings: {len(self.findings)}")
        report.append(f"  Critical: {len(critical)}")
        report.append(f"  High: {len(high)}")
        report.append("")
        
        if self.findings:
            report.append("-" * 80)
            report.append("FINDINGS")
            report.append("-" * 80)
            
            for finding in sorted(self.findings, key=lambda x: (x['severity'], x['file'])):
                report.append(f"\n[{finding['severity']}] {finding['type']}")
                report.append(f"  File: {finding['file']}:{finding['line']}")
                report.append(f"  Preview: {finding['preview']}")
        else:
            report.append("✓ No hardcoded secrets detected")
        
        report.append("\n" + "=" * 80)
        report.append("\nRECOMMENDATIONS:")
        report.append("- Use environment variables for all sensitive configuration")
        report.append("- Never commit .env files (add to .gitignore)")
        report.append("- Use strong, randomly generated secrets (min 32 characters)")
        report.append("- Rotate secrets regularly")
        report.append("- Use secret management tools (e.g., HashiCorp Vault, AWS Secrets Manager)")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    project_root = Path(__file__).parent.parent
    scanner = SecretScanner(str(project_root))
    
    print("Scanning codebase for hardcoded secrets and weak credentials...")
    scanner.scan_project()
    
    report = scanner.generate_report()
    print(report)
    
    report_path = project_root / "security_audit_secrets.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    
    if scanner.findings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
