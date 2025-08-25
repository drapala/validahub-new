# Clean Architecture Roadmap - ValidaHub

> **Status**: Phase 1 in progress  
> **Updated**: 2025-08-25

## TL;DR

Transforming ValidaHub from coupled monolith to **Clean + DDD + Ports & Adapters** architecture through incremental, measurable phases with CI gates preventing regression.

---

## 🎯 Current Architecture Score: 2/5

### Problems Identified
- **Core → Infrastructure coupling** (use cases import concrete services)
- **Circular dependencies** (core ↔ services ↔ infrastructure)
- **Framework contamination** (pandas, SQLAlchemy in core)
- **God services** (RuleEngineServiceAdapter with 10+ responsibilities)
- **sys.path manipulation** (global state changes)

---

## 📋 Implementation Phases

### ✅ Phase 0: Entropy Quarantine (COMPLETED)
**Goal**: Stop the bleeding - prevent new violations

**Deliverables**:
- ✅ Pre-commit hooks blocking forbidden imports
- ✅ Architecture validation script (`scripts/check_architecture.py`)
- ✅ Import-linter configuration in `pyproject.toml`
- ✅ Coverage gates: 70% global, 80% core
- ✅ CI pipeline with architecture checks

**Files Created**:
- `.pre-commit-config.yaml` (enhanced)
- `scripts/check_architecture.py`
- `pyproject.toml` (import-linter config)
- `.github/workflows/ci.yml` (architecture gates)

---

### 🚧 Phase 1: Ports & Adapters (IN PROGRESS)
**Goal**: Invert dependencies through abstraction

**Deliverables**:
- ✅ Core ports created (`core/ports/`)
  - `ClockPort` - Time abstractions
  - `ValidationServicePort` - Validation contract
  - `RuleEnginePort` - Rule execution
  - `StoragePort` - File operations
  - `TabularReaderPort` - CSV/Excel reading
  - `PolicyLoaderPort` - Policy management
  - `QueuePort` - Async messaging
- ⏳ Refactor use cases to use ports
- ⏳ Implement adapters in infrastructure
- ⏳ Wire dependencies at application boundary

**Next Steps**:
1. Create infrastructure adapters implementing ports
2. Refactor `ValidateCsvUseCase` to use `ValidationServicePort`
3. Create factory/DI container for wiring

---

### 📅 Phase 2: Remove Frameworks from Core (Week 2)
**Goal**: Pure domain layer

**Tasks**:
- Move logging config to infrastructure
- Replace DataFrameUtils with TabularReaderPort
- Split validators.py into cohesive modules
- Remove sys.path manipulations

**Acceptance Criteria**:
- Zero pandas/SQLAlchemy imports in core
- Core tests run < 1s
- All validators in registry pattern

---

### 📅 Phase 3: MELI ACL Isolation (Week 3)
**Goal**: Protect domain from external changes

**Tasks**:
- Create `bounded_contexts/acl_meli/`
- MELI→Canonical mapper
- Contract tests with golden fixtures
- Policy versioning with schema validation

**Acceptance Criteria**:
- Core never imports MELI types
- Contract tests for all categories
- Policy update pipeline in CI

---

### 📅 Phase 4: Resilience Patterns (Week 4)
**Goal**: Production-ready error handling

**Tasks**:
- Retry/backoff in adapters only
- Circuit breaker at boundaries
- Time abstractions via ClockPort
- Correlation ID propagation

**Acceptance Criteria**:
- Chaos tests pass (429/5xx/timeout)
- Core remains pure (no retries/sleeps)
- Full request tracing

---

### 📅 Phase 5: Architecture Freeze (Week 5)
**Goal**: Prevent regression

**Tasks**:
- Import-linter enforced in CI
- Dependency graph generation
- Mutation testing for core
- Coverage gates: 85% core, 80% global

**Acceptance Criteria**:
- CI fails on layer violations
- Zero circular dependencies
- Core tests < 2s, full suite < 5min

---

### 📅 Phase 6: Documentation & Governance (Week 6)
**Goal**: Sustainable architecture

**Tasks**:
- ADR-007: Ports & Adapters
- ADR-008: Policy Lifecycle
- Developer Playbook
- Contribution templates

**Acceptance Criteria**:
- New dev productive in < 1 day
- All decisions documented
- Templates for common patterns

---

## 📊 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Architecture Score | 2/5 | 4/5 | 🔴 |
| Core Coverage | ~60% | 85% | 🟡 |
| Circular Dependencies | 3 | 0 | 🔴 |
| Core Test Speed | ~5s | <2s | 🟡 |
| Build Time | ~10min | <7min | 🟢 |
| Core Fan-out | 6 | <3 | 🔴 |

---

## 🛡️ Guardrails

### CI Gates (Enforced)
```yaml
- Pre-commit hooks (blocking)
- Import-linter contracts
- Coverage thresholds
- Architecture validation
- Mutation testing (sample)
```

### Review Requirements
- Architecture changes: 2 reviewers
- Core changes: 1 domain + 1 architecture reviewer
- New adapters: Must include contract tests

---

## 🚀 Quick Start for Developers

### Check Architecture Locally
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run architecture checks
python scripts/check_architecture.py apps/api/src/core/**/*.py

# Check import contracts
pip install import-linter
lint-imports --config pyproject.toml

# Run with coverage gates
pytest --cov=apps/api/src/core --cov-fail-under=80
```

### Creating New Components

#### New Port
```python
# apps/api/src/core/ports/my_port.py
from abc import ABC, abstractmethod

class MyPort(ABC):
    @abstractmethod
    async def do_something(self, data: dict) -> dict:
        pass
```

#### New Adapter
```python
# apps/api/src/infrastructure/adapters/my_adapter.py
from core.ports import MyPort

class MyAdapter(MyPort):
    async def do_something(self, data: dict) -> dict:
        # Implementation here
        return processed_data
```

#### Wiring in API
```python
# apps/api/src/api/dependencies.py
from infrastructure.adapters import MyAdapter

def get_my_port() -> MyPort:
    return MyAdapter()
```

---

## 📚 References

- [Clean Architecture - Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [DDD - Eric Evans](https://domainlanguage.com/ddd/)
- [Architecture Report](../ARCHITECTURE_REPORT.md)
- [Refactoring Checklist](REFACTORING_CHECKLIST.md)
- [Hardening Checklist](HARDENING_CHECKLIST.md)

---

**Next Review**: After Phase 1 completion (estimated 2025-08-30)