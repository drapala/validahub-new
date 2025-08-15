# Technical Debt

## Configuration Management

### 1. Centralize Configuration Values
**File:** `apps/api/src/api/v1/validation.py:50-51`

**Issue:** Configuration values like MAX_SYNC_FILE_SIZE and MAX_FILE_SIZE are defined directly in the module rather than centralized in a settings/config module.

**Current Code:**
```python
MAX_SYNC_FILE_SIZE = int(os.environ.get("MAX_SYNC_FILE_SIZE", 5 * 1024 * 1024))
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 50 * 1024 * 1024))
```

**Impact:** Low - The current approach works but makes configuration management less organized.

**Suggested Improvement:** Move these constants to `src/config.py` for centralized configuration management.

---

## Type System

### 2. Python Typing Compatibility
**File:** `apps/api/src/services/rule_engine_service.py`

**Issue:** Using `tuple[...]` syntax requires Python 3.9+. For better compatibility, should use `Tuple` from typing module.

**Current Code:**
```python
def validate_and_fix_row(...) -> tuple[Dict[str, Any], List[ValidationItem]]:
```

**Impact:** Low - CI/CD already uses Python 3.11, so this is not a current issue but could affect local development on older Python versions.

**Suggested Improvement:** Use `from typing import Tuple` and change to `Tuple[Dict[str, Any], List[ValidationItem]]`

---

## Code Quality Improvements

### 1. Rule Engine Mapping Logic Optimization
**File:** `libs/rule_engine/engine.py:161-164`

**Issue:** The `new_val` variable is modified but the row update happens later, creating a gap between value determination and application.

**Current Code:**
```python
if current_val in mapping_dict:
    row[field] = mapping_dict[current_val]
    new_val = mapping_dict[current_val]
```

**Impact:** Low - The current implementation works correctly, but the code structure could be cleaner and more maintainable.

**Suggested Improvement:** Refactor to update the row immediately after determining the new value, or consolidate the logic to avoid intermediate state.

---

### 2. Extract Field Name Logic Duplication
**File:** `apps/api/src/services/rule_engine_service.py:182-185`

**Issue:** Field extraction from rule results is duplicated and uses fragile string manipulation.

**Current Code:**
```python
field = result.metadata.get("field") if result.metadata else None
if not field and "_" in result.rule_id:
    # Try to extract field from rule_id (e.g., "sku_required" -> "sku")
    field = result.rule_id.rsplit("_", 1)[0]
```

**Impact:** Low - Code duplication but functional. Could lead to maintenance issues if field extraction logic needs to change.

**Suggested Improvement:** Create a helper method `_extract_field_from_result(result)` to centralize this logic.

---

### 3. Python Path Manipulation
**File:** `apps/api/src/services/rule_engine_service.py:12-14`

**Issue:** Runtime `sys.path` manipulation for imports should be avoided in favor of proper Python packaging.

**Current Code:**
```python
libs_path = Path(__file__).parent.parent.parent.parent.parent / "libs"
if str(libs_path) not in sys.path:
    sys.path.insert(0, str(libs_path))
```

**Impact:** Low - Works for current project structure but is not a best practice.

**Suggested Improvement:** 
- Use proper Python packaging with `setup.py` or `pyproject.toml`
- Alternatively, use `PYTHONPATH` environment variable
- Consider restructuring the project to avoid cross-directory imports

---

### 4. When Condition Evaluation for Falsy Values
**File:** `libs/rule_engine/engine.py:92-94`

**Issue:** Simple field existence check doesn't handle boolean `False` or `0` values correctly - these valid values would be treated as 'falsy' and skip rule execution.

**Current Code:**
```python
if '==' not in condition and '!=' not in condition:
    field = condition.strip()
    value = row.get(field)
    return value is not None and value != "" and value != []
```

**Impact:** Low - Current validation rules don't use boolean/zero values, so this isn't affecting current use cases.

**Suggested Improvement:**
```python
return field in row and value is not None and value != "" and value != []
```

Or better yet, explicitly check for the types of "empty" values that should fail the condition:
```python
return field in row and value not in [None, "", []]
```

---

## Priority Assessment

All items listed are **low priority** as they:
- Don't affect current functionality
- Don't pose security risks
- Don't impact performance significantly
- Are primarily code organization and maintainability improvements

These can be addressed during future refactoring cycles or when touching these specific areas of code for other features.