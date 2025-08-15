# 📋 Plano de Implementação - Features Core

## Status Atual ✅
- Sistema de validação com rule engine YAML
- API REST funcional
- Frontend básico
- Auditoria de dívida técnica completa

## Features Prioritárias para MVP 🎯

### 1. **Jobs & Queue System** 🔄
```python
# Endpoints necessários
POST   /api/v1/jobs                 # Criar job
GET    /api/v1/jobs/{id}           # Status do job
GET    /api/v1/jobs/{id}/result    # Resultado
DELETE /api/v1/jobs/{id}           # Cancelar
GET    /api/v1/jobs                 # Listar jobs do usuário
```

**Stack**: Celery + Redis + PostgreSQL

### 2. **Conectores** 🔌
```python
# Marketplaces prioritários
- Mercado Livre API
- Shopee Seller Center
- Google Sheets
- CSV/Excel upload

# Endpoints
POST   /api/v1/connectors                    # Criar conexão
GET    /api/v1/connectors                    # Listar
POST   /api/v1/connectors/{id}/sync         # Sincronizar
DELETE /api/v1/connectors/{id}              # Remover
```

### 3. **Webhooks** 🪝
```python
# Eventos principais
- validation.completed
- correction.applied
- connector.synced
- job.status_changed

# Endpoints
POST   /api/v1/webhooks              # Criar webhook
GET    /api/v1/webhooks              # Listar
POST   /api/v1/webhooks/{id}/test   # Testar
DELETE /api/v1/webhooks/{id}        # Remover
```

### 4. **Mappings & Templates** 🗺️
```python
# Features
- Templates por marketplace/categoria
- Mapeamento de campos customizado
- Transformações (uppercase, format, etc)

# Endpoints
GET    /api/v1/mappings/templates           # Templates disponíveis
POST   /api/v1/mappings                     # Criar mapping
PUT    /api/v1/mappings/{id}               # Atualizar
GET    /api/v1/mappings/{marketplace}      # Por marketplace
```

### 5. **Billing & Subscriptions** 💳
```python
# Planos
Free:     100 validações/mês
Pro:      10k validações/mês ($49)
Business: 100k validações/mês ($299)
Enterprise: Ilimitado (custom)

# Endpoints
GET    /api/v1/billing/plans               # Planos disponíveis
POST   /api/v1/billing/subscribe          # Assinar plano
GET    /api/v1/billing/usage              # Uso atual
GET    /api/v1/billing/invoices           # Faturas
```

### 6. **Documentação** 📚
- API Docs com Swagger/OpenAPI
- Guias por marketplace
- SDKs Python/Node.js
- Postman collection

## Ordem de Implementação Sugerida 📅

### Fase 1: Infraestrutura (1 semana)
- [ ] Setup Celery + Redis
- [ ] Modelos de banco de dados
- [ ] Sistema de jobs básico
- [ ] Testes de integração

### Fase 2: Conectores (2 semanas)
- [ ] Abstração de conector base
- [ ] Conector Mercado Livre
- [ ] Conector Google Sheets
- [ ] UI de configuração

### Fase 3: Webhooks & Events (1 semana)
- [ ] Sistema de eventos
- [ ] Webhook delivery
- [ ] Retry logic
- [ ] UI de gerenciamento

### Fase 4: Billing (1 semana)
- [ ] Integração Stripe
- [ ] Gestão de planos
- [ ] Usage tracking
- [ ] Portal de billing

### Fase 5: Polish (1 semana)
- [ ] Documentação completa
- [ ] Dashboard analytics
- [ ] Onboarding flow
- [ ] Performance tuning

## Arquivos a Criar 📁

```
apps/api/src/
├── models/
│   ├── job.py
│   ├── connector.py
│   ├── webhook.py
│   ├── mapping.py
│   └── subscription.py
├── services/
│   ├── job_service.py
│   ├── connector_service.py
│   ├── webhook_service.py
│   ├── billing_service.py
│   └── mapping_service.py
├── workers/
│   ├── celery_app.py
│   ├── tasks.py
│   └── schedulers.py
├── connectors/
│   ├── base.py
│   ├── mercadolivre.py
│   ├── shopee.py
│   └── google_sheets.py
└── api/
    └── v1/
        ├── jobs.py
        ├── connectors.py
        ├── webhooks.py
        ├── mappings.py
        └── billing.py
```

## Decisões Técnicas 🔧

### Jobs & Queue
- **Celery** para processamento assíncrono
- **Redis** como broker e result backend
- **PostgreSQL** para persistência de jobs
- **Priority queues** para diferentes planos

### Conectores
- **OAuth2** para autenticação
- **Webhook** para sync em tempo real
- **Batch processing** para grandes volumes
- **Rate limiting** respeitando APIs

### Billing
- **Stripe** para pagamentos
- **Usage-based** + subscription híbrido
- **Webhooks** para eventos de billing
- **Portal self-service** para gestão

## KPIs de Sucesso 📊

### Técnicos
- Job success rate > 98%
- P95 latency < 500ms
- Webhook delivery > 99%
- Uptime > 99.9%

### Negócio
- 100+ clientes ativos em 3 meses
- MRR $10k em 6 meses
- Churn < 5%
- NPS > 50

## Riscos & Mitigações ⚠️

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Rate limits das APIs | Alto | Cache agressivo, batch processing |
| Volume de dados | Alto | Streaming, chunking, S3 storage |
| Custos de infra | Médio | Auto-scaling, usage limits |
| Complexidade de mappings | Médio | Templates pré-definidos, AI assist |

## Próximo Passo Imediato 🚀

```bash
# 1. Instalar dependências
cd apps/api
pip install celery redis stripe

# 2. Configurar Redis
docker run -d -p 6379:6379 redis:alpine

# 3. Criar migrations
alembic revision -m "Add jobs and connectors tables"

# 4. Implementar primeiro endpoint de jobs
# 5. Testar com CSV grande
```

---

**Objetivo Final**: Plataforma SaaS completa de validação e integração de dados para e-commerce, com foco em qualidade, performance e experiência do desenvolvedor.