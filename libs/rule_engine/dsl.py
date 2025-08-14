import re
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


def check_exists(path: str, context: Dict[str, Any]) -> bool:
    """Check if a key exists in context or file exists on disk"""
    if '/' in path or '\\' in path:
        return Path(path).exists()
    return path in context


def check_regex(pattern: str, value: str, flags: int = 0) -> bool:
    """Check if value matches regex pattern"""
    try:
        return bool(re.search(pattern, str(value), flags))
    except re.error:
        return False


def check_json_path(path: str, context: Dict[str, Any], expected: Any = None) -> bool:
    """Check JSON path existence or value match"""
    parts = path.split('.')
    current = context
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return False
        else:
            return False
    
    if expected is not None:
        return current == expected
    return True


def check_range(value: Union[int, float], min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """Check if numeric value is within range"""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except (TypeError, ValueError):
        return False


def fix_replace(context: Dict[str, Any], path: str, new_value: Any) -> Dict[str, Any]:
    """Replace value at path in context (idempotent)"""
    result = context.copy()
    parts = path.split('.')
    
    if len(parts) == 1:
        result[path] = new_value
        return result
    
    current = result
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    current[parts[-1]] = new_value
    return result


def fix_insert(context: Dict[str, Any], path: str, value: Any, index: Optional[int] = None) -> Dict[str, Any]:
    """Insert value into list at path (idempotent - checks if already exists)"""
    result = context.copy()
    parts = path.split('.')
    
    current = result
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    list_key = parts[-1]
    if list_key not in current:
        current[list_key] = []
    
    target_list = current[list_key]
    if not isinstance(target_list, list):
        target_list = current[list_key] = []
    
    if value not in target_list:
        if index is not None:
            target_list.insert(index, value)
        else:
            target_list.append(value)
    
    return result


def fix_delete(context: Dict[str, Any], path: str) -> Dict[str, Any]:
    """Delete key at path (idempotent - safe if not exists)"""
    result = context.copy()
    parts = path.split('.')
    
    if len(parts) == 1:
        result.pop(path, None)
        return result
    
    current = result
    for part in parts[:-1]:
        if part not in current:
            return result
        current = current[part]
    
    current.pop(parts[-1], None)
    return result


def fix_append(context: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """Append value to string or list at path (idempotent)"""
    result = context.copy()
    parts = path.split('.')
    
    current = result
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    key = parts[-1]
    if key not in current:
        current[key] = value
    elif isinstance(current[key], str):
        if not current[key].endswith(str(value)):
            current[key] += str(value)
    elif isinstance(current[key], list):
        if value not in current[key]:
            current[key].append(value)
    
    return result