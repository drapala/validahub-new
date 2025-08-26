# Learning Document: Removing Pandas from Core Layer

## Context
During the architectural review of ValidaHub, we identified that the core domain layer had direct dependencies on infrastructure libraries (pandas, numpy), violating Clean Architecture principles.

## What Was Done Wrong Initially

### 1. Direct Framework Dependencies in Core
**Mistake**: The core layer directly imported and used pandas/numpy
```python
# WRONG: core/utils.py
import pandas as pd
import numpy as np

class DataFrameUtils:
    def parse_csv(self, csv_content: str) -> pd.DataFrame:
        return pd.read_csv(StringIO(csv_content))
```

**Why it's wrong**: 
- Core should be framework-agnostic
- Creates tight coupling to specific libraries
- Makes testing harder (need to mock pandas)
- Violates Dependency Inversion Principle

### 2. Missing Abstraction Layer
**Mistake**: No interface/port defined for tabular data operations
- Use cases directly knew about pandas DataFrames
- No way to swap implementations
- Business logic coupled to data structure implementation

### 3. Inadequate Dependency Injection
**Mistake**: Services created their own dependencies
```python
# WRONG: Direct instantiation
class ValidateCsvUseCase:
    def __init__(self):
        self.utils = DataFrameUtils()  # Creates own dependency
```

**Why it's wrong**:
- Cannot test in isolation
- Cannot swap implementations
- Violates IoC (Inversion of Control)

## How It Was Fixed

### 1. Created Port Interface
```python
# core/ports/tabular_data_port.py
from abc import ABC, abstractmethod

class TabularDataPort(ABC):
    @abstractmethod
    def parse_csv(self, csv_content: Union[str, StringIO]) -> Any:
        """Parse CSV content into tabular data"""
        pass
```

### 2. Moved Implementation to Infrastructure
```python
# infrastructure/adapters/pandas_adapter.py
import pandas as pd

class PandasAdapter(TabularDataPort):
    def parse_csv(self, csv_content: Union[str, StringIO]) -> pd.DataFrame:
        # Pandas-specific implementation
        return pd.read_csv(StringIO(csv_content))
```

### 3. Used Dependency Injection
```python
# core/use_cases/validate_csv.py
class ValidateCsvUseCase:
    def __init__(self, tabular_adapter: TabularDataPort):
        self.data_utils = DataFrameUtils(tabular_adapter)
```

## Key Learnings

### 1. **Always Define Ports First**
Before implementing any external dependency usage, define the port/interface that represents what the core needs, not how it's implemented.

### 2. **Core Should Only Know Abstractions**
The core domain should only import from:
- Its own modules
- Port interfaces
- Standard library
- Never from infrastructure/frameworks

### 3. **Dependency Direction Matters**
Dependencies should always point inward:
```
Infrastructure → Application → Domain
         ↓             ↓          ↑
    Implements    Uses Ports   Defines Ports
```

### 4. **Test the Port, Not the Implementation**
Write tests against the port interface to ensure any implementation will work correctly.

### 5. **Use Typing for Documentation**
The port interface serves as documentation of what operations the core needs:
```python
def parse_csv(self, csv_content: Union[str, StringIO]) -> Any
def clean_data(self, data: Any) -> Any
def to_dict_records(self, data: Any) -> List[Dict[str, Any]]
```

## Mistakes to Avoid in the Future

1. **Don't leak implementation details**: Return types should be generic (`Any`) or domain types, not framework types
2. **Don't create dependencies inside classes**: Always inject them
3. **Don't skip the abstraction**: Even for "simple" dependencies, create a port
4. **Don't mix concerns**: Keep data manipulation separate from business logic

## Benefits Achieved

1. **Testability**: Can test core logic with mock adapters
2. **Flexibility**: Can swap pandas for polars, duckdb, or any other implementation
3. **Maintainability**: Changes to pandas API don't affect core logic
4. **Clear boundaries**: Obvious what belongs in core vs infrastructure
5. **Documentation**: Port interface documents exact requirements

## Next Steps

1. Apply same pattern to other violations:
   - Database access (SQLAlchemy)
   - HTTP framework (FastAPI)
   - Cache (Redis)
   
2. Add architecture tests to prevent regression:
   - Import-linter rules
   - Pre-commit hooks
   - CI/CD gates

3. Consider using Result types for error handling instead of exceptions

## Conclusion

The key insight is that **the core domain should express what it needs, not how to get it**. By defining ports and using dependency injection, we achieve true independence from infrastructure concerns while maintaining clean, testable, and maintainable code.