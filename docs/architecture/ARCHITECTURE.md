# ValidaHub - Arquitetura do Sistema

## Visão Geral

ValidaHub utiliza uma arquitetura baseada em **Strategy Pattern** e **Chain of Responsibility** para permitir extensibilidade e baixo acoplamento entre componentes.

## Princípios Arquiteturais

1. **Open/Closed Principle** - Aberto para extensão, fechado para modificação
2. **Dependency Inversion** - Depender de abstrações, não de implementações
3. **Single Responsibility** - Cada classe tem uma única responsabilidade
4. **Plugin Architecture** - Novas regras e marketplaces como plugins

## Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                         API Gateway                          │
│                    (FastAPI - api/validate.py)              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Validation Pipeline                       │
│                  (Orchestrator/Coordinator)                  │
└────────┬──────────────────┬──────────────────┬─────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Rule Registry │  │ Rule Engine  │  │  Corrector   │
│              │  │              │  │   Engine     │
└──────────────┘  └──────────────┘  └──────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────────────────────────────────────────┐
│                  Rule Providers                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │Marketplace│ │ Category │ │  Custom  │         │
│  │  Rules   │ │  Rules   │ │  Rules   │         │
│  └──────────┘ └──────────┘ └──────────┘         │
└───────────────────────────────────────────────────┘
```

## Estrutura de Diretórios Proposta

```
apps/api/src/
├── core/
│   ├── interfaces/           # Abstrações/Contratos
│   │   ├── rule.py          # IRule, IRuleProvider
│   │   ├── validator.py     # IValidator
│   │   └── corrector.py     # ICorrector
│   │
│   ├── pipeline/            # Orquestração
│   │   ├── validation_pipeline.py
│   │   └── correction_pipeline.py
│   │
│   └── engines/             # Implementações core
│       ├── rule_engine.py
│       └── correction_engine.py
│
├── rules/                   # Regras como plugins
│   ├── base/
│   │   ├── required_fields.py
│   │   ├── data_types.py
│   │   └── format_rules.py
│   │
│   ├── marketplaces/
│   │   ├── mercado_livre/
│   │   │   ├── __init__.py
│   │   │   ├── rules.yaml    # Configuração declarativa
│   │   │   └── validators.py # Validadores específicos
│   │   │
│   │   ├── shopee/
│   │   └── amazon/
│   │
│   └── categories/
│       ├── electronics/
│       ├── fashion/
│       └── home/
│
├── corrections/            # Correções como plugins
│   ├── base/
│   │   ├── text_corrections.py
│   │   ├── number_corrections.py
│   │   └── format_corrections.py
│   │
│   └── marketplace_specific/
│       └── mercado_livre_corrections.py
│
└── config/
    ├── rules_config.yaml   # Configuração de regras
    └── marketplace_config.yaml
```

## Design Patterns Utilizados

### 1. Strategy Pattern
```python
# core/interfaces/rule.py
from abc import ABC, abstractmethod
from typing import Any, Optional

class IRule(ABC):
    @abstractmethod
    def validate(self, value: Any, context: dict) -> Optional[ValidationError]:
        pass

class ICorrection(ABC):
    @abstractmethod
    def can_correct(self, error: ValidationError) -> bool:
        pass
    
    @abstractmethod
    def apply(self, value: Any, error: ValidationError) -> Any:
        pass
```

### 2. Chain of Responsibility
```python
# core/pipeline/validation_pipeline.py
class ValidationPipeline:
    def __init__(self):
        self.validators: List[IValidator] = []
    
    def add_validator(self, validator: IValidator):
        self.validators.append(validator)
    
    def validate(self, data: DataFrame) -> ValidationResult:
        errors = []
        for validator in self.validators:
            errors.extend(validator.validate(data))
        return ValidationResult(errors=errors)
```

### 3. Factory Pattern
```python
# rules/factory.py
class RuleFactory:
    _rules: Dict[str, Type[IRule]] = {}
    
    @classmethod
    def register(cls, name: str, rule_class: Type[IRule]):
        cls._rules[name] = rule_class
    
    @classmethod
    def create(cls, name: str, **kwargs) -> IRule:
        return cls._rules[name](**kwargs)
```

### 4. Plugin Architecture
```python
# rules/loader.py
class RuleLoader:
    def load_marketplace_rules(self, marketplace: str) -> List[IRule]:
        # Carrega regras de arquivo YAML
        config = self._load_config(f"rules/marketplaces/{marketplace}/rules.yaml")
        
        rules = []
        for rule_config in config['rules']:
            rule_class = RuleFactory.create(rule_config['type'])
            rules.append(rule_class(**rule_config['params']))
        
        return rules
```

## Exemplo de Configuração Declarativa

```yaml
# rules/marketplaces/mercado_livre/rules.yaml
marketplace: mercado_livre
version: "2.0.0"
rules:
  - type: required_fields
    params:
      fields: [sku, title, price, available_quantity, condition]
      
  - type: text_length
    params:
      field: title
      max_length: 60
      
  - type: number_range
    params:
      field: price
      min: 0.01
      max: 999999.99
      
  - type: custom_validator
    params:
      class: MercadoLivreSpecificValidator
      module: rules.marketplaces.mercado_livre.validators
```

## Vantagens da Nova Arquitetura

1. **Extensibilidade** ✅
   - Adicionar marketplace = adicionar pasta com regras
   - Sem modificar código existente

2. **Testabilidade** ✅
   - Cada regra pode ser testada isoladamente
   - Mocks fáceis de criar para interfaces

3. **Manutenibilidade** ✅
   - Regras organizadas por domínio
   - Fácil localizar e modificar regras específicas

4. **Reusabilidade** ✅
   - Regras base compartilhadas
   - Composição de regras complexas

5. **Versionamento** ✅
   - Suporte a múltiplas versões de regras
   - Migração gradual entre versões

6. **Performance** ✅
   - Lazy loading de regras
   - Cache de regras compiladas
   - Processamento paralelo possível

## Implementação Gradual

### Fase 1: Abstrações (Sprint Atual)
- [ ] Criar interfaces base (IRule, IValidator, ICorrector)
- [ ] Implementar RuleEngine básico
- [ ] Migrar regras existentes para o novo formato

### Fase 2: Plugins (Próxima Sprint)
- [ ] Sistema de carregamento dinâmico de regras
- [ ] Configuração via YAML
- [ ] Hot reload de regras

### Fase 3: Otimizações
- [ ] Cache de regras compiladas
- [ ] Processamento paralelo
- [ ] Métricas e telemetria

## Exemplo de Uso

```python
# api/validate.py
from core.pipeline import ValidationPipeline
from rules.loader import RuleLoader

@router.post("/validate")
async def validate_csv(
    file: UploadFile,
    marketplace: str,
    category: str
):
    # Carrega regras dinamicamente
    loader = RuleLoader()
    rules = loader.load_rules(marketplace, category)
    
    # Configura pipeline
    pipeline = ValidationPipeline()
    for rule in rules:
        pipeline.add_rule(rule)
    
    # Executa validação
    result = pipeline.validate(file)
    
    return result
```

## Conclusão

Esta arquitetura permite que o ValidaHub cresça de forma sustentável, adicionando novos marketplaces e regras sem comprometer a estabilidade do sistema existente.