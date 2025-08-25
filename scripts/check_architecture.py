#!/usr/bin/env python3
"""
Architecture validation script for ValidaHub.
Ensures clean architecture principles are followed.
"""

import ast
import sys
from pathlib import Path
from typing import Set, List, Dict, Tuple

# Layer definitions
LAYERS = {
    "core": {
        "path": "apps/api/src/core",
        "allowed_imports": {
            "core",  # Can import from itself
            "schemas",  # Domain models
            "models",  # Domain entities
            "typing",
            "datetime",
            "decimal",
            "uuid",
            "enum",
            "abc",
            "dataclasses",
            "pydantic",
            "collections",
            "itertools",
            "functools",
            "re",
            "json",  # For serialization only
            "pathlib",
        },
        "forbidden_imports": {
            "infrastructure",
            "services",
            "db",
            "api",
            "workers",
            "middleware",
            "fastapi",
            "sqlalchemy",
            "pandas",
            "numpy",
            "aiohttp",
            "requests",
            "redis",
            "boto3",
            "celery",
            "uvicorn",
        }
    },
    "application": {
        "path": "apps/api/src/application",
        "allowed_imports": {
            "core",
            "application",
            "schemas",
            "models",
        },
        "forbidden_imports": {
            "infrastructure",
            "api",
            "db",
            "fastapi",
            "sqlalchemy",
        }
    },
    "infrastructure": {
        "path": "apps/api/src/infrastructure",
        "allowed_imports": {
            "core",
            "application",
            "infrastructure",
            "schemas",
            "models",
            "db",
            # External libs are OK here
            "sqlalchemy",
            "pandas",
            "numpy",
            "boto3",
            "redis",
            "aiohttp",
            "requests",
        },
        "forbidden_imports": {
            "api",  # Infra should not know about API
            "middleware",
            "workers",
        }
    },
    "interfaces": {
        "path": "apps/api/src/api",
        "allowed_imports": {
            # Interfaces can know everything except other interfaces
            "core",
            "application", 
            "infrastructure",
            "services",
            "schemas",
            "models",
            "db",
            "middleware",
            "fastapi",
        },
        "forbidden_imports": set()  # API layer can import from anywhere
    }
}


class ImportChecker(ast.NodeVisitor):
    """AST visitor to check imports."""
    
    def __init__(self, layer: str):
        self.layer = layer
        self.violations: List[Tuple[int, str, str]] = []
        self.layer_config = LAYERS.get(layer, {})
        
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self._check_import(node.lineno, alias.name)
            
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self._check_import(node.lineno, node.module)
            
    def _check_import(self, lineno: int, module: str):
        """Check if import is allowed."""
        if not self.layer_config:
            return
            
        # Get the root module
        root_module = module.split('.')[0]
        
        # Check forbidden imports
        if root_module in self.layer_config.get("forbidden_imports", set()):
            self.violations.append((
                lineno,
                module,
                f"Forbidden import '{module}' in {self.layer} layer"
            ))
            return
            
        # For core layer, be more strict
        if self.layer == "core":
            # Check if it's an internal project import
            if root_module in {"infrastructure", "services", "api", "db", "workers", "middleware", "adapters"}:
                self.violations.append((
                    lineno,
                    module,
                    f"Core layer cannot import from '{root_module}'"
                ))


def detect_layer(file_path: Path) -> str:
    """Detect which layer a file belongs to."""
    path_str = str(file_path)
    
    for layer, config in LAYERS.items():
        if config["path"] in path_str:
            return layer
    
    return "unknown"


def check_file(file_path: Path) -> List[str]:
    """Check a single file for architecture violations."""
    errors = []
    
    # Detect layer
    layer = detect_layer(file_path)
    if layer == "unknown":
        return errors
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        checker = ImportChecker(layer)
        checker.visit(tree)
        
        for lineno, module, message in checker.violations:
            errors.append(f"{file_path}:{lineno}: {message}")
            
    except Exception as e:
        errors.append(f"{file_path}: Error parsing file: {e}")
    
    return errors


def main():
    """Main entry point."""
    # Get files from command line or stdin
    files = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not files:
        # Read from stdin if no args
        for line in sys.stdin:
            line = line.strip()
            if line:
                files.append(line)
    
    all_errors = []
    for file_str in files:
        file_path = Path(file_str)
        if file_path.exists() and file_path.suffix == '.py':
            errors = check_file(file_path)
            all_errors.extend(errors)
    
    if all_errors:
        print("Architecture violations found:")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()