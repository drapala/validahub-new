# Plano de Refatoração Pragmática

## Princípio Fundamental
**Reduzir acoplamento e custo de mudança, não eliminar condicionais.**

O objetivo não é "zero-ifs", mas sim código mais manutenível, testável e extensível. Condicionais explícitas muitas vezes são mais honestas e imediatas que abstrações desnecessárias.

## Quando Usar Cada Abordagem

### ✅ Use Data-Driven/Registries Quando:
- As variações são **dados**, não lógica (ex: limites de caracteres por marketplace)
- Há muitas variações similares (5+ casos)
- As regras mudam frequentemente ou vêm de configuração externa
- Você precisa adicionar novos casos sem recompilar

### ✅ Mantenha if/match Quando:
- A lógica é específica e complexa para cada caso
- Há poucos casos (2-3)
- Os casos são fundamentalmente diferentes
- A clareza é mais importante que a "pureza"

## Refatorações Recomendadas

### 1. Marketplace Configurations (✅ BOM CANDIDATO)
**Localização**: `src/services/corrector_v2.py`

**Por quê refatorar**: São configurações puras (limites, defaults), não lógica complexa.

```python
# Em vez de esconder em registries complexos, use configuração explícita
@dataclass
class MarketplaceConfig:
    title_max_length: int
    title_default: str
    price_min: float
    # ... outras configs

MARKETPLACE_CONFIGS = {
    Marketplace.MERCADO_LIVRE: MarketplaceConfig(
        title_max_length=60,
        title_default="Produto sem título",
        price_min=0.01
    ),
    Marketplace.SHOPEE: MarketplaceConfig(
        title_max_length=100,
        title_default="Product Title",
        price_min=0.01
    ),
}

# Uso simples e direto
config = MARKETPLACE_CONFIGS[self.marketplace]
if len(title) > config.title_max_length:
    title = title[:config.title_max_length]
```

### 2. Validação de Arquivos (❌ NÃO REFATORAR)
**Localização**: `src/api/validate.py`

**Por quê manter**: É simples, direto e raramente muda.

```python
# MANTER ASSIM - é honesto e imediato
if not file.filename.endswith(('.csv', '.CSV')):
    raise HTTPException(400, "File must be CSV")

if file.size > MAX_FILE_SIZE:
    raise HTTPException(400, "File too large")
```

### 3. Correções de Erro (⚠️ REFATORAR PARCIALMENTE)
**Localização**: `src/services/corrector.py`

**Abordagem híbrida**: Classificador simples + lógica específica

```python
# Classificador simples para casos comuns
def classify_error_type(error_text: str) -> ErrorType:
    """Retorna tipo genérico do erro, não tenta resolver tudo"""
    error_lower = error_text.lower()
    if "too long" in error_lower or "max length" in error_lower:
        return ErrorType.LENGTH_EXCEEDED
    if "negative" in error_lower or "must be positive" in error_lower:
        return ErrorType.INVALID_SIGN
    if "required" in error_lower or "missing" in error_lower:
        return ErrorType.MISSING_VALUE
    return ErrorType.UNKNOWN

# Lógica específica permanece explícita
def apply_correction(error: ValidationError, value: Any) -> Any:
    error_type = classify_error_type(error.message)
    
    match error_type:
        case ErrorType.LENGTH_EXCEEDED:
            # Lógica específica para cada campo
            if error.column == "title":
                return value[:60]  # ML tem limite menor
            elif error.column == "description":
                return value[:500]
            else:
                return value[:100]  # default conservador
                
        case ErrorType.INVALID_SIGN:
            if error.column == "price":
                return max(0.01, abs(float(value or 0)))
            elif error.column == "stock":
                return max(0, int(value or 0))
            else:
                return abs(value)
                
        case ErrorType.MISSING_VALUE:
            # Defaults específicos por campo
            return get_field_default(error.column)
            
        case _:
            return value
```

### 4. Pipeline de Validação (✅ BOM CANDIDATO)
**Localização**: `src/core/pipeline/`

**Por quê refatorar**: Pipelines são naturalmente composicionais.

```python
# Pipeline composicional, mas simples
class ValidationPipeline:
    def __init__(self, validators: List[Validator]):
        self.validators = validators
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        errors = []
        for validator in self.validators:
            # Cada validator é independente e testável
            errors.extend(validator.validate(data))
        return ValidationResult(errors)

# Uso claro e extensível
pipeline = ValidationPipeline([
    RequiredFieldsValidator(["sku", "title", "price"]),
    NumericRangeValidator("price", min=0.01),
    TextLengthValidator("title", max=config.title_max_length),
    CategorySpecificValidator(category),
])
```

## Métricas Relevantes

### Focar em:
- **Acoplamento**: Classes/módulos dependem menos uns dos outros?
- **Testabilidade**: É mais fácil testar unidades isoladas?
- **Clareza**: Um desenvolvedor novo entende rapidamente?
- **Flexibilidade**: É fácil adicionar novos marketplaces/regras?

### Ignorar:
- Contagem de ifs (métrica superficial)
- Linhas de código (pode aumentar com boa abstração)
- "Pureza funcional" (não é o objetivo)

## Plano de Implementação Revisado

### Fase 1: Quick Wins (1 semana)
- [ ] Extrair configurações de marketplace para data classes
- [ ] Criar pipeline simples de validação
- [ ] Melhorar mensagens de erro (mais contexto)

### Fase 2: Refatorações Estruturais (2 semanas)
- [ ] Implementar classificador de erros básico
- [ ] Separar regras de negócio de regras técnicas
- [ ] Criar abstrações APENAS onde há variação real

### Fase 3: Consolidação (1 semana)
- [ ] Documentar padrões escolhidos
- [ ] Treinar equipe nos novos padrões
- [ ] Medir impacto real (bugs, tempo de desenvolvimento)

## Anti-Patterns a Evitar

### 🚫 Strategy Pattern Everywhere
```python
# RUIM - abstração desnecessária
class TitleValidator(ValidationStrategy):
    def validate(self, value):
        return len(value) <= 60

validator = ValidatorFactory.create("title")
result = validator.validate(data)
```

### ✅ Preferir Simplicidade
```python
# BOM - direto e claro
if len(title) > 60:
    errors.append("Title too long")
```

### 🚫 Registry Pattern para Tudo
```python
# RUIM - indireção desnecessária
CorrectorRegistry.register("too_long", TooLongCorrector)
CorrectorRegistry.register("negative", NegativeCorrector)
corrector = CorrectorRegistry.get(error_type)
```

### ✅ Match/Case Quando Apropriado
```python
# BOM - casos explícitos e rastreáveis
match error_type:
    case "too_long": return value[:limit]
    case "negative": return abs(value)
    case _: return value
```

## Conclusão

O código bom equilibra:
- **Simplicidade** vs Flexibilidade
- **Explícito** vs DRY
- **Direto** vs Extensível

Não existe bala de prata. Use a ferramenta certa para cada problema:
- Dados → Configuração
- Lógica simples → if/match
- Composição → Pipelines
- Variação complexa → Polimorfismo

O objetivo é código que seja fácil de:
1. Entender (ler uma vez e saber o que faz)
2. Modificar (adicionar casos sem quebrar outros)
3. Testar (unidades isoladas e previsíveis)
4. Debugar (fluxo rastreável)