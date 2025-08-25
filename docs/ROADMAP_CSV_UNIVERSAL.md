# 🚀 Roadmap de Features - ValidaHub CSV Universal

> **Visão**: Transformar qualquer CSV em formatos otimizados para múltiplos marketplaces brasileiros, com validação inteligente e correção automática.

## 📊 Status Atual
- ✅ Infraestrutura base (API, Jobs, Storage)
- ✅ Testing Policy definida
- ✅ Glossário de Linguagem Ubíqua
- 🚧 Business logic com stubs
- ⏳ Exportadores multi-marketplace

---

## **Sprint 1 – Fundamento (Semana 1–2)**

🎯 **Objetivo**: Ter um fluxo end-to-end mínimo (upload → normalizar → exportar ML).

### Features
- [ ] Definir **UPC Schema v0.1** (Universal Product Catalog - superset de colunas canônicas)
- [ ] Criar **mapeador CSV→UPC** com salvamento por tenant
- [ ] Implementar **validações universais básicas**:
  - Preço > 0
  - SKU não vazio
  - Imagens presentes
- [ ] Exportador inicial **Mercado Livre** (colunas essenciais)
- [ ] Endpoint `/transform` + `/jobs/:id` com polling
- [ ] Relatório simples (`report.json`) listando erros/warnings

### Entregáveis Técnicos
```typescript
// UPC Schema v0.1
interface UniversalProductSchema {
  // Core fields (todos marketplaces)
  sku: string;
  title: string;
  description: string;
  price: decimal;
  stock: integer;
  brand: string;
  category: string;
  images: string[];
  
  // Metadata
  _source_row: number;
  _validation_status: 'valid' | 'warning' | 'error';
  _corrections_applied: string[];
}
```

### Critérios de Sucesso
- Upload CSV → Download CSV formatado para ML em < 30s
- Taxa de sucesso > 90% em CSVs bem formados
- Relatório claro de erros com linha/coluna

---

## **Sprint 2 – Ampliar Alcance (Semana 3–4)**

🎯 **Objetivo**: Cobrir 2 marketplaces e já ter diferencial real.

### Features
- [ ] Exportador **Amazon BR** (SP-API rules)
- [ ] Normalização de **título/descrição** com truncamento por destino
  - ML: máx 60 chars título
  - Amazon: máx 200 chars título
- [ ] **Namespace de campos específicos**:
  ```json
  {
    "ml_specific": { "listing_type": "gold_pro" },
    "amazon_specific": { "bullet_points": [...] }
  }
  ```
- [ ] Relatório de divergências por destino (warnings, auto-fixes)
- [ ] Salvar **mapping_id** para reuso (onboarding mais rápido)

### Entregáveis Técnicos
- Pipeline de transformação plugável
- Policies por marketplace
- Cache de mappings por tenant

### Critérios de Sucesso
- Export simultâneo ML + Amazon
- Reuso de mapping reduz tempo 50%
- Zero perda de dados críticos

---

## **Sprint 3 – Consolidação (Semana 5–6)**

🎯 **Objetivo**: Multi-market + detecção de conflitos.

### Features
- [ ] Exportador **Magalu** (subset inicial)
- [ ] Motor de **policies por destino**:
  - TitlePolicy (comprimento, chars especiais)
  - GTINPolicy (validação EAN/UPC)
  - ImagesPolicy (formato, dimensões)
- [ ] **Detector de conflitos**:
  - Interseção vazia → split automático
  - Avisos de incompatibilidade
- [ ] Relatório enriquecido:
  - Download ZIP com CSVs + README.md
  - Explicação de diferenças/adaptações
- [ ] Métricas por tenant:
  - Itens corrigidos
  - Erros recorrentes
  - Taxa de sucesso por marketplace

### Entregáveis Técnicos
```python
class ConflictResolver:
    def detect_conflicts(self, product: UPC, targets: List[Marketplace]):
        """
        Detecta quando um produto não pode ser
        exportado para múltiplos destinos simultaneamente
        """
        conflicts = []
        if product.price < 10 and 'AMAZON' in targets:
            conflicts.append("Amazon requer preço mínimo R$ 10")
        return conflicts
```

### Critérios de Sucesso
- 3 marketplaces funcionais
- Detecção proativa de 80%+ dos conflitos
- Relatório autoexplicativo (não precisa suporte)

---

## **Sprint 4 – Experiência & Growth (Semana 7–8)**

🎯 **Objetivo**: Tornar "produto SaaS" e facilitar vendas.

### Features
- [ ] Exportador **Americanas** (subset inicial)
- [ ] Assistente de categoria (heurística por título/brand)
  - ML de categorização baseado em histórico
  - Sugestões ranqueadas
- [ ] Auto-patches conservadores:
  - Normalização Unicode (ç→c se necessário)
  - Arredondar preços (9.99 → 10.00 se regra)
  - Truncar títulos preservando palavras
- [ ] UI/UX para preview:
  - Mapping visual drag-and-drop
  - Preview lado-a-lado (original vs transformado)
- [ ] **Landing page** com demo:
  - Upload exemplo.csv
  - Ver transformações em tempo real
  - Download samples

### Entregáveis Técnicos
- Widget embeddable de preview
- API de sugestões com cache Redis
- A/B testing na landing

### Critérios de Sucesso
- Conversão landing > 5%
- NPS > 40 em early adopters
- Redução 70% em tickets de suporte

---

## **Fase 2 – Expansão (após MVP validado)**

### Q1 2025
- [ ] **Shopee** (se demanda > 10 clientes)
- [ ] Auto-integradores por API (não só CSV)
  - Webhook ingestion
  - REST endpoints por marketplace
- [ ] Conectores diretos:
  - WooCommerce
  - Shopify
  - Bling/Tiny

### Q2 2025
- [ ] Webhooks para Jobs (async notifications)
- [ ] Billing real:
  - Stripe (cartão)
  - Boleto/Pix (Pagar.me)
  - Planos: Free (100 SKUs), Pro (10k), Enterprise (custom)
- [ ] Multi-idioma (EN, ES)

### Q3 2025
- [ ] Security & Compliance:
  - LGPD compliance badge
  - SOC2 Type 1
  - Auditoria completa de logs
- [ ] BI Dashboard:
  - Análise de erros recorrentes
  - Sugestões de otimização
  - Benchmarks por categoria

---

## 🎯 Estratégia Geral

### Princípios
1. **MVP realista** = 2 exportadores (ML + Amazon) + relatório claro
2. **União no schema**, regras aplicadas **por destino**
3. Sempre entregar **arquivo universal + CSVs específicos**
4. Ser **conservador nas correções** e **explícito nos relatórios**

### Métricas Norte
- **Ativação**: Upload → Export em < 5 min (first time)
- **Retenção**: 60% voltam na semana 2
- **Expansão**: 30% usam 2+ marketplaces
- **NPS**: > 50 após Sprint 4

### Tech Debt Aceitável (MVP)
- [ ] Processamento síncrono para < 1000 linhas
- [ ] Validações hardcoded (sem editor de regras)
- [ ] Storage local (sem S3 ainda)
- [ ] Monolito (sem microserviços)

### Tech Debt Inaceitável
- [ ] Sem testes nos fluxos principais
- [ ] Sem versionamento de schema
- [ ] Sem backup de dados originais
- [ ] Sem rate limiting

---

## 📝 Backlog Técnico Prioritário

### Semana 1
1. Implementar `UniversalProductSchema` com Pydantic
2. Criar `CSVMapper` com detecção automática de colunas
3. Implementar `MLExporter` com regras básicas
4. Setup testes E2E do fluxo completo

### Semana 2
1. Adicionar `AmazonExporter` com validações SP-API
2. Criar `PolicyEngine` extensível
3. Implementar `ConflictDetector`
4. Cache de mappings com Redis

### Ongoing
- Documentação de APIs com OpenAPI
- Testes de carga (k6/Locust)
- Monitoring com Sentry
- CI/CD com GitHub Actions

---

## 🚦 Go/No-Go Criteria para Produção

### Sprint 1 → Dev Preview
- [ ] 100 uploads processados com sucesso
- [ ] Tempo médio < 10s para 1000 linhas
- [ ] Zero data loss confirmado

### Sprint 2 → Beta Fechado
- [ ] 10 clientes beta ativos
- [ ] 2 marketplaces funcionais
- [ ] Uptime > 99%

### Sprint 4 → GA (General Availability)
- [ ] 100 clientes pagantes
- [ ] 4 marketplaces
- [ ] Documentação completa
- [ ] SLA 99.9%

---

## 📊 Recursos Necessários

### Time Mínimo
- 1 Backend Senior (Python/Node)
- 1 Frontend (React/Next)
- 1 Product Manager (part-time)
- 1 DevOps (part-time)

### Infraestrutura MVP
- 2 dynos Heroku ou EC2 t3.medium
- PostgreSQL (RDS ou Supabase)
- Redis (ElastiCache ou Upstash)
- S3 bucket (após Sprint 2)

### Budget Estimado
- Infra: R$ 500-1000/mês (MVP)
- Ferramentas: R$ 300/mês (Sentry, monitoring)
- Marketing: R$ 2000/mês (ads, content)

---

> 💡 **Próximos Passos**: 
> 1. Validar roadmap com stakeholders
> 2. Criar épicos no Jira/Linear
> 3. Definir squad e rituais
> 4. Kickoff Sprint 1

---

*Última atualização: Sprint Planning Q4 2024*