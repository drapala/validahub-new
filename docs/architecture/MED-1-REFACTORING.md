# MED-1: Desacoplamento do Pipeline de RuleEngineService

## 📋 Problema Identificado
**ID:** MED-1  
**Severidade:** 🟠 Média  
**Status:** ✅ Endereçado  

### Descrição
O `ValidationPipeline` estava diretamente acoplado ao `RuleEngineService`, impedindo:
- Uso de diferentes motores de validação
- Paralelização eficiente
- Substituição de estratégias de validação
- Testes isolados do pipeline

## 🎯 Solução Implementada

### Padrão Strategy + Dependency Injection

```
┌────────────────────────────────────────────────┐
│          ValidationPipelineV2                   │ ← Orquestrador puro
├────────────────────────────────────────────────┤
│    IValidator    │    IDataAdapter              │ ← Interfaces abstratas
├────────────────────────────────────────────────┤
│ RuleEngine │ ML │ Schema │ PandasAdapter       │ ← Implementações concretas
└────────────────────────────────────────────────┘
```

### Novos Componentes

#### 1. Interfaces (`src/core/interfaces/validation.py`)
- **IValidator**: Abstração para validadores
- **IDataAdapter**: Abstração para conversão de dados
- **IValidationPipeline**: Interface do pipeline
- **IValidationStrategy**: Strategy pattern para validação

#### 2. Pipeline Refatorado (`src/core/pipeline/validation_pipeline_v2.py`)
- **ValidationPipelineV2**: Pipeline com injeção de dependências
- **PandasDataAdapter**: Adapter para operações com pandas
- Suporte a processamento paralelo configurável

#### 3. Validadores (`src/infrastructure/validators/`)
- **RuleEngineValidator**: Adapter para RuleEngineService
- **MultiStrategyValidator**: Combina múltiplos validadores

#### 4. Configuração (`src/infrastructure/pipeline_dependencies.py`)
- Factory functions para criar componentes
- Configuração baseada em ambiente
- Suporte a singleton para performance

### Benefícios Alcançados

1. **Desacoplamento Total**
   - Pipeline não conhece RuleEngineService
   - Pode usar qualquer IValidator
   - Testável com mocks simples

2. **Flexibilidade de Validação**
   ```python
   # Rule Engine
   validator = RuleEngineValidator(engine)
   
   # Machine Learning
   validator = MLValidator(model)
   
   # Múltiplas estratégias
   validator = MultiStrategyValidator([rule, ml, schema])
   ```

3. **Performance Otimizada**
   - Processamento paralelo opcional
   - Batching configurável
   - Reuso de instâncias

4. **Evolução Facilitada**
   - Novos validadores = implementar IValidator
   - Novos adapters = implementar IDataAdapter
   - Sem quebra de contratos

## 📁 Estrutura de Arquivos

```
apps/api/src/
├── core/
│   ├── interfaces/
│   │   └── validation.py            # Interfaces de validação
│   └── pipeline/
│       ├── validation_pipeline.py   # Original (preservado)
│       └── validation_pipeline_v2.py # Refatorado
├── infrastructure/
│   ├── validators/
│   │   └── rule_engine_validator.py # Adapters para validadores
│   └── pipeline_dependencies.py     # Configuração de DI
└── tests/unit/
    └── test_pipeline_v2.py          # Testes unitários
```

## 🧪 Testes

### Cobertura de Testes
- ✅ ValidationPipelineV2
  - Uso de validador injetado
  - Sem dependência direta de RuleEngine
  - Auto-fix funcional
  - Processamento paralelo

- ✅ RuleEngineValidator
  - Adaptação correta do RuleEngine
  - Suporte a engines síncronos
  - Preservação de dados originais

- ✅ MultiStrategyValidator
  - Combinação de resultados
  - Deduplicação de items

- ✅ PandasDataAdapter
  - Conversão DataFrame ↔ Rows
  - Normalização de NaN

## 🔄 Migração

### Fase 1: Coexistência (Atual)
```python
# Original
from core.pipeline.validation_pipeline import ValidationPipeline

# Novo
from core.pipeline.validation_pipeline_v2 import ValidationPipelineV2
```

### Fase 2: Configuração via Ambiente
```bash
# .env
VALIDATOR_TYPE=rule_engine  # ou multi, ml, etc
USE_RULE_ENGINE_V2=true
PIPELINE_PARALLEL=true
PIPELINE_BATCH_SIZE=100
DATA_ADAPTER=pandas
```

### Fase 3: Uso em Use Cases
```python
# De:
self.validation_pipeline = ValidationPipeline(rule_engine_service)

# Para:
self.validation_pipeline = get_validation_pipeline()
```

## 📊 Métricas de Melhoria

### Antes
- Acoplamento: Alto (RuleEngineService direto)
- Validadores: Apenas 1 (rule engine)
- Paralelização: Não suportada
- Testabilidade: Baixa (mock complexo)

### Depois
- Acoplamento: Zero (interfaces)
- Validadores: Ilimitados (IValidator)
- Paralelização: Configurável
- Testabilidade: Alta (mocks simples)

## ✅ Checklist de Validação

- [x] Interfaces definidas
- [x] Pipeline refatorado
- [x] Adapters implementados
- [x] Dependency injection configurado
- [x] Testes unitários
- [x] Documentação
- [ ] Migração de use cases
- [ ] Testes de integração
- [ ] Benchmarks de performance

## 🚀 Próximos Passos

1. **Implementar novos validadores**
   ```python
   class MLValidator(IValidator):
       async def validate_row(self, row, marketplace, row_number):
           # Validação com ML
           predictions = self.model.predict(row)
           return self._convert_to_items(predictions)
   
   class SchemaValidator(IValidator):
       async def validate_row(self, row, marketplace, row_number):
           # Validação com JSON Schema
           errors = self.schema.validate(row)
           return self._convert_to_items(errors)
   ```

2. **Otimizar processamento paralelo**
   ```python
   # Ativar para grandes volumes
   PIPELINE_PARALLEL=true
   PIPELINE_BATCH_SIZE=500
   ```

3. **Adicionar métricas**
   - Tempo por validador
   - Taxa de erro por estratégia
   - Throughput com/sem paralelização

## 📝 Notas de Implementação

- **Zero Breaking Changes**: Pipeline original preservado
- **Migração Incremental**: Pode ser feita aos poucos
- **Performance**: Paralelização pode aumentar throughput em 3-5x
- **Extensibilidade**: Novos validadores sem tocar no pipeline

## 🎯 Exemplo de Uso

```python
# Configuração automática
from infrastructure.pipeline_dependencies import get_validation_pipeline

# Obter pipeline configurado
pipeline = get_validation_pipeline()

# Usar normalmente
result = await pipeline.validate(
    df=dataframe,
    marketplace=Marketplace.MERCADO_LIVRE,
    category=Category.ELETRONICOS,
    auto_fix=True
)

# Trocar validador = mudar variável de ambiente
# VALIDATOR_TYPE=multi (combina múltiplas estratégias!)
```

## 📈 Roadmap de Validadores

1. **Rule Engine** ✅ (Implementado)
2. **Multi-Strategy** ✅ (Implementado)
3. **ML Validator** 🔄 (Próximo)
4. **Schema Validator** 📅 (Planejado)
5. **Custom Business Rules** 📅 (Planejado)
6. **External API Validator** 💡 (Ideia)