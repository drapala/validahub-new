# CRIT-1: Refatoração de Endpoints Monolíticos

## 📋 Problema Identificado
**ID:** CRIT-1  
**Severidade:** 🔴 Crítica  
**Status:** ✅ Endereçado  

### Descrição
Os endpoints `validate_csv_v2` e `correct_csv_v2` violavam o Single Responsibility Principle (SRP) ao misturar:
- Parsing de CSV
- I/O de arquivos
- Lógica de negócio
- Orquestração HTTP

## 🎯 Solução Implementada

### Arquitetura Clean Architecture
Separação clara de responsabilidades em camadas:

```
┌─────────────────────────────────────────┐
│         HTTP Layer (Endpoints)          │  ← Apenas HTTP concerns
├─────────────────────────────────────────┤
│         Use Cases (Business)            │  ← Lógica de negócio pura
├─────────────────────────────────────────┤
│      Domain (Pipelines/Services)        │  ← Regras de domínio
├─────────────────────────────────────────┤
│      Infrastructure (File I/O, DB)      │  ← Detalhes técnicos
└─────────────────────────────────────────┘
```

### Novos Componentes

#### 1. Use Cases (`src/core/use_cases/`)
- **ValidateCsvUseCase**: Lógica de validação de CSV
- **CorrectCsvUseCase**: Lógica de correção de CSV
- **ValidateRowUseCase**: Lógica de validação de linha única

#### 2. Endpoints Refatorados (`src/api/v1/validation_refactored.py`)
- **validate_csv_clean**: Endpoint limpo para validação
- **correct_csv_clean**: Endpoint limpo para correção
- **validate_row_clean**: Endpoint limpo para validação de linha

### Benefícios Alcançados

1. **Separação de Responsabilidades**
   - Endpoints: Apenas HTTP (upload, responses)
   - Use Cases: Apenas lógica de negócio
   - Pipelines: Apenas regras de domínio

2. **Testabilidade**
   - Use cases testáveis isoladamente
   - Mocking simplificado
   - Testes unitários puros

3. **Manutenibilidade**
   - Mudanças isoladas por camada
   - Código mais legível
   - Menor acoplamento

4. **Evolução**
   - Fácil adicionar novos use cases
   - Trocar implementações sem afetar outras camadas
   - Suporte a diferentes protocolos (REST, GraphQL, gRPC)

## 📁 Estrutura de Arquivos

```
apps/api/src/
├── api/v1/
│   ├── validation.py                    # Original (preservado)
│   └── validation_refactored.py         # Refatorado
├── core/
│   └── use_cases/
│       ├── __init__.py
│       ├── base.py                      # Base class para use cases
│       ├── validate_csv.py              # Use case de validação
│       ├── correct_csv.py               # Use case de correção
│       └── validate_row.py              # Use case de linha
└── tests/unit/
    └── test_use_cases.py                # Testes unitários

```

## 🧪 Testes

### Cobertura de Testes
- ✅ ValidateCsvUseCase
  - Validação bem-sucedida
  - Validação com auto-fix
  - Tratamento de CSV vazio
  - Tratamento de erros

- ✅ CorrectCsvUseCase
  - Correção bem-sucedida
  - Caso sem correções necessárias
  - Tratamento de erros

- ✅ ValidateRowUseCase
  - Validação de linha única
  - Validação com auto-fix
  - Detecção de erros e warnings

## 🔄 Migração

### Fase 1: Coexistência (Atual)
- Endpoints originais preservados em `/api/v1/validation.py`
- Novos endpoints em `/api/v1/validation_refactored.py`
- Sufixo `-clean` nos novos endpoints

### Fase 2: Teste e Validação
```bash
# Testar novos endpoints
curl -X POST http://localhost:3001/api/v1/validate-clean \
  -F "file=@test.csv" \
  -F "marketplace=MERCADO_LIVRE" \
  -F "category=ELETRONICOS"

# Comparar com originais
curl -X POST http://localhost:3001/api/v1/validate \
  -F "file=@test.csv" \
  -F "marketplace=MERCADO_LIVRE" \
  -F "category=ELETRONICOS"
```

### Fase 3: Substituição
1. Atualizar frontend para usar novos endpoints
2. Deprecar endpoints antigos
3. Remover código legado após período de transição

## 📊 Métricas de Melhoria

### Antes
- Complexidade ciclomática: ~20 por endpoint
- Linhas por função: ~150
- Responsabilidades: 4-5 por endpoint
- Testabilidade: Baixa (muitos mocks necessários)

### Depois
- Complexidade ciclomática: ~5 por componente
- Linhas por função: ~50
- Responsabilidades: 1 por componente
- Testabilidade: Alta (testes isolados)

## ✅ Checklist de Validação

- [x] Use cases criados e testados
- [x] Endpoints refatorados
- [x] Testes unitários implementados
- [x] Documentação atualizada
- [x] Compatibilidade mantida
- [ ] Frontend atualizado
- [ ] Endpoints antigos deprecados
- [ ] Monitoramento em produção

## 🚀 Próximos Passos

1. **Validar em ambiente de desenvolvimento**
2. **Atualizar integração do frontend**
3. **Implementar jobs assíncronos** (MED-3)
4. **Adicionar telemetria estruturada** (LOW-4)
5. **Deprecar endpoints antigos**

## 📝 Notas de Implementação

- Mantida compatibilidade total com contratos existentes
- Nenhuma quebra de API
- Código original preservado para rollback
- Migração pode ser feita gradualmente