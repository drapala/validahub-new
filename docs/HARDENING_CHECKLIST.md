# Hardening Audit Checklist - ValidaHub

> **Objetivo**: Garantir robustez, segurança e resiliência em produção  
> **Uso**: Para cada PR relevante, marque os itens aplicáveis e linke evidências

## 📊 Status
- **Owner**: `@drapala`
- **Última revisão**: `2025-08-25`
- **ADRs relacionadas**: [`ADR-006`](adr/ADR-006-anti-corruption-layer-pattern.md)

---

## ✅ Checklist de Segurança e Robustez

### 🔐 Segurança

- [ ] **JWT com algoritmo fixo (HS256/RS256)**
  - Risco: Algorithm confusion attack
  - Evidência: Validação restrita em `JWT_ALGORITHM`
  - Teste: Rejeitar algoritmos não esperados

- [ ] **Proteção contra path traversal**
  - Risco: Acesso não autorizado a arquivos
  - Evidência: Validação em `StorageService`
  - Teste: `../`, `%2e%2e/`, symlinks

- [ ] **YAML seguro (`safe_load`/`safe_dump`)**
  - Risco: Deserialização perigosa
  - Evidência: Uso consistente de safe APIs
  - Teste: Payloads maliciosos rejeitados

- [ ] **Headers de segurança HTTP**
  - Risco: Vulnerabilidades XSS/CSRF
  - Evidência: CSP, CORS, Referrer-Policy configurados
  - Teste: Scanner OWASP ZAP

### ⏱️ Tempo e Sincronização

- [ ] **Tempo monotônico para métricas**
  - Risco: Clock skew quebrando medições
  - Evidência: `time.monotonic()` em telemetria
  - Teste: Simular ajuste de relógio

- [ ] **Datetime timezone-aware (UTC)**
  - Risco: Bugs de timezone
  - Evidência: `datetime.now(timezone.utc)`
  - Teste: Serialização com TZ

### 🔄 Resiliência e Retry

- [ ] **Rate limiting com janela deslizante**
  - Risco: DDoS, estouro de memória
  - Evidência: Implementação com GC
  - Teste: Carga com múltiplos IPs

- [ ] **Backoff exponencial com jitter**
  - Risco: Thundering herd
  - Evidência: Jitter 50-150%
  - Teste: Distribuição estatística

- [ ] **Retry-After respeitado (429/503)**
  - Risco: Ban por retry agressivo
  - Evidência: Parser de segundos e HTTP-date
  - Teste: Contratos 429/503

- [ ] **Tratamento de CancelledError**
  - Risco: Recursos não liberados
  - Evidência: Try/finally em async
  - Teste: Cancel durante operações

### 📝 Validação e Parsing

- [ ] **Pydantic v2 com validação estrita**
  - Risco: Coerção silenciosa
  - Evidência: `@field_validator`, tipos estritos
  - Teste: Property-based (Hypothesis)

- [ ] **Parse robusto de JSON**
  - Risco: Crash em JSON inválido
  - Evidência: Try/except + validação
  - Teste: HTML/texto como resposta

- [ ] **UUID completo (sem truncar)**
  - Risco: Colisões
  - Evidência: Remoção de `[:8]`
  - Teste: Geração em massa

### 🏭 MELI ACL Específico

- [ ] **Enums como objetos (id/name)**
  - Risco: Validação incorreta
  - Evidência: Validação por `id`
  - Teste: Golden tests com fixtures

- [ ] **Mapeamento canônico completo**
  - Risco: Dados perdidos na transformação
  - Evidência: Testes de contrato
  - Teste: Fixtures reais do MELI

- [ ] **Tratamento de campos opcionais**
  - Risco: KeyError em produção
  - Evidência: `.get()` com defaults
  - Teste: Payloads mínimos/máximos

### 🎯 Performance e Async

- [ ] **Async I/O sem bloquear event loop**
  - Risco: Degradação de performance
  - Evidência: `asyncio.to_thread` para CPU-bound
  - Teste: Profiling de latência

- [ ] **Pool de conexões configurado**
  - Risco: Esgotamento de conexões
  - Evidência: Limites em DB/HTTP clients
  - Teste: Carga concorrente

### 📊 Observabilidade

- [ ] **Correlation ID consistente**
  - Risco: Tracing quebrado
  - Evidência: Propagação em SQS/HTTP
  - Teste: Round-trip do ID

- [ ] **Métricas de erro estruturadas**
  - Risco: Debugging difícil
  - Evidência: Códigos canônicos
  - Teste: Forçar diferentes erros

- [ ] **Health checks abrangentes**
  - Risco: Falsos positivos
  - Evidência: DB/Redis/S3 checks
  - Teste: Simular falhas parciais

### 🧪 Testes

- [ ] **Cobertura > 80%**
  - Evidência: Relatório coverage
  - Link: CI pipeline

- [ ] **Testes de resiliência (chaos)**
  - Evidência: Timeout/network failures
  - Teste: Monkey patching

- [ ] **Golden tests para transformações**
  - Evidência: Fixtures versionadas
  - Path: `tests/fixtures/`

- [ ] **Testes de carga/stress**
  - Evidência: Relatório de performance
  - Ferramenta: locust/k6

---

## 📋 Template de PR

```markdown
## Hardening Checklist
- [x] Segurança: JWT fixo, path traversal OK
- [x] Resiliência: Retry com backoff implementado
- [x] Validação: Pydantic v2 strict mode
- [x] Testes: Coverage 85%, chaos tests passando
- [ ] N/A: Rate limiting (não aplicável neste PR)

### Evidências
- Commit de segurança: abc123
- Testes de resiliência: def456
- Coverage report: [link]
```

---

## 🔗 Referências
- [ADR-006: Anti-Corruption Layer](adr/ADR-006-anti-corruption-layer-pattern.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [12 Factor App](https://12factor.net/)
- CI/CD: `.github/workflows/ci.yml`

---

**Última atualização**: 2025-08-25  
**Próxima revisão**: Antes do próximo major release