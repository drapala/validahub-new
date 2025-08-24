# ValidaHub Testing Policy

## 📋 Table of Contents
1. [Overview](#overview)
2. [Testing Philosophy](#testing-philosophy)
3. [Testing Pyramid](#testing-pyramid)
4. [Coverage Requirements](#coverage-requirements)
5. [Testing Types](#testing-types)
6. [Implementation Guidelines](#implementation-guidelines)
7. [CI/CD Integration](#cicd-integration)
8. [Tools and Frameworks](#tools-and-frameworks)

## Overview

This document defines ValidaHub's comprehensive testing strategy to ensure code quality, reliability, and maintainability across all services.

### Core Principles
- **Test Early, Test Often**: Write tests alongside code, not after
- **Pragmatic Coverage**: Focus on critical paths and business logic
- **Fast Feedback**: Prioritize fast-running tests in development workflow
- **Living Documentation**: Tests serve as executable documentation

## Testing Philosophy

### What We Test
✅ **Always Test**:
- Business logic and core algorithms
- API endpoints and contracts
- Data validation and transformation
- Error handling and edge cases
- Security boundaries
- Critical user journeys

### What We Don't Test
❌ **Skip Testing**:
- Third-party libraries (trust their tests)
- Simple getters/setters
- Framework boilerplate
- Configuration files (unless complex logic)
- UI styling/CSS

## Testing Pyramid

```
         /\
        /  \  E2E Tests (5%)
       /____\ - Critical user journeys
      /      \ Integration Tests (25%)
     /________\ - API, Database, External services
    /          \ Unit Tests (70%)
   /____________\ - Business logic, Utilities, Validators
```

## Coverage Requirements

### Smart Coverage Strategy
Focamos em cobertura **por diff** e **por diretório crítico** para evitar "gaming" de cobertura global.

#### Coverage por Diff (Blocking PR)
- **Files Changed**: 85% minimum coverage on modified lines
- **New Files**: 90% minimum coverage
- **Critical Paths**: 95% coverage for files touching validation, payment, authentication

#### Coverage por Directory (Blocking PR)
| Directory | Coverage Required | Enforcement |
|-----------|------------------|-------------|
| `src/services/` | 90% | Blocking PR |
| `src/domain/` | 90% | Blocking PR |
| `src/api/` | 85% | Blocking PR |
| `src/validators/` | 95% | Blocking PR |
| Frontend critical pages* | 85% | Blocking PR |
| Other components | 70% | Warning |

*Critical pages: upload, validation results, payment/checkout, onboarding

#### Overall Project Targets
- **Total Coverage**: 80% (Blocking Deploy)
- **Diff Coverage**: 85% (Blocking PR)  
- **Mutation Score**: 80% for critical paths (Nightly check)

### Coverage Exceptions
Exceptions require explicit documentation with expiration:
```python
# pragma: no cover 
# Reason: External API mock for development only
# Issue: #123 - Remove after Q1 2025
# Expires: 2025-03-31
```

### Anti-Gaming Measures
- ✅ Use **diff-cover** tool for PR checks
- ✅ **Mutation testing** on critical paths (catches false positives)
- ✅ Manual review for files with >90% coverage but low complexity
- ❌ Block trivial getters/setters from inflating coverage

## Testing Types

### 1. Unit Tests
**Purpose**: Test individual functions/methods in isolation

**Characteristics**:
- Fast execution (< 100ms per test)
- No external dependencies
- Use mocks/stubs for dependencies
- Run on every file save (watch mode)
- **Deterministic data**: Fixed seeds, frozen time, predictable factories

**Example Structure**:
```python
# apps/api/tests/unit/test_validation_service.py
import pytest
from unittest.mock import Mock, patch
from src.services.validation_service import ValidationService

class TestValidationService:
    def test_validate_csv_row_valid_data(self):
        # Given
        service = ValidationService()
        row = {"product_id": "123", "price": 99.99}
        
        # When
        result = service.validate_row(row)
        
        # Then
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_csv_row_invalid_price(self):
        # Given
        service = ValidationService()
        row = {"product_id": "123", "price": -10}
        
        # When
        result = service.validate_row(row)
        
        # Then
        assert result.is_valid is False
        assert "price" in result.errors[0].field
```

### 2. Integration Tests
**Purpose**: Test interactions between components

**Characteristics**:
- Test API endpoints with real database
- Verify external service integrations
- Use test database/containers
- Run in CI pipeline

**Example Structure**:
```python
# apps/api/tests/integration/test_validation_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    # Setup test database
    yield db
    # Cleanup

class TestValidationAPI:
    def test_validate_csv_endpoint(self, client, test_db):
        # Given
        csv_file = {"file": ("test.csv", b"product_id,price\n123,99.99")}
        
        # When
        response = client.post(
            "/api/v1/validate",
            files=csv_file,
            data={"marketplace": "mercado_livre"}
        )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["total_rows"] == 1
```

### 3. E2E Tests
**Purpose**: Test complete user workflows

**Characteristics**:
- Test critical user journeys
- Run against staging environment
- Use real browser automation
- Run before production deploy

**Example Structure**:
```typescript
// apps/web/tests/e2e/upload-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('CSV Upload Flow', () => {
  test('should upload and validate CSV successfully', async ({ page }) => {
    // Given
    await page.goto('/upload');
    
    // When
    await page.setInputFiles('input[type="file"]', 'fixtures/valid.csv');
    await page.selectOption('#marketplace', 'mercado_livre');
    await page.click('button[type="submit"]');
    
    // Then
    await expect(page.locator('.validation-results')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Validation completed');
  });
});
```

### 4. Performance Tests
**Purpose**: Ensure system meets performance requirements

**Characteristics**:
- Test response times under load
- Memory usage monitoring
- Database query optimization
- Run weekly in CI

**Example**:
```python
# apps/api/tests/performance/test_bulk_validation.py
import pytest
from locust import HttpUser, task, between

class ValidationUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def validate_large_csv(self):
        with open('fixtures/large_file.csv', 'rb') as f:
            self.client.post(
                "/api/v1/validate",
                files={"file": f},
                data={"marketplace": "mercado_livre"}
            )

# Run: locust -f test_bulk_validation.py --users 100 --spawn-rate 10
```

### 5. Contract Tests
**Purpose**: Ensure API contracts between services are maintained

**Characteristics**:
- OpenAPI schema validation (requests/responses)
- Consumer-driven contracts (Pact) between web ↔ api
- External service contracts (marketplace APIs)
- Run on API changes and deployment

**Example**:
```python
# apps/api/tests/contract/test_validation_api_contract.py
import pytest
from openapi_spec_validator import validate_spec
from src.main import app

def test_openapi_schema_is_valid():
    """Ensure OpenAPI schema is valid and up-to-date."""
    schema = app.openapi()
    validate_spec(schema)  # Raises if invalid
    
def test_validation_endpoint_matches_contract(client):
    """Test that actual API matches OpenAPI contract."""
    # Test request validation
    response = client.post(
        "/api/v1/validate",
        files={"file": ("test.csv", b"data")},
        data={"marketplace": "mercado_livre"}
    )
    
    # Response should match OpenAPI schema
    assert response.status_code in [200, 400, 422]
    data = response.json()
    
    if response.status_code == 200:
        # Validate response structure matches schema
        assert "status" in data
        assert "total_rows" in data
        assert isinstance(data["total_rows"], int)
```

### 6. Security Tests
**Purpose**: Identify security vulnerabilities

**Characteristics**:
- SAST: Static analysis (Bandit, Semgrep, Ruff)
- DAST: Dynamic testing against staging (OWASP ZAP)
- Dependency scanning (pip-audit, npm audit)
- SBOM generation and license compliance

**Example**:
```python
# apps/api/tests/security/test_sql_injection.py
import pytest
from src.repositories.user_repository import UserRepository

class TestSQLInjection:
    @pytest.mark.parametrize("malicious_input", [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "<script>alert('XSS')</script>"
    ])
    def test_sql_injection_prevention(self, malicious_input):
        repo = UserRepository()
        
        # Should handle malicious input safely
        result = repo.find_by_email(malicious_input)
        assert result is None  # No user found, no SQL executed
```

## Anti-Flakiness Policy

### Flaky Test Management
Flaky tests são o inimigo #1 da produtividade. Nossa estratégia:

#### Detection & Quarantine
1. **Auto-detection**: CI detecta flakiness automático (3+ falhas intermitentes em 7 dias)
2. **Manual marking**: Devs podem marcar `@pytest.mark.flaky` com motivo
3. **Quarantine**: Testes flaky rodam em job separado (não bloqueia PR)
4. **Auto-issue**: Issue automática criada com SLA de 7 dias para fix

#### SLA & Metrics
- **Target**: < 0.5% flaky rate para E2E, < 0.1% para unit
- **Alert**: Slack notification quando rate > threshold
- **Cleanup**: Auto-disable de testes flaky > 30 days sem fix

#### Prevention Strategies
```python
# ✅ Deterministic data
@pytest.fixture
def fixed_time():
    with freezegun.freeze_time("2024-08-24 12:00:00"):
        yield

@pytest.fixture  
def seeded_faker():
    fake = Faker()
    fake.seed_instance(12345)  # Fixed seed
    return fake

# ✅ Proper waits
await expect(page.locator(".results")).to_be_visible(timeout=10000)

# ❌ Sleep-based waits  
time.sleep(2)  # Never use this

# ✅ Database isolation
@pytest.fixture
def isolated_db():
    transaction = db.begin()
    yield db
    transaction.rollback()

# ✅ Idempotent operations
def test_idempotent_validation():
    # Should work same way multiple times
    result1 = service.validate(data)
    result2 = service.validate(data)
    assert result1 == result2
```

## Implementation Guidelines

### Test Naming Convention
```python
def test_<unit_under_test>_<scenario>_<expected_result>():
    # Example:
    def test_validate_csv_row_missing_required_field_returns_error():
        pass
```

### Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange (Given)
    service = MyService()
    input_data = {"key": "value"}
    
    # Act (When)
    result = service.process(input_data)
    
    # Assert (Then)
    assert result.status == "success"
```

### Test Data Management

#### Fixtures
```python
# apps/api/tests/conftest.py
import pytest
from typing import Generator

@pytest.fixture
def valid_csv_data() -> dict:
    return {
        "marketplace": "mercado_livre",
        "category": "electronics",
        "rows": [
            {"product_id": "123", "price": 99.99},
            {"product_id": "456", "price": 149.99}
        ]
    }

@pytest.fixture
def mock_s3_client():
    with patch('boto3.client') as mock:
        yield mock
```

#### Factories
```python
# apps/api/tests/factories/job_factory.py
import factory
from src.models import Job

class JobFactory(factory.Factory):
    class Meta:
        model = Job
    
    id = factory.Sequence(lambda n: f"job_{n}")
    status = "pending"
    marketplace = "mercado_livre"
    total_rows = factory.Faker('random_int', min=1, max=1000)
```

### Mocking Strategy

#### When to Mock
- External APIs
- Database in unit tests
- File system operations
- Time-dependent operations

#### Example Mock Usage
```python
@patch('src.services.email_service.send_email')
def test_notification_on_validation_complete(mock_send_email):
    # Given
    service = ValidationService()
    
    # When
    service.complete_validation(job_id="123")
    
    # Then
    mock_send_email.assert_called_once_with(
        to="user@example.com",
        subject="Validation Complete"
    )
```

## Advanced CI/CD Integration

### Smart Pipeline Strategy
- **Ephemeral Environments**: Preview env por PR (Vercel + Neon DB branch)
- **Matrix Testing**: Python 3.10-3.12, Node LTS + LTS-1  
- **Selective Re-runs**: Só jobs afetados pelo diff
- **Parallel Execution**: Unit, integration, contract, security em paralelo
- **Rich Artifacts**: HTML coverage, Playwright traces, mutation reports

### Performance Testing Tiers
1. **Smoke por PR**: 1-2 cenários críticos (p95 < 300ms)
2. **Nightly Load**: Cenários completos com baseline histórico
3. **Alerts**: Falhar se p95/p99 degradar >15% vs média dos últimos 7 dias

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd apps/api
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run Unit Tests
        run: |
          cd apps/api
          pytest tests/unit -v --cov=src --cov-report=xml
      
      - name: Run Integration Tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379
        run: |
          cd apps/api
          pytest tests/integration -v
      
      - name: Check Coverage
        run: |
          cd apps/api
          coverage report --fail-under=80
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./apps/api/coverage.xml
          fail_ci_if_error: true

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install pnpm
        run: npm install -g pnpm
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Run Unit Tests
        run: |
          cd apps/web
          pnpm test:unit --coverage
      
      - name: Run Component Tests
        run: |
          cd apps/web
          pnpm test:components
      
      - name: Type Check
        run: |
          cd apps/web
          pnpm typecheck

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Run E2E Tests
        run: |
          cd apps/web
          pnpm test:e2e
      
      - name: Upload Playwright Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: apps/web/playwright-report/
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: backend-tests
        name: Backend Unit Tests
        entry: bash -c 'cd apps/api && pytest tests/unit -x'
        language: system
        files: ^apps/api/.*\.py$
        
      - id: frontend-tests
        name: Frontend Tests
        entry: bash -c 'cd apps/web && pnpm test:unit --run'
        language: system
        files: ^apps/web/.*\.(ts|tsx)$
        
      - id: type-check
        name: TypeScript Type Check
        entry: bash -c 'cd apps/web && pnpm typecheck'
        language: system
        files: ^apps/web/.*\.(ts|tsx)$
```

## Tools and Frameworks

### Backend (Python)
- **pytest**: Main testing framework + **pytest-xdist** (parallel)
- **pytest-cov**: Coverage + **diff-cover** (diff coverage)
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking utilities  
- **freezegun**: Time mocking for deterministic tests
- **factory-boy**: Test data factories + **faker** with fixed seeds
- **hypothesis**: Property-based testing (fuzz testing)
- **mutmut**: Mutation testing (catch false positives)
- **testcontainers**: Isolated test environments
- **locust**: Performance testing
- **bandit** + **semgrep** + **ruff**: Security + quality analysis
- **pact-python**: Consumer-driven contract testing

### Frontend (TypeScript)
- **Vitest**: Unit testing + **@vitest/coverage-v8**
- **Testing Library**: Component testing + **@testing-library/jest-dom**
- **Playwright**: E2E testing + **@axe-core/playwright** (a11y)
- **MSW**: API mocking + **OpenAPI contract validation**
- **Faker.js**: Test data generation (fixed seeds)
- **Stryker**: Mutation testing for TypeScript
- **Chromatic**: Visual regression (if using Storybook)

### Infrastructure
- **Docker**: Test containers
- **GitHub Actions**: CI/CD
- **Codecov**: Coverage tracking
- **SonarQube**: Code quality
- **Sentry**: Error monitoring

## Test Commands

### Backend
```bash
# Run all tests
cd apps/api
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_validation.py

# Run tests matching pattern
pytest -k "test_validate"

# Run with verbose output
pytest -v

# Run in watch mode
pytest-watch

# Run security tests
bandit -r src/

# Run performance tests
locust -f tests/performance/test_load.py
```

### Frontend
```bash
# Run all tests
cd apps/web
pnpm test

# Run unit tests
pnpm test:unit

# Run in watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage

# Run E2E tests
pnpm test:e2e

# Run E2E in UI mode
pnpm test:e2e:ui

# Type checking
pnpm typecheck
```

## Operational Metrics & SLAs

### Pipeline Health Metrics
1. **Lead Time**: PR aberta → verde = **< 10 min** (target)
2. **MTTR**: Falha de pipeline → fix = **< 1 hour** (SLA)
3. **Change Failure Rate**: % de deploys que quebram prod (**< 5%** target)
4. **Diff Coverage**: Changed lines coverage (**>= 85%** blocking)
5. **Test Execution Time**: Total pipeline **< 15 min**, PR checks **< 8 min**

### Quality Metrics
1. **Flaky Rate**: E2E **< 0.5%**, Unit **< 0.1%** (auto-alert)
2. **Mutation Score**: Critical paths **>= 80%** (nightly check)
3. **Security Findings**: Critical/High **= 0** (blocking), Medium **< 5** (warning)
4. **Performance Regression**: P95 degradation **< 15%** vs 7-day baseline
5. **Contract Drift**: API schema changes sem atualizar contratos (**= 0** blocking)

### Business Impact Metrics
1. **Critical Path Coverage**: Upload, validation, payment flows **>= 95%**
2. **Accessibility Score**: Core journeys **>= 95%** (axe-core)
3. **Cross-browser Coverage**: Chrome, Firefox, Safari (latest 2 versions)
4. **Mobile Coverage**: iOS Safari, Android Chrome (responsive + PWA)
5. **Internationalization**: Test com dados BR, US, EU (formatos, moeda, data)

### Reporting Dashboard
Create a test metrics dashboard showing:
- Coverage trends
- Test execution times
- Flaky test tracking
- Performance regression alerts

## Best Practices

### DO ✅
- **Write tests first** (TDD when possible, especially for complex logic)
- **Test integrations**, not third-party libraries themselves
- **Use deterministic data** (fixed seeds, frozen time, predictable factories)
- **Test behavior and contracts**, not implementation details
- **Mark flaky tests** immediately with `@pytest.mark.flaky` + reason
- **Review test code** as carefully as production code
- **Use quarantine** for flaky tests (separate job, auto-issue)
- **Test error conditions** and edge cases extensively
- **Validate logs/metrics** during integration tests
- **Check accessibility** in E2E for critical flows
- **Test with realistic data** (BR formats, large files, special chars)

### DON'T ❌
- **Game coverage** with trivial tests or empty assertions
- **Use `time.sleep()`** - always use proper waits/conditions
- **Test external APIs** directly without contracts/mocks
- **Ignore flaky tests** - quarantine and fix within SLA
- **Skip mutation testing** on critical business logic  
- **Use production data** in tests (LGPD compliance)
- **Test private methods** directly - test through public interface
- **Leave failing tests** commented out - delete or fix
- **Mix test types** - keep unit/integration/e2e separated
- **Hardcode credentials** - use fixtures and env vars

## Migration Strategy

### Phase 1: Foundation (Week 1-2)
- [ ] Set up testing frameworks
- [ ] Configure CI/CD pipeline
- [ ] Create example tests for each type
- [ ] Document testing standards

### Phase 2: Critical Path (Week 3-4)
- [ ] Add tests for all API endpoints
- [ ] Test core validation logic
- [ ] Add integration tests for database operations
- [ ] Implement E2E tests for main user flows

### Phase 3: Expansion (Week 5-6)
- [ ] Increase coverage to 80%
- [ ] Add performance tests
- [ ] Implement security tests
- [ ] Set up monitoring dashboard

### Phase 4: Optimization (Ongoing)
- [ ] Optimize test execution time
- [ ] Reduce test flakiness
- [ ] Improve test data management
- [ ] Enhance coverage reporting

## Review Checklist

Before merging any PR, ensure:
- [ ] All tests pass
- [ ] Coverage meets minimum requirements
- [ ] New features have corresponding tests
- [ ] No tests are skipped without justification
- [ ] Performance tests pass for critical paths
- [ ] Security tests pass for new endpoints
- [ ] Documentation is updated if needed

## Support and Resources

### Internal Resources
- Test examples: `/tests/examples/`
- Test utilities: `/tests/utils/`
- Fixtures: `/tests/fixtures/`

### External Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Martin Fowler - Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

## Questions?

For questions or suggestions about this testing policy:
- Create an issue in GitHub
- Discuss in #testing Slack channel
- Contact: qa@validahub.com

---

*Last Updated: August 2024*
*Version: 1.0.0*