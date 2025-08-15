# ValidaHub API - Rule Engine Based Validation

## Overview

The ValidaHub API introduces a YAML-based rule engine for CSV validation and correction. This replaces the hardcoded validation logic with configurable rules that can be easily updated without code changes.

## Key Features

### 1. YAML-Based Rule Configuration
- Rules are defined in YAML files under `/rulesets/`
- Each marketplace can have its own ruleset
- Fallback to `default.yaml` if marketplace-specific rules not found
- Hot-reload capability without service restart

### 2. API Endpoints

#### `POST /api/v1/validate`
CSV validation with YAML-based rule engine:
- Uses YAML-configured rules
- Supports auto-fix mode
- Returns detailed validation items with errors and corrections
- Provides comprehensive summary statistics

```bash
curl -X POST http://localhost:3001/api/v1/validate \
  -F "file=@products.csv" \
  -F "marketplace=MERCADO_LIVRE" \
  -F "category=ELETRONICOS" \
  -F "auto_fix=true"
```

#### `POST /api/v1/validate_row`
Single row validation:
- Real-time validation for UI integrations
- Supports auto-fix
- Returns original and fixed row data

```bash
curl -X POST http://localhost:3001/api/v1/validate_row \
  -H "Content-Type: application/json" \
  -d '{"sku": "", "title": "Product", "price": -10}' \
  "?marketplace=MERCADO_LIVRE&auto_fix=true"
```

#### `POST /api/v1/correct`
Automatic CSV correction:
- Applies all available fixes
- Returns downloadable corrected CSV
- Includes correction statistics in headers

```bash
curl -X POST http://localhost:3001/api/v1/correct \
  -F "file=@products.csv" \
  -F "marketplace=MERCADO_LIVRE" \
  -F "category=ELETRONICOS" \
  -o corrected.csv
```

#### `POST /api/v1/reload_rules`
Reload validation rules:
- Updates rules without service restart
- Can target specific marketplace or all

```bash
curl -X POST http://localhost:3001/api/v1/reload_rules?marketplace=MERCADO_LIVRE
```

## Architecture

### Components

1. **RuleEngineService** (`src/services/rule_engine_service.py`)
   - Manages rule engine instances
   - Loads and caches YAML rulesets
   - Converts between rule engine and API formats

2. **ValidationPipeline** (`src/core/pipeline/validation_pipeline.py`)
   - Orchestrates validation process
   - Handles DataFrame processing
   - Generates validation results

3. **Rule Engine** (`libs/rule_engine/`)
   - YAML-based rule interpreter
   - Supports various check and fix types
   - Conditional rule execution

### Rule Structure

```yaml
version: "1.0"
name: "Marketplace Rules"
mappings:
  category_map:
    "Electronics": "ELETRONICOS"
    
rules:
  - id: "sku_required"
    name: "SKU is required"
    check:
      type: "required"
      field: "sku"
    fix:
      type: "set_default"
      field: "sku"
      value: "SKU-PENDING"
    meta:
      severity: "ERROR"
```

### Supported Rule Types

#### Check Types
- `required`: Field must have a value
- `numeric_min`: Numeric minimum value
- `numeric_max`: Numeric maximum value
- `in_set`: Value must be in allowed set
- `regex`: Pattern matching
- `length_min/max`: String length constraints

#### Fix Types
- `set_default`: Set default value
- `map_value`: Map to new value using mapping table
- `trim`: Remove whitespace
- `uppercase/lowercase`: Case conversion
- `coalesce`: Use first non-empty value

## Key Features

1. **Rule Configuration**
   - YAML configuration files
   - Hot-reload without restart
   - Marketplace-specific rules

2. **Response Format**
   - Detailed validation items with corrections
   - Comprehensive error and fix information
   - Summary statistics

3. **Auto-Fix Support**
   - Integrated auto-fix in validation
   - Configurable fix strategies
   - Confidence scores for corrections

## Configuration

### Environment Variables

```bash
# Rule engine configuration
RULE_ENGINE_CACHE_ENABLED=true
RULE_ENGINE_CACHE_TTL=3600
RULESETS_PATH=/path/to/rulesets
```

### Adding New Rules

1. Edit YAML file in `/rulesets/`
2. Call reload endpoint or restart service
3. Test with sample data

### Custom Marketplaces

Create new file: `/rulesets/{marketplace}.yaml`

```yaml
version: "1.0"
name: "Custom Marketplace Rules"
rules:
  # Add marketplace-specific rules
```

## Testing

### Unit Tests
```bash
pytest tests/unit/test_rule_engine_service.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_validation_endpoint.py -v
```

### Manual Testing
```bash
# Start the API
cd apps/api
uvicorn src.main:app --reload --port 3001

# Test validation
curl -X POST http://localhost:3001/api/v1/validate \
  -F "file=@test.csv" \
  -F "marketplace=MERCADO_LIVRE" \
  -F "category=ELETRONICOS"
```

## Performance Considerations

1. **Caching**: Rule engines are cached per marketplace
2. **Batch Processing**: Rules applied row-by-row for memory efficiency
3. **Async Support**: Large files processed asynchronously
4. **Streaming**: Results can be streamed for large datasets

## Troubleshooting

### Rules Not Loading
- Check YAML syntax
- Verify file paths
- Check logs for parsing errors

### Performance Issues
- Enable caching
- Reduce rule complexity
- Use async processing for large files

### Validation Not Working
- Reload rules via endpoint
- Check field names match CSV headers
- Verify rule conditions

## Future Enhancements

- [ ] Rule versioning and rollback
- [ ] A/B testing for rules
- [ ] Rule performance metrics
- [ ] Visual rule editor UI
- [ ] Rule validation and testing tools
- [ ] Machine learning-based rule suggestions