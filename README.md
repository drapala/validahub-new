# ValidaHub 🚀

![CI/CD](https://github.com/drapala/validahub-new/workflows/CI%2FCD%20Pipeline/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Node](https://img.shields.io/badge/node-20-green.svg)
[![codecov](https://codecov.io/gh/drapala/validahub-new/branch/main/graph/badge.svg)](https://codecov.io/gh/drapala/validahub-new)

**ValidaHub** é uma plataforma de validação e correção inteligente de arquivos CSV para marketplaces. Com arquitetura de plugins extensível, oferece validação específica por marketplace e categoria, com correções automáticas e preview em tempo real.

## 🏗️ Arquitetura Plugin-Based

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   ValidaHub                                      │
│                         Plataforma de Validação CSV                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 Frontend (Next.js)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Upload     │  │   Preview    │  │   Results    │  │  Corrections │       │
│  │   Component  │  │   Component  │  │    Table     │  │    Preview   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                    API REST
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Backend (FastAPI)                                   │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │                         API Layer (/api/v1)                             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │  /validate   │  │   /correct   │  │  /preview    │                 │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                 │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                         │
│                                        ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │                         Service Layer                                   │    │
│  │  ┌──────────────────────┐  ┌──────────────────────┐                   │    │
│  │  │   CSV Validator V2    │  │   CSV Corrector V2   │                   │    │
│  │  │  ┌────────────────┐  │  │  ┌────────────────┐  │                   │    │
│  │  │  │  Rule Engine   │  │  │  │  Correction    │  │                   │    │
│  │  │  │                │  │  │  │    Engine      │  │                   │    │
│  │  │  └────────────────┘  │  │  └────────────────┘  │                   │    │
│  │  └──────────────────────┘  └──────────────────────┘                   │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                         │
│                                        ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │                    Plugin Architecture Core                             │    │
│  │                                                                         │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │    │
│  │  │                        Interfaces                                │  │    │
│  │  │  ┌────────┐  ┌────────┐  ┌────────────┐  ┌──────────────┐     │  │    │
│  │  │  │ IRule  │  │IRulePr │  │ICorrector  │  │IValidator    │     │  │    │
│  │  │  │        │  │ovider  │  │            │  │              │     │  │    │
│  │  │  └────────┘  └────────┘  └────────────┘  └──────────────┘     │  │    │
│  │  └─────────────────────────────────────────────────────────────────┘  │    │
│  │                                   │                                    │    │
│  │                                   ▼                                    │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │    │
│  │  │                    Rule Implementations                          │  │    │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │  │    │
│  │  │  │Required Field│  │ Text Rules   │  │Number Rules  │         │  │    │
│  │  │  │    Rule      │  │ (Min/Max)    │  │(Range/Type)  │         │  │    │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘         │  │    │
│  │  └─────────────────────────────────────────────────────────────────┘  │    │
│  │                                   │                                    │    │
│  │                                   ▼                                    │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │    │
│  │  │                 Marketplace Providers                            │  │    │
│  │  │                                                                  │  │    │
│  │  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │  │    │
│  │  │  │ Mercado Livre  │  │     Shopee     │  │     Amazon     │   │  │    │
│  │  │  │   Provider     │  │    Provider    │  │    Provider    │   │  │    │
│  │  │  │                │  │                │  │                │   │  │    │
│  │  │  │ • Title: 60ch  │  │ • Title: 100ch │  │ • Title: 200ch │   │  │    │
│  │  │  │ • Price > 0    │  │ • Weight req.  │  │ • ASIN/UPC     │   │  │    │
│  │  │  │ • Stock >= 0   │  │ • Square imgs  │  │ • Bullets req. │   │  │    │
│  │  │  └────────────────┘  └────────────────┘  └────────────────┘   │  │    │
│  │  │                                                                  │  │    │
│  │  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │  │    │
│  │  │  │     Magalu     │  │   Americanas   │  │   B2W/Others   │   │  │    │
│  │  │  │   Provider     │  │    Provider    │  │    Provider    │   │  │    │
│  │  │  │   (Planned)    │  │   (Planned)    │  │   (Planned)    │   │  │    │
│  │  │  └────────────────┘  └────────────────┘  └────────────────┘   │  │    │
│  │  └─────────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────────────┐
                        │   Data Flow Pipeline     │
                        └──────────────────────────┘
                                    │
                    1. Upload CSV   ▼
                        ┌──────────────────┐
                        │   Parse & Load    │
                        └──────────────────┘
                                    │
                    2. Select Rules ▼
                        ┌──────────────────┐
                        │  Load Provider    │
                        │  (Marketplace)    │
                        └──────────────────┘
                                    │
                    3. Validate     ▼
                        ┌──────────────────┐
                        │   Rule Engine     │
                        │  Execute Rules    │
                        └──────────────────┘
                                    │
                    4. Errors?      ▼
                        ┌──────────────────┐
                        │  Correction       │
                        │    Engine         │
                        └──────────────────┘
                                    │
                    5. Preview      ▼
                        ┌──────────────────┐
                        │  Show Results     │
                        │  & Corrections    │
                        └──────────────────┘
                                    │
                    6. Download     ▼
                        ┌──────────────────┐
                        │  Corrected CSV    │
                        └──────────────────┘
```

## 🚀 Features

### ✅ Implementado
- **Validação por Marketplace**: Regras específicas para Mercado Livre, Shopee, Amazon
- **Correção Automática**: Fixes inteligentes baseados em padrões do marketplace
- **Preview de Correções**: Visualize mudanças antes de aplicar
- **Arquitetura de Plugins**: Fácil adição de novos marketplaces e regras
- **API RESTful**: Endpoints bem definidos e documentados
- **Interface Web**: Upload drag-and-drop com feedback visual

### 🔄 Em Desenvolvimento
- **Processamento Assíncrono**: Para arquivos grandes (Celery + Redis)
- **Sistema de Templates**: Mapeamentos customizáveis por usuário
- **Batch Processing**: Streaming de CSVs grandes com chunks configuráveis
- **Dry-run Mode**: Preview de correções sem aplicar

## 📅 Roadmap

### ✅ Sprint Concluído
- [x] **T1**: Configurar monorepo com pnpm + Turborepo
- [x] **T2**: Implementar endpoint `/validate_csv` com validação síncrona
- [x] **T4**: Adicionar download de CSV corrigido
- [x] **Golden Tests**: Arquitetura completa de testes de regressão

### 🚧 Sprint Atual - Quick Wins
- [ ] **MarketplaceConfig Data-Driven**: Refatorar configurações para data classes
- [ ] **Classificador de Erros**: Sistema simples de classificação de erros
- [ ] **Integração Golden Tests**: Conectar com pipeline real

### 📋 Backlog Priorizado

#### Q1 2025
- [ ] **T3 - Processamento Assíncrono**: Celery + Redis para arquivos grandes
- [ ] **BatchSettings**: Processar CSVs em chunks configuráveis
- [ ] **PartialSuccessPolicy**: Modos fail_fast/continue/threshold

#### Q2 2025
- [ ] **T5 - Sistema de Templates**: UI para configurar mapeamentos
- [ ] **Dry-run Mode**: Preview completo sem efeitos colaterais
- [ ] **Reason Codes**: Catalogar e documentar todos os códigos de correção

#### Futuro
- [ ] **Novos Marketplaces**: Magalu, Americanas, B2W
- [ ] **API v2**: GraphQL com subscriptions
- [ ] **Machine Learning**: Correções preditivas baseadas em histórico

## 🛠️ Stack Tecnológica

### Frontend
- **Next.js 14** (App Router) + TypeScript
- **Tailwind CSS** + shadcn/ui components
- **Framer Motion** para animações
- **TanStack Query** para data fetching
- **React Hook Form** + Zod para validação

### Backend
- **FastAPI** (Python 3.11+)
- **Plugin Architecture** com interfaces bem definidas
- **Pandas** para manipulação de CSV
- **Pydantic** para validação de dados
- **PostgreSQL** (futuro) para persistência

### DevOps
- **pnpm** + Turborepo para monorepo
- **GitHub Actions** para CI/CD
- **Docker** para containerização
- **pytest** para testes backend
- **Vitest** para testes frontend

## 🏃‍♂️ Quick Start

### Pré-requisitos
- Node.js 20+
- Python 3.11+
- pnpm

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/drapala/validahub-new.git
cd validahub-new
```

2. **Instale as dependências**
```bash
pnpm install
```

3. **Configure o ambiente**
```bash
cp .env.example .env.local
```

4. **Inicie o desenvolvimento**
```bash
pnpm dev
```

Isso iniciará:
- Frontend em http://localhost:3001
- Backend em http://localhost:8000
- Documentação da API em http://localhost:8000/docs

## 📚 API Endpoints

### Validação
```http
POST /api/v1/validate_csv
Content-Type: multipart/form-data

Parameters:
- file: CSV file
- marketplace: MERCADO_LIVRE | SHOPEE | AMAZON | MAGALU | AMERICANAS
- category: ELETRONICOS | MODA | CASA | ESPORTE | BELEZA | etc
```

### Correção
```http
POST /api/v1/correct_csv
Content-Type: multipart/form-data

Parameters:
- file: CSV file
- marketplace: string
- category: string

Returns: Corrected CSV file
```

### Preview de Correções
```http
POST /api/v1/correction_preview
Content-Type: multipart/form-data

Parameters:
- file: CSV file
- marketplace: string
- category: string

Returns: JSON with corrections that would be applied
```

## 🧩 Adicionando Novos Marketplaces

1. **Crie um novo provider** em `/apps/api/src/rules/marketplaces/`
```python
from src.core.interfaces import IRuleProvider, IRule

class MeuMarketplaceProvider(IRuleProvider):
    def get_rules(self) -> List[IRule]:
        # Implemente suas regras
        pass
```

2. **Registre no validator** em `/apps/api/src/services/validator.py`
```python
elif marketplace == Marketplace.MEU_MARKETPLACE:
    from src.rules.marketplaces.meu import MeuMarketplaceProvider
    provider = MeuMarketplaceProvider()
```

3. **Adicione ao enum** em `/apps/api/src/schemas/validate.py`
```python
class Marketplace(str, Enum):
    # ...
    MEU_MARKETPLACE = "MEU_MARKETPLACE"
```

## 🧪 Testes

### Comandos Principais
```bash
# Rodar todos os testes
pnpm test

# Testes do backend
cd apps/api
pytest

# Testes do frontend
cd apps/web
pnpm test

# Golden Tests (testes de regressão)
make test-golden
make test-golden-ml      # Apenas Mercado Livre
make test-golden-shopee  # Apenas Shopee
```

### Golden Tests
Sistema de testes de regressão que compara outputs do pipeline com resultados esperados:
- Detecta mudanças não intencionais no comportamento
- Suporta diferentes marketplaces e categorias
- Gera HTML diffs visuais em caso de falha
- [Documentação completa](docs/testing/golden-tests.md)

## 📊 Métricas de Qualidade

- **Cobertura de Testes**: >80% (meta)
- **Performance**: <2s para arquivos até 10MB
- **Taxa de Correção**: >85% dos erros corrigíveis
- **Uptime**: 99.9% SLA

## 🔒 Segurança

O projeto segue as melhores práticas de segurança:
- Input validation com Pydantic
- Rate limiting (em desenvolvimento)
- CORS configurado
- Sanitização de dados
- Logs estruturados

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é proprietário e confidencial.

## 👥 Time

- **Backend & Arquitetura**: FastAPI + Plugin System
- **Frontend**: Next.js + React
- **DevOps**: CI/CD + Monitoring

---

**ValidaHub** - Transformando dados em vendas, uma validação por vez! 🚀