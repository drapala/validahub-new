# ENG-5: Integração do Rule Engine com apps/api

## 📋 Definition of Done (DoD)

### Objetivo
Integrar o rule engine desenvolvido (packages/rule-engine) com a API FastAPI (apps/api), substituindo a lógica de validação hardcoded atual por regras configuráveis via YAML.

### Critérios de Aceitação

#### ✅ Funcionalidades
- [ ] O endpoint `/validate_csv` usa o rule engine para validação
- [ ] Regras de validação são carregadas de arquivos YAML
- [ ] Mantém retrocompatibilidade com comportamento atual
- [ ] Suporta todos os marketplaces existentes (Mercado Livre, Shopee, Amazon, Magalu)
- [ ] Logs estruturados mostram execução das regras

#### ✅ Código & Arquitetura
- [ ] Service layer criado para abstrair rule engine (`RuleEngineService`)
- [ ] Dependency injection configurado no FastAPI
- [ ] Separação clara entre camadas (API → Service → Engine)
- [ ] Nenhuma lógica de negócio nos controllers
- [ ] Configurações externalizadas (path dos YAMLs)

#### ✅ Testes
- [ ] Cobertura de testes > 80% para novos códigos
- [ ] Testes unitários para `RuleEngineService`
- [ ] Testes de integração para endpoint atualizado
- [ ] Golden tests passando sem regressão
- [ ] Testes de carga validando performance

#### ✅ Documentação
- [ ] OpenAPI/Swagger atualizado
- [ ] README da API com instruções de uso do engine
- [ ] Exemplos de arquivos YAML de regras
- [ ] Comentários em código complexo

#### ✅ Performance
- [ ] Tempo de resposta < 2s para CSV de 1000 linhas
- [ ] Uso de memória estável (sem memory leaks)
- [ ] Cache de regras implementado

#### ✅ Observabilidade
- [ ] Logs estruturados com contexto (rule_id, row_num, field)
- [ ] Métricas de execução (regras aplicadas, tempo por regra)
- [ ] Tratamento de erros com mensagens claras

### Definição de Pronto
- [ ] Code review aprovado
- [ ] CI/CD pipeline verde
- [ ] Deploy em ambiente de staging testado
- [ ] Documentação atualizada
- [ ] Sem débitos técnicos críticos

### Out of Scope
- Novos endpoints (será feito em ENG-6)
- Processamento assíncrono (será feito em ENG-7)
- UI changes
- Novas regras de validação

### Riscos & Mitigações
- **Risco**: Breaking changes na API
  - **Mitigação**: Manter interface idêntica, apenas trocar implementação interna
  
- **Risco**: Performance degradation
  - **Mitigação**: Benchmark antes/depois, cache de regras compiladas

- **Risco**: Regras YAML malformadas
  - **Mitigação**: Validação de schema, fallback para regras default