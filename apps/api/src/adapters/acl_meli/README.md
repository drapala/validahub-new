# MELI ACL (Anti-Corruption Layer)

## Overview

The MELI ACL module provides an Anti-Corruption Layer for integrating with Mercado Livre (MELI) marketplace APIs. It transforms MELI-specific rule formats into a canonical rule model that can be used consistently across different marketplaces.

## Architecture

```
acl_meli/
├── models/                 # Data models
│   ├── canonical_rule.py   # Canonical Rule Model (CRM)
│   └── meli_models.py      # MELI-specific models
├── clients/                # HTTP clients
│   └── meli_client.py      # MELI API client with rate limiting
├── mappers/                # Data transformation
│   └── meli_to_canonical_mapper.py  # MELI to CRM mapper
├── errors/                 # Error handling
│   └── meli_error_translator.py     # Error translation
├── importers/              # Orchestration
│   └── meli_rules_importer.py       # Main importer
└── tests/                  # Tests and fixtures
    ├── fixtures/           # Test data
    └── test_*.py           # Unit tests
```

## Components

### 1. Canonical Rule Model (CRM)

The Canonical Rule Model provides a unified representation for marketplace rules:

```python
from adapters.acl_meli.models.canonical_rule import CanonicalRule, CanonicalRuleSet

# A canonical rule represents a single validation requirement
rule = CanonicalRule(
    id="meli_brand_required",
    marketplace_id="MELI",
    field_name="brand",
    rule_type=RuleType.REQUIRED,
    data_type=DataType.STRING,
    severity=RuleSeverity.ERROR,
    message="Brand is required"
)
```

**Key Features:**
- Normalized rule representation
- Support for multiple rule types (required, length, pattern, enum, etc.)
- Severity levels (error, warning, info)
- Conditional rules and dependencies
- Built-in validation methods

### 2. MELI Client

HTTP client for communicating with MELI APIs:

```python
from adapters.acl_meli.clients.meli_client import MeliClient

async with MeliClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    site_id="MLB"  # Brazil
) as client:
    category = await client.get_category("MLB1051")
    attributes = await client.get_category_attributes("MLB1051")
```

**Features:**
- OAuth authentication
- Rate limiting (configurable)
- Automatic retry with exponential backoff
- Async/await support

### 3. MELI to Canonical Mapper

Transforms MELI-specific rules to canonical format:

```python
from adapters.acl_meli.mappers.meli_to_canonical_mapper import MeliToCanonicalMapper

mapper = MeliToCanonicalMapper(marketplace_id="MELI")

# Map MELI attribute to canonical rules
canonical_rules = mapper.map_attribute_to_rules(meli_attribute)

# Map entire category
canonical_ruleset = mapper.map_category_to_ruleset(meli_category)
```

**Mapping Logic:**
- Required attributes → Required rules
- value_min_length → MinLength rules
- value_max_length → MaxLength rules
- value_pattern → Pattern rules
- allowed_values → Enum rules

### 4. Error Translator

Translates MELI API errors to canonical error format:

```python
from adapters.acl_meli.errors.meli_error_translator import MeliErrorTranslator

translator = MeliErrorTranslator()

# Translate MELI error
canonical_error = translator.translate_api_error(meli_error)

# Create error summary
summary = translator.create_error_summary(errors)
```

**Error Categories:**
- Authentication errors
- Validation errors
- Rate limiting errors
- System errors

### 5. Rules Importer (Orchestrator)

Main orchestrator that coordinates all components:

```python
from adapters.acl_meli.importers.meli_rules_importer import MeliRulesImporter

importer = MeliRulesImporter(
    client=meli_client,
    cache_dir="cache/meli_rules",
    cache_ttl_hours=24
)

# Import category rules
result = await importer.import_category_rules(
    category_id="MLB1051",
    use_cache=True
)

if result.is_ok():
    ruleset = result.unwrap()
    print(f"Imported {len(ruleset.rules)} rules")
```

**Features:**
- Rule caching with TTL
- Batch import for multiple categories
- Category search functionality
- Export to multiple formats (JSON, YAML, CSV)

## Usage Examples

### Basic Rule Import

```python
import asyncio
from adapters.acl_meli.clients.meli_client import MeliClient
from adapters.acl_meli.importers.meli_rules_importer import MeliRulesImporter

async def import_rules():
    # Initialize client
    client = MeliClient(
        access_token="your_token",
        site_id="MLB"
    )
    
    # Initialize importer
    importer = MeliRulesImporter(client=client)
    
    # Import rules for cellphones category
    result = await importer.import_category_rules("MLB1051")
    
    if result.is_ok():
        ruleset = result.unwrap()
        
        # Get required fields
        required_fields = ruleset.get_required_fields()
        print(f"Required fields: {required_fields}")
        
        # Validate data
        product_data = {
            "brand": "Samsung",
            "model": "Galaxy S21",
            "color": "Black"
        }
        
        errors = ruleset.validate_data(product_data)
        if errors:
            print(f"Validation errors: {errors}")

asyncio.run(import_rules())
```

### Search and Import Category

```python
async def search_category():
    async with MeliClient(site_id="MLB") as client:
        importer = MeliRulesImporter(client=client)
        
        # Search for category and import rules
        result = await importer.search_and_import_category(
            query="smartphones",
            use_cache=True
        )
        
        if result.is_ok():
            ruleset = result.unwrap()
            # Export to JSON
            export_result = importer.export_rules_to_file(
                ruleset,
                output_path="rules/smartphones.json",
                format="json"
            )

asyncio.run(search_category())
```

### Validate Product Data

```python
async def validate_product():
    # Import rules
    importer = MeliRulesImporter()
    rule_result = await importer.import_category_rules("MLB1051")
    
    if rule_result.is_ok():
        ruleset = rule_result.unwrap()
        
        # Product data to validate
        product = {
            "brand": "Apple",
            "model": "iPhone 13",
            "color": "Blue",
            "internal_memory": "128 GB",
            "ram": "6 GB",
            "operating_system": "iOS"
        }
        
        # Validate
        validation_result = await importer.validate_data_against_rules(
            data=product,
            ruleset=ruleset
        )
        
        if validation_result["valid"]:
            print("Product data is valid!")
        else:
            print(f"Validation errors: {validation_result['errors']}")

asyncio.run(validate_product())
```

## Configuration

### Environment Variables

```bash
# MELI OAuth credentials
MELI_CLIENT_ID=your_client_id
MELI_CLIENT_SECRET=your_client_secret
MELI_ACCESS_TOKEN=your_access_token

# Site configuration
MELI_SITE_ID=MLB  # Brazil

# Rate limiting
MELI_RATE_LIMIT=10  # Calls per second

# Cache configuration
MELI_CACHE_DIR=/path/to/cache
MELI_CACHE_TTL_HOURS=24
```

### Cache Management

The importer caches rules locally to reduce API calls:

```python
# Clear cache for a category
cache_dir = Path("cache/meli_rules")
cache_file = cache_dir / "MLB1051.json"
cache_file.unlink(missing_ok=True)

# Force refresh (ignore cache)
result = await importer.import_category_rules(
    category_id="MLB1051",
    use_cache=False,
    save_cache=True
)
```

## Testing

Run unit tests:

```bash
# Run all tests
pytest src/adapters/acl_meli/tests/

# Run specific test file
pytest src/adapters/acl_meli/tests/test_mapper.py

# Run with coverage
pytest --cov=src/adapters/acl_meli src/adapters/acl_meli/tests/
```

## Integration with ValidaHub

The MELI ACL can be integrated with ValidaHub's validation pipeline:

```python
from services.rule_engine_service import RuleEngineService
from adapters.acl_meli.importers.meli_rules_importer import MeliRulesImporter

# Import MELI rules
importer = MeliRulesImporter()
meli_rules = await importer.import_category_rules("MLB1051")

# Convert to ValidaHub format
rule_engine = RuleEngineService()
rule_engine.add_marketplace_rules(
    marketplace="MELI",
    rules=meli_rules
)

# Validate CSV with MELI rules
validation_result = rule_engine.validate_csv(
    file_path="products.csv",
    marketplace="MELI"
)
```

## Error Handling

The ACL provides comprehensive error handling:

```python
result = await importer.import_category_rules("INVALID_ID")

if result.is_err():
    errors = result.err()
    for error in errors:
        print(f"Error: {error.code} - {error.message}")
        if error.recoverable:
            print(f"  Retry after: {error.retry_after} seconds")
```

## Performance Considerations

1. **Rate Limiting**: Default is 10 requests/second
2. **Caching**: Rules are cached for 24 hours by default
3. **Batch Operations**: Use `import_multiple_categories` for bulk imports
4. **Async Operations**: All API calls are async for better performance

## Future Enhancements

- [ ] Support for more MELI endpoints
- [ ] WebSocket support for real-time updates
- [ ] Rule versioning and change tracking
- [ ] Integration with more marketplaces
- [ ] Rule conflict detection
- [ ] Advanced caching strategies
- [ ] Metrics and monitoring

## License

This module is part of the ValidaHub project and follows the same license terms.