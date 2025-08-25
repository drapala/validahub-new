# Refactoring & Clean Architecture Checklist - ValidaHub

> **Objetivo**: Garantir aderência a Clean Architecture, DDD, SOLID e boas práticas  
> **Uso**: Para cada refatoração ou novo desenvolvimento, valide conformidade arquitetural

## 📊 Status da Arquitetura
- **Conformidade atual**: ⚠️ 2/5 (baseado em ARCHITECTURE_REPORT.md)
- **Última avaliação**: `2025-08-25`
- **Meta de conformidade**: 4/5 até próximo release

---

## 🏗️ Checklist de Arquitetura Limpa

### 📦 Separação de Camadas

#### Domain Layer (Núcleo do Negócio)
- [ ] **Entidades sem dependências externas**
  - Risco: Domínio acoplado a frameworks
  - Evidência: Apenas Python puro em `models/`, `schemas/`
  - Teste: Imports não devem ter pandas, sqlalchemy, fastapi

- [ ] **Value Objects imutáveis**
  - Risco: Estado mutável causando bugs
  - Evidência: Uso de `frozen=True` em dataclasses
  - Teste: Tentar modificar após criação deve falhar

- [ ] **Regras de negócio isoladas**
  - Risco: Lógica espalhada pela aplicação
  - Evidência: Toda validação em `core/validators/`
  - Teste: Executar regras sem infraestrutura

#### Application Layer (Casos de Uso)
- [ ] **Use Cases sem conhecer infraestrutura**
  - Risco: Acoplamento direto (violação atual!)
  - Evidência: Injeção via interfaces/ports
  - Teste: Mock de todas as dependências
  - **Fix**: Criar interfaces para RuleEngineService

- [ ] **Orchestração via portas**
  - Risco: Use case criando services diretamente
  - Evidência: Constructor injection apenas
  - Teste: Use case testável com stubs

- [ ] **DTOs para comunicação entre camadas**
  - Risco: Vazamento de detalhes de implementação
  - Evidência: Conversão explícita nas bordas
  - Teste: Schemas não conhecem ORM

#### Infrastructure Layer
- [ ] **Adapters implementam portas**
  - Risco: Dependência invertida quebrada
  - Evidência: `implements IRepository`
  - Teste: Trocar implementação sem quebrar

- [ ] **Configuração isolada de frameworks**
  - Risco: Core conhecendo FastAPI/SQLAlchemy
  - Evidência: Config em `infrastructure/config/`
  - Teste: Core sem imports de frameworks
  - **Fix**: Mover logging_config para infra

- [ ] **Sem manipulação global de estado**
  - Risco: sys.path alterado (RuleLoader)
  - Evidência: Imports relativos ou packages
  - Teste: Múltiplas instâncias isoladas
  - **Fix**: Remover sys.path.append

### 🎯 Princípios SOLID

- [ ] **Single Responsibility (SRP)**
  - Risco: God classes/services
  - Evidência: Classes com 1 razão para mudar
  - Teste: Coesão > 0.8
  - **Fix**: Dividir validators.py, RuleEngineServiceAdapter

- [ ] **Open/Closed (OCP)**
  - Risco: Modificar código existente para features
  - Evidência: Extensão via herança/composição
  - Teste: Nova feature sem alterar core

- [ ] **Liskov Substitution (LSP)**
  - Risco: Subclasses quebrando contratos
  - Evidência: Testes com todas as implementações
  - Teste: Substituir sem quebrar invariantes

- [ ] **Interface Segregation (ISP)**
  - Risco: Interfaces gordas forçando implementações vazias
  - Evidência: Interfaces pequenas e coesas
  - Teste: Nenhum método não utilizado

- [ ] **Dependency Inversion (DIP)**
  - Risco: Alto acoplamento a concretos
  - Evidência: Depender de abstrações
  - Teste: Inverter implementações facilmente
  - **Fix**: Criar IValidationService, IRuleLoader

### 🔄 Ciclos de Dependência

- [ ] **Sem ciclos entre módulos**
  - Risco: Impossível compilar/testar isoladamente
  - Evidência: Grafo acíclico de dependências
  - Teste: `pip install` cada módulo sozinho
  - **Fix atual**: core ↔ services, core ↔ infrastructure

- [ ] **Fan-out baixo (<5)**
  - Risco: Módulo muito acoplado
  - Evidência: Poucas dependências externas
  - Teste: Análise estática de imports
  - **Fix**: API com fan-out=5, workers=3

- [ ] **Fan-in controlado**
  - Risco: Módulo fazendo muita coisa
  - Evidência: Especialização clara
  - Teste: Métricas de acoplamento

### 🏛️ Domain-Driven Design

- [ ] **Bounded Contexts definidos**
  - Risco: Modelo anêmico ou confuso
  - Evidência: Contextos isolados (ex: MELI ACL)
  - Teste: Mudança em um não afeta outro
  - **Fix**: Formalizar ACL MELI como BC

- [ ] **Aggregates com invariantes**
  - Risco: Estado inconsistente
  - Evidência: Validação no aggregate root
  - Teste: Impossível criar estado inválido

- [ ] **Ubiquitous Language**
  - Risco: Termos técnicos vs negócio
  - Evidência: Glossário em docs
  - Teste: Nomes alinhados com domínio

### 🧩 Hexagonal Architecture (Ports & Adapters)

- [ ] **Portas como contratos**
  - Risco: Acoplamento a implementações
  - Evidência: Interfaces em `core/ports/`
  - Teste: Múltiplas implementações da porta

- [ ] **Adapters plugáveis**
  - Risco: Vendor lock-in
  - Evidência: Trocar DB/Queue facilmente
  - Teste: Tests com in-memory adapter

- [ ] **ACL para sistemas externos**
  - Risco: Mudanças externas quebram domínio
  - Evidência: Tradução na fronteira
  - Teste: Contract tests
  - **Status**: MELI ACL implementado ✓

### 🏭 Padrões e Anti-Patterns

#### Evitar
- [ ] **Sem God Services**
  - Check: < 5 responsabilidades por classe
  - **Fix**: RuleEngineServiceAdapter

- [ ] **Sem Anemic Domain**
  - Check: Entidades com comportamento
  - Status: Models apenas com dados ⚠️

- [ ] **Sem Feature Envy**
  - Check: Métodos usam dados locais
  - Status: Utils acessando múltiplos objetos ⚠️

- [ ] **Sem Helpers estáticos genéricos**
  - Check: Funções em contexto apropriado
  - **Fix**: DataFrameUtils, validators.py

#### Aplicar
- [ ] **Repository Pattern**
  - Check: Abstração de persistência
  - Status: Parcialmente implementado

- [ ] **Factory Pattern**
  - Check: Criação complexa encapsulada
  - **Fix**: Criar PipelineFactory

- [ ] **Strategy Pattern**
  - Check: Algoritmos intercambiáveis
  - Aplicar em: Validators, Loaders

- [ ] **Dependency Injection**
  - Check: Inversão de controle
  - **Fix**: Container DI para services

### 📐 Métricas de Qualidade

- [ ] **Complexidade ciclomática < 10**
  - Ferramenta: radon, flake8
  - Fix: Extrair métodos/classes

- [ ] **Cobertura de testes > 80%**
  - Ferramenta: pytest-cov
  - Focus: Use cases e domínio

- [ ] **Duplicação < 3%**
  - Ferramenta: jscpd
  - Fix: Extrair para shared

- [ ] **Acoplamento aferente < 7**
  - Ferramenta: pydeps
  - Fix: Reduzir dependências

---

## 🚀 Quick Wins (≤2h cada)

### 1. Interfaces para Services
```python
# core/ports/validation_service.py
from abc import ABC, abstractmethod

class IValidationService(ABC):
    @abstractmethod
    async def validate(self, data: dict) -> ValidationResult:
        pass

# application/use_cases/validate_csv.py
def __init__(self, validation_service: IValidationService):
    self.validation_service = validation_service  # não RuleEngineService
```

### 2. Remover sys.path manipulation
```python
# ANTES (infrastructure/loaders/rule_loader.py)
sys.path.append(str(rules_dir))  # ❌

# DEPOIS
from importlib import import_module
spec = importlib.util.spec_from_file_location(name, path)
```

### 3. Especializar validators
```python
# ANTES: utils/validators.py com 10+ funções ❌

# DEPOIS:
# utils/validators/email_validator.py
# utils/validators/product_id_validator.py
# utils/validators/pricing.py
```

### 4. Factory para Pipeline
```python
# infrastructure/factories/pipeline_factory.py
class PipelineFactory:
    def create_validation_pipeline(self, config: dict) -> ValidationPipeline:
        # Injeta dependências aqui
        pass

# api/v1/endpoints/validation.py
pipeline = factory.create_validation_pipeline(config)  # não new ValidationPipeline()
```

### 5. Logging sem frameworks
```python
# ANTES: core/logging_config.py importa fastapi ❌

# DEPOIS: infrastructure/logging/framework_config.py
def configure_fastapi_logging():
    # Config específica aqui
```

---

## 📋 Template de PR - Refatoração

```markdown
## Refactoring Checklist

### Arquitetura
- [x] Camadas: Domínio independente de infra
- [x] SOLID: DIP aplicado em ValidationService  
- [x] Ciclos: Removido core ↔ services
- [ ] N/A: DDD aggregates (não aplicável)

### Mudanças
- Interface IValidationService criada
- RuleLoader sem sys.path global
- validators.py dividido em 3 módulos

### Riscos
- Breaking: API de validators mudou
- Mitigação: Aliases temporários

### Testes
- Unit: 95% coverage em domain
- Integration: Pipeline com mock service
- E2E: Smoke tests passando

### Métricas
- Complexidade: 12 → 7
- Fan-out: 5 → 3
- Duplicação: 4% → 2%

Fixes #123
```

---

## 🔗 Referências
- [Clean Architecture - Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [DDD - Eric Evans](https://domainlanguage.com/ddd/)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Architecture Report](../ARCHITECTURE_REPORT.md)
- [Dependency Graph](../DEPENDENCY_GRAPH.md)

---

**Última atualização**: 2025-08-25  
**Próxima avaliação**: Após implementar quick wins