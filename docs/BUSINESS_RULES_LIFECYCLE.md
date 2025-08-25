# Business Rules Lifecycle and Update Policy

## Purpose

ValidaHub integrates with external marketplaces (Mercado Livre, Amazon, Magalu, etc.). Each marketplace evolves its validation rules over time (attributes, required fields, pricing limits, etc.).
This document defines how we maintain business rules up to date, versioned, and safely deployed without breaking customer workflows.

---

## Principles

* **Policy as Data**: Rules are never hard-coded. They are defined in YAML/JSON files under `/policies/{site}/{category}.yml`.
* **Single Source of Truth**: Official marketplace APIs (categories, attributes, listing validator, user quotas) are the only authoritative sources.
* **Safe Rollout**: New policies are introduced with canary testing and can be rolled back.
* **Auditability**: All changes are versioned, with changelog and links to original docs or validator responses.
* **Pass-through Safety Net**: Whenever a rule is ambiguous or missing, we always include the marketplace validator output directly in the user report.

---

## Update Workflow

### 1. Harvest

A scheduled job runs nightly/weekly to:

* Fetch `/categories/{id}` and `/categories/{id}/attributes` for supported categories.
* Run synthetic payloads against the marketplace **listing validator**.
* Generate **snapshots** (JSON) containing rules, limits, enums, error codes, and timestamps.

### 2. Diff & PR

The harvester compares the new snapshot with the previous one and:

* Detects semantic changes (e.g. new required attribute, max_title_length updated, enum value removed).
* Opens an automated Pull Request updating the corresponding policy files in `/policies`.
* PR includes:
  * Diff summary (old vs new values).
  * Links to official docs/endpoints.
  * Sample validator responses.

### 3. Contract Tests

Each PR triggers contract tests:

* **Schema validation**: policy YAML matches schema, values coherent (`min ≤ max`).
* **Table-driven tests**: fixtures ensure rules in the YAML match actual validator behavior.

### 4. Canary Release

On merge:

* New policy version is **flagged off by default**.
* Canary rollout runs the new version on a small % of jobs (e.g. 10%).
* Metrics tracked:
  * Error rate change vs previous version.
  * Unknown error codes surfaced.

If stable after 24–48h, the new policy becomes default.

### 5. Versioning & Rollback

* Every policy has `policy_version`, `effective_date`, and `deprecated_after`.
* API supports `?policy_version=…` for reproducibility.
* Rollback = flipping the feature flag to previous version.

### 6. Monitoring

* Dashboards track:
  * `error_rate` per category and version.
  * `top_error_codes`.
  * `unknown_validator_codes`.
* Alerts trigger when:
  * Spike of unknown codes > X in 1h.
  * Error rate jumps > Y% after rollout.

---

## File Structure

```
/policies
  /MLB
    meta.yml
    categories/
      MLB1743.yml     # Celulares e Smartphones
      MLB1055.yml     # Eletrônicos
  /AMZN_BR
    meta.yml
    categories/
      electronics.yml
      cell_phones.yml
  /MGLU
    ...
/snapshots
  /MLB/2025-08-24/
    category-MLB1743.json
    attributes-MLB1743.json
    validator-response-MLB1743.json
  /MLB/2025-08-25/
    ...
```

---

## Policy Schema Example

```yaml
# /policies/MLB/categories/MLB1743.yml
version: "2025.08.24"
marketplace: MLB
category_id: MLB1743
category_name: "Celulares e Smartphones"
effective_date: 2025-08-24T00:00:00Z
deprecated_after: null
source:
  api: "https://api.mercadolibre.com/categories/MLB1743/attributes"
  docs: "https://developers.mercadolivre.com.br/pt_br/categorias-e-atributos"
  last_fetched: 2025-08-24T03:00:00Z

rules:
  title:
    required: true
    min_length: 10
    max_length: 60
    forbidden_chars: ["@", "#", "$"]
    
  price:
    required: true
    min_value: 1.00
    max_value: 999999.99
    decimal_places: 2
    
  brand:
    required: true
    enum_values:
      - SAMSUNG
      - APPLE
      - MOTOROLA
      - XIAOMI
      # ... fetched from API
    
  condition:
    required: true
    enum_values: ["new", "used", "refurbished"]
    
  pictures:
    min_count: 1
    max_count: 10
    max_size_mb: 10
    formats: ["jpg", "jpeg", "png", "webp"]

custom_attributes:
  MODEL:
    required: true
    type: string
    max_length: 50
  STORAGE_CAPACITY:
    required: false
    type: enum
    values: ["16GB", "32GB", "64GB", "128GB", "256GB", "512GB", "1TB"]
  COLOR:
    required: false
    type: string

error_codes:
  MLB_TITLE_TOO_SHORT: "Title must have at least 10 characters"
  MLB_PRICE_INVALID: "Price must be between R$ 1,00 and R$ 999.999,99"
  MLB_BRAND_NOT_RECOGNIZED: "Brand not in approved list for this category"
```

---

## Developer Guidelines

### Loading Policies

```python
# NEVER do this:
if len(title) < 60:  # ❌ Hard-coded
    return "Title too long"

# ALWAYS do this:
policy = PolicyLoader.get("MLB", "MLB1743")
if len(title) > policy.rules.title.max_length:  # ✅ Data-driven
    return f"Title exceeds {policy.rules.title.max_length} chars"
```

### Handling Unknown Errors

```python
# When marketplace returns unknown error code
if error_code not in policy.error_codes:
    # Log for monitoring
    logger.warning(f"Unknown error code: {error_code}")
    
    # Pass through to user
    return {
        "error": "MARKETPLACE_ERROR",
        "details": marketplace_response,  # Full response
        "message": "Marketplace returned an error we haven't seen before"
    }
```

### Testing with Policies

```python
@pytest.mark.parametrize("category,version", [
    ("MLB1743", "2025.08.24"),
    ("MLB1743", "2025.08.23"),  # Previous version
])
def test_title_validation(category, version):
    policy = PolicyLoader.get("MLB", category, version=version)
    assert validate_title("Short", policy) == False
    assert validate_title("A" * 61, policy) == False
    assert validate_title("Valid Product Title", policy) == True
```

---

## Monitoring & Alerts

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `policy.version.deployed` | Current active version per category | - |
| `policy.errors.unknown` | Count of unknown error codes | > 100/hour |
| `policy.errors.rate` | Error rate per category/version | > 20% increase |
| `policy.rollback.count` | Number of emergency rollbacks | > 0 |
| `policy.canary.success_rate` | Success rate in canary | < 90% |

### Grafana Dashboard

```
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ Active Policy Versions      │ │ Error Rate by Category      │
│ MLB1743: v2025.08.24 ✓     │ │ MLB1743: 2.3% ↓            │
│ MLB1055: v2025.08.23 ⚠     │ │ MLB1055: 5.1% ↑            │
└─────────────────────────────┘ └─────────────────────────────┘

┌─────────────────────────────┐ ┌─────────────────────────────┐
│ Unknown Error Codes (24h)   │ │ Canary Performance          │
│ MLB_NEW_ERROR_123: 45       │ │ Old: 95.2% success          │
│ AMZN_UNKNOWN_456: 12        │ │ New: 94.8% success ⚠        │
└─────────────────────────────┘ └─────────────────────────────┘
```

---

## Rollback Procedure

1. **Automatic Rollback** (if canary success < 85%):
   ```bash
   kubectl set env deployment/api POLICY_VERSION_MLB1743=2025.08.23
   ```

2. **Manual Rollback** (ops decision):
   ```bash
   # Via feature flag
   curl -X POST https://api.validahub.com/admin/policies/rollback \
     -d '{"marketplace": "MLB", "category": "MLB1743", "version": "2025.08.23"}'
   ```

3. **Tenant-specific freeze**:
   ```sql
   UPDATE tenant_settings 
   SET policy_freeze = '{"MLB1743": "2025.08.23"}'
   WHERE tenant_id = ?;
   ```

---

## Roadmap

- [ ] **Q4 2024**: MLB harvester + canary system
- [ ] **Q1 2025**: Amazon/Magalu harvesters
- [ ] **Q2 2025**: Policy diff UI for customers
- [ ] **Q3 2025**: ML-based rule prediction
- [ ] **Q4 2025**: Real-time sync with marketplace webhooks

### Phase 1: Foundation (Current)
* Manual policy updates via PR
* Basic versioning
* Contract tests

### Phase 2: Automation
* Automated harvesting
* Canary deployments
* Monitoring dashboards

### Phase 3: Intelligence
* Predictive rule changes
* Auto-correction suggestions
* Cross-marketplace normalization

---

## Benefits

* **No silent breakages**: Customers are shielded from sudden rule changes
* **Traceability**: Every rule has origin and version
* **Fast adaptation**: We can ship new rules in hours without regression
* **Confidence**: Engineering + customers know validations reflect the live marketplace
* **Compliance**: Full audit trail for regulatory requirements

---

## Appendix A: Policy File Validation

All policy files are validated against this JSON Schema on commit:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "marketplace", "category_id", "rules"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d{4}\\.\\d{2}\\.\\d{2}$"
    },
    "marketplace": {
      "type": "string",
      "enum": ["MLB", "AMZN_BR", "MGLU", "AMER"]
    },
    "rules": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "required": {"type": "boolean"},
          "min_length": {"type": "integer", "minimum": 0},
          "max_length": {"type": "integer", "minimum": 1}
        }
      }
    }
  }
}
```

---

## Appendix B: Emergency Contacts

* **Policy Issues**: #validahub-policies (Slack)
* **Rollback Authority**: On-call SRE + Product Manager
* **Marketplace Liaisons**:
  * MLB: technical-support@mercadolibre.com
  * Amazon: sp-api-support@amazon.com

---

*Last Updated: 2024-08-25*
*Next Review: 2025-01-01*