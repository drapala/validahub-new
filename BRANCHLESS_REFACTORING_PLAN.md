# Branchless Programming Refactoring Plan

## Overview
This document outlines the strategy to refactor the ValidaHub codebase to minimize or eliminate if/else branches using various design patterns and functional programming techniques.

## Refactoring Strategies

### 1. **Strategy Pattern with Dictionaries**
Replace if/elif chains with dictionary lookups for behavior selection.

### 2. **Registry Pattern**
Use registries for dynamic type/class selection.

### 3. **Guard Clauses**
Use early returns to flatten nested conditions.

### 4. **Null Object Pattern**
Provide default behaviors instead of null checks.

### 5. **Polymorphism**
Use inheritance/protocols for type-specific behavior.

### 6. **Function Composition**
Chain operations instead of conditional execution.

## Priority 1: High-Impact Refactorings

### 1.1 Marketplace-Specific Logic
**Location**: `src/services/corrector_v2.py`
**Current Code**:
```python
if self.marketplace == Marketplace.MERCADO_LIVRE:
    corrections = {...}
elif self.marketplace == Marketplace.SHOPEE:
    corrections = {...}
elif self.marketplace == Marketplace.AMAZON:
    corrections = {...}
```

**Refactored Approach**:
```python
MARKETPLACE_CORRECTIONS = {
    Marketplace.MERCADO_LIVRE: {
        'title': [TruncateCorrection(60), DefaultValueCorrection("Produto sem título")],
        'price': [MinValueCorrection(0.01)],
    },
    Marketplace.SHOPEE: {
        'title': [TruncateCorrection(100), DefaultValueCorrection("Product Title")],
        'price': [MinValueCorrection(0.01)],
    },
    Marketplace.AMAZON: {
        'title': [TruncateCorrection(200), DefaultValueCorrection("Product")],
        'price': [MinValueCorrection(0.01)],
    }
}

def _load_corrections(self):
    return MARKETPLACE_CORRECTIONS.get(self.marketplace, {})
```

### 1.2 Category-Specific Rules
**Location**: `src/rules/marketplaces/shopee/provider.py`, `src/rules/marketplaces/amazon/provider.py`
**Current Code**:
```python
if category == 'ELETRONICOS':
    rules.extend([...])
elif category == 'MODA':
    rules.extend([...])
elif category == 'BELEZA':
    rules.extend([...])
```

**Refactored Approach**:
```python
CATEGORY_RULES = {
    'ELETRONICOS': [
        MaxLengthRule(column='title', max_length=100),
        MinValueRule(column='price', min_value=0.01),
    ],
    'MODA': [
        MaxLengthRule(column='title', max_length=120),
        RequiredRule(column='size'),
    ],
    'BELEZA': [
        MaxLengthRule(column='title', max_length=100),
        RequiredRule(column='ingredients'),
    ],
}

def get_category_rules(self, category: str) -> List[IRule]:
    return CATEGORY_RULES.get(category, [])
```

### 1.3 Error Type to Correction Mapping
**Location**: `src/services/corrector.py`
**Current Code**:
```python
if "too long" in error.error.lower():
    new_value = str(old_value)[:60]
elif "must be greater than 0" in error.error.lower():
    new_value = 0.01
elif "cannot be negative" in error.error.lower():
    new_value = abs(float(old_value))
```

**Refactored Approach**:
```python
ERROR_CORRECTION_STRATEGIES = {
    'too_long': lambda value, ctx: str(value)[:ctx.get('max_length', 60)],
    'must_be_positive': lambda value, ctx: max(0.01, float(value or 0)),
    'cannot_be_negative': lambda value, ctx: abs(float(value or 0)),
    'required_empty': lambda value, ctx: ctx.get('default', 'N/A'),
}

def get_correction_strategy(error_text: str) -> Optional[Callable]:
    error_key = classify_error(error_text)  # Maps error text to error_key
    return ERROR_CORRECTION_STRATEGIES.get(error_key)
```

## Priority 2: Validation Rules

### 2.1 Numeric Validation
**Location**: `src/rules/base/number_rules.py`
**Current Code**:
```python
if self.min_value is not None and num_value < self.min_value:
    return ValidationError(...)
if self.max_value is not None and num_value > self.max_value:
    return ValidationError(...)
```

**Refactored Approach**:
```python
NUMERIC_VALIDATORS = [
    (lambda v, min: v >= min if min else True, "Value too small"),
    (lambda v, max: v <= max if max else True, "Value too large"),
]

def validate(self, value):
    for validator, error_msg in NUMERIC_VALIDATORS:
        if not validator(value, self.constraints):
            return ValidationError(error_msg)
```

### 2.2 Text Validation
**Location**: `src/rules/base/text_rules.py`
**Current Code**:
```python
if value is None:
    return None
if length > self.max_length:
    return ValidationError(...)
```

**Refactored Approach**:
```python
def validate(self, value):
    validators = [
        NullValidator(),
        LengthValidator(self.max_length),
        PatternValidator(self.pattern),
    ]
    
    return next(
        (error for v in validators if (error := v.check(value))),
        None
    )
```

## Priority 3: File Type Validation

### 3.1 File Extension Check
**Location**: `src/api/validate.py`
**Current Code**:
```python
if not file.filename.endswith(('.csv', '.CSV')):
    raise HTTPException(...)
```

**Refactored Approach**:
```python
ALLOWED_EXTENSIONS = {'.csv', '.CSV'}
FILE_VALIDATORS = {
    'extension': lambda f: any(f.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS),
    'size': lambda f: f.size <= 10 * 1024 * 1024,
}

def validate_file(file):
    failed = [name for name, validator in FILE_VALIDATORS.items() if not validator(file)]
    if failed:
        raise ValidationException(failed)
```

## Priority 4: Guard Clauses Refactoring

### 4.1 Flatten Nested Conditions
**Location**: Multiple files
**Current Pattern**:
```python
if condition1:
    if condition2:
        do_something()
    else:
        do_other()
```

**Refactored Pattern**:
```python
if not condition1:
    return early_result()
if not condition2:
    return do_other()
return do_something()
```

## Implementation Plan

### Phase 1: Core Business Logic (Week 1)
- [ ] Refactor marketplace-specific corrections (corrector_v2.py)
- [ ] Refactor category-specific rules (provider files)
- [ ] Create error classification system

### Phase 2: Validation System (Week 2)
- [ ] Implement validator composition for numeric rules
- [ ] Implement validator composition for text rules
- [ ] Create validation pipeline with chain of responsibility

### Phase 3: Infrastructure (Week 3)
- [ ] Refactor file validation
- [ ] Apply guard clauses throughout codebase
- [ ] Implement Null Object pattern for optional providers

### Phase 4: Testing & Documentation (Week 4)
- [ ] Update unit tests for new patterns
- [ ] Create integration tests
- [ ] Document new patterns and conventions

## Benefits Expected

1. **Extensibility**: Adding new marketplaces/categories becomes configuration, not code
2. **Testability**: Each strategy/validator can be tested independently
3. **Readability**: Business rules become declarative configurations
4. **Maintainability**: Less cyclomatic complexity
5. **Performance**: Dictionary lookups are O(1) vs O(n) for if/elif chains

## Code Metrics to Track

- Cyclomatic complexity reduction (target: 50% reduction)
- Lines of code (expect 20-30% reduction)
- Test coverage (maintain or improve current levels)
- Number of if/else statements (target: 70% reduction)

## Migration Strategy

1. Start with new features using branchless patterns
2. Refactor high-churn code first
3. Leave stable, rarely-changed code for last
4. Maintain backward compatibility during migration

## Example: Complete Refactoring

### Before (45 lines, complexity: 8)
```python
def apply_correction(self, error, value):
    if error.type == "too_long":
        if error.column == "title":
            return value[:60]
        elif error.column == "description":
            return value[:500]
        else:
            return value[:100]
    elif error.type == "negative":
        if error.column == "price":
            return 0.01
        elif error.column == "stock":
            return 0
        else:
            return abs(value)
    elif error.type == "missing":
        if error.column == "sku":
            return f"SKU-{uuid.uuid4()}"
        else:
            return "N/A"
    return value
```

### After (20 lines, complexity: 1)
```python
CORRECTION_MATRIX = {
    ("too_long", "title"): lambda v: v[:60],
    ("too_long", "description"): lambda v: v[:500],
    ("too_long", None): lambda v: v[:100],
    ("negative", "price"): lambda v: 0.01,
    ("negative", "stock"): lambda v: 0,
    ("negative", None): lambda v: abs(v),
    ("missing", "sku"): lambda v: f"SKU-{uuid.uuid4()}",
    ("missing", None): lambda v: "N/A",
}

def apply_correction(self, error, value):
    key = (error.type, error.column)
    correction = CORRECTION_MATRIX.get(key) or CORRECTION_MATRIX.get((error.type, None))
    return correction(value) if correction else value
```

## Next Steps

1. Review and approve this plan
2. Create feature branch for Phase 1
3. Implement first refactoring as proof of concept
4. Measure improvements
5. Iterate based on results