import ast
import sys
from pathlib import Path
from typing import List, Dict


class EndpointScanner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.routes = []
        self.issues = []
        
    def scan_file(self, filepath: Path) -> None:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            
            self._analyze_ast(tree, filepath)
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
    
    def _analyze_ast(self, tree: ast.AST, filepath: Path) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_route_function(node, filepath)
    
    def _check_route_function(self, func_node: ast.FunctionDef, filepath: Path) -> None:
        decorator_names = []
        for decorator in func_node.decorator_list:
            node = decorator
            while isinstance(node, ast.Call):
                node = node.func
            
            if isinstance(node, ast.Name):
                decorator_names.append(node.id)
            elif isinstance(node, ast.Attribute):
                decorator_names.append(node.attr)

        if 'route' not in decorator_names:
            return
        
        auth_decorators = {'require_auth', 'require_admin_role', 'login_required', 'jwt_required'}
        has_auth = any(d in auth_decorators for d in decorator_names)
        
        route_info = {
            'function': func_node.name,
            'file': str(filepath.relative_to(self.project_root)),
            'line': func_node.lineno,
            'decorators': decorator_names,
            'has_auth': has_auth
        }
        
        self.routes.append(route_info)
        
        if not has_auth and not self._is_public_route(func_node.name):
            self.issues.append({
                'severity': 'HIGH',
                'type': 'Missing Authentication',
                'location': f"{route_info['file']}:{route_info['line']}",
                'function': func_node.name,
                'recommendation': 'Add authentication decorator (@require_auth or @require_admin_role)'
            })
    
    def _is_public_route(self, func_name: str) -> bool:
        public_prefixes = ['login', 'register', 'signup', 'signin', 'auth', 'request_otp', 'verify_otp', 'set_password', 'google']
        public_exact = {'health', 'index', 'landing', 'home', 'privacy', 'terms', 'about'}
        
        func_lower = func_name.lower()
        if func_lower in public_exact:
            return True
        if any(func_lower.startswith(prefix) for prefix in public_prefixes):
            return True
        return False
    
    def scan_project(self) -> None:
        python_files = list(self.project_root.glob('**/*.py'))
        exclude_dirs = {'venv', '__pycache__', 'tests', 'node_modules', '.git'}
        
        for filepath in python_files:
            if any(excluded in filepath.parts for excluded in exclude_dirs):
                continue
                
            self.scan_file(filepath)
    
    def generate_report(self) -> str:
        report = []
        report.append("=" * 80)
        report.append("ENDPOINT SECURITY AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        report.append(f"Total routes scanned: {len(self.routes)}")
        report.append(f"Routes with authentication: {sum(1 for r in self.routes if r['has_auth'])}")
        report.append(f"Routes without authentication: {sum(1 for r in self.routes if not r['has_auth'])}")
        report.append(f"Security issues found: {len(self.issues)}")
        report.append("")
        
        if self.issues:
            report.append("-" * 80)
            report.append("SECURITY ISSUES")
            report.append("-" * 80)
            
            for issue in self.issues:
                report.append(f"\n[{issue['severity']}] {issue['type']}")
                report.append(f"  Location: {issue['location']}")
                report.append(f"  Function: {issue['function']}")
                report.append(f"  Recommendation: {issue['recommendation']}")
        else:
            report.append("✓ No critical security issues detected")
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)


def main():
    project_root = Path(__file__).parent.parent
    scanner = EndpointScanner(str(project_root))
    
    print("Scanning Flask endpoints for security issues...")
    scanner.scan_project()
    
    report = scanner.generate_report()
    print(report)
    
    report_path = project_root / "security_audit_endpoints.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    
    if scanner.issues:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
