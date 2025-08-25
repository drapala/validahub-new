#!/usr/bin/env python3
"""Fix remaining relative import issues in the codebase."""

import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix relative imports in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix patterns like ..core. -> core.
    content = re.sub(r'from \.\.(core|schemas|models|infrastructure|telemetry|db)\.', r'from \1.', content)
    # Fix patterns like from ..core -> from core
    content = re.sub(r'from \.\.(\w+)\s+import', r'from \1 import', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed imports in {filepath}")
        return True
    return False

def main():
    src_dir = Path('src')
    fixed_count = 0
    
    # Find all Python files
    for py_file in src_dir.rglob('*.py'):
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print(f"\nFixed imports in {fixed_count} files")

if __name__ == '__main__':
    main()