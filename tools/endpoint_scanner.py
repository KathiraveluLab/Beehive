import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Set


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
        decorators = [d.attr if isinstance(d, ast.Attribute) else 
                     d.id if isinstance(d, ast.Name) else None 
                     for d in func_node.decorator_list]
        
        route_decorator = None
        for dec in func_node.decorator_list:
            if isinstance(dec, ast.Attribute) and dec.attr == 'route':
                route_decorator = dec
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if dec.func.attr == 'route':
                    route_decorator = dec
        
        if not route_decorator:
            return
        
        has_auth = any(d in ['login_required', 'jwt_required', 'admin_required'] 
                      for d in decorators if d)
        
        route_info = {
            'function': func_node.name,
            'file': str(filepath.relative_to(self.project_root)),
            'line': func_node.lineno,
            'decorators': [d for d in decorators if d],
            'has_auth': has_auth
        }
        
        self.routes.append(route_info)
        
        if not has_auth and not self._is_public_route(func_node.name):
            self.issues.append({
                'severity': 'HIGH',
                'type': 'Missing Authentication',
                'location': f"{route_info['file']}:{route_info['line']}",
                'function': func_node.name,
                'recommendation': 'Add authentication decorator (@login_required or @jwt_required)'
            })
    
    def _is_public_route(self, func_name: str) -> bool:
        public_routes = {
            'login', 'register', 'signup', 'signin', 
            'health', 'index', 'landing', 'home',
            'privacy', 'terms', 'about'
        }
        return any(p in func_name.lower() for p in public_routes)
    
    def scan_project(self) -> None:
        python_files = list(self.project_root.glob('**/*.py'))
        
        for filepath in python_files:
            if 'venv' in str(filepath) or '__pycache__' in str(filepath):
                continue
            if 'tests' in str(filepath):
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
