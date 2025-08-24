#!/usr/bin/env python3
"""
Script to update all Python files to use centralized logging.
This will replace logging.getLogger(__name__) with get_logger(__name__).
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped."""
    skip_patterns = [
        'venv', 'venv_new', '__pycache__', '.git', 
        'node_modules', 'migrations', 'logging_config.py',
        'update_logging.py'
    ]
    
    for pattern in skip_patterns:
        if pattern in str(file_path):
            return True
    return False


def update_logging_imports(content: str, file_path: Path) -> Tuple[str, bool]:
    """Update logging imports to use centralized logging."""
    changed = False
    lines = content.split('\n')
    new_lines = []
    
    # Track if we've already added the import
    has_get_logger_import = False
    has_logging_import = False
    import_section_end = 0
    
    for i, line in enumerate(lines):
        # Check for existing imports
        if 'from src.core.logging_config import' in line or \
           'from ..core.logging_config import' in line or \
           'from ...core.logging_config import' in line:
            has_get_logger_import = True
        
        if line.strip().startswith('import logging'):
            has_logging_import = True
            import_section_end = i
        
        # Track end of import section
        if line.strip() and not line.strip().startswith('#') and \
           not line.strip().startswith('import') and \
           not line.strip().startswith('from'):
            if import_section_end == 0 and i > 0:
                import_section_end = i - 1
    
    # Process lines
    for i, line in enumerate(lines):
        # Replace logger = logging.getLogger(__name__)
        if 'logging.getLogger(__name__)' in line:
            # Add import if not present
            if not has_get_logger_import:
                # Determine the correct relative import path
                import_line = get_import_line(file_path)
                new_lines.insert(import_section_end + 1, import_line)
                has_get_logger_import = True
                changed = True
            
            # Replace the logger line
            new_line = line.replace('logging.getLogger(__name__)', 'get_logger(__name__)')
            new_lines.append(new_line)
            changed = True
        else:
            new_lines.append(line)
    
    # Remove standalone import logging if no longer needed
    final_lines = []
    for line in new_lines:
        if line.strip() == 'import logging' and has_get_logger_import:
            # Check if logging is still used elsewhere
            remaining_content = '\n'.join(new_lines)
            if not needs_logging_module(remaining_content):
                changed = True
                continue  # Skip this line
        final_lines.append(line)
    
    return '\n'.join(final_lines), changed


def get_import_line(file_path: Path) -> str:
    """Get the correct import line based on file location."""
    # Convert to string path relative to src
    path_str = str(file_path)
    
    # Count directory levels from src
    if '/src/' in path_str:
        after_src = path_str.split('/src/')[1]
        depth = after_src.count('/') - 1  # -1 for the file itself
        
        if depth == 0:  # Direct child of src
            return "from core.logging_config import get_logger"
        elif depth == 1:  # One level deep
            return "from ..core.logging_config import get_logger"
        elif depth == 2:  # Two levels deep
            return "from ...core.logging_config import get_logger"
        else:  # Three or more levels deep
            return "from ....core.logging_config import get_logger"
    
    return "from src.core.logging_config import get_logger"


def needs_logging_module(content: str) -> bool:
    """Check if logging module is still needed."""
    # Check for other logging usage
    patterns = [
        r'logging\.',  # Any logging.something
        r'logging\.basicConfig',
        r'logging\.DEBUG',
        r'logging\.INFO',
        r'logging\.WARNING',
        r'logging\.ERROR',
        r'logging\.CRITICAL',
    ]
    
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    
    return False


def process_file(file_path: Path) -> bool:
    """Process a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if no logging usage
        if 'logging.getLogger' not in content:
            return False
        
        # Update the content
        new_content, changed = update_logging_imports(content, file_path)
        
        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {file_path}")
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all Python files."""
    src_dir = Path('/Users/drapala/vibe/validahub-new/apps/api/src')
    
    if not src_dir.exists():
        print(f"Source directory not found: {src_dir}")
        return
    
    # Find all Python files
    python_files = list(src_dir.rglob('*.py'))
    
    # Filter out files to skip
    files_to_process = [f for f in python_files if not should_skip_file(f)]
    
    print(f"Found {len(files_to_process)} Python files to process")
    
    # Process each file
    updated_count = 0
    for file_path in files_to_process:
        if process_file(file_path):
            updated_count += 1
    
    print(f"\nCompleted! Updated {updated_count} files")


if __name__ == '__main__':
    main()