# Auditoria de Dívida Técnica — Validahub

## Contexto & Escopo
Este relatório cobre todos os arquivos versionados do monorepo `validahub-new`, incluindo os serviços `apps/api` (FastAPI) e `apps/web` (Next.js/TypeScript). A análise contemplou arquitetura, código, testes, observabilidade, segurança e fluxo de CI/CD.

## Heatmap por Dimensão
| Dimensão | Nível (0-5) |
| --- | --- |
| Arquitetura | 3 |
| Código | 4 |
| Testes | 3 |
| Dados/Esquemas | 2 |
| API/Contratos | 3 |
| Observabilidade | 3 |
| CI/CD & DevEx | 3 |
| Segurança | 4 |
| Performance | 2 |
| Infra/Contêineres | 2 |
| Documentação | 3 |

## Top 10 Riscos + ROI
1. **Dependências Python vulneráveis** – `fastapi` 0.109.0 e `ecdsa` 0.19.1 expõem a aplicação a CVEs.
2. **Erros de tipagem no mypy** – ausência de stubs `types-PyYAML` e conflitos de módulo.
3. **Health checks e rate limit fictícios** – endpoints retornam sucesso sem validar infraestrutura.
4. **Frontend sem lint/type check** – ESLint e TypeScript falham por configuração incompleta.
5. **Módulo de validação monolítico** – arquivo `validation.py` com 668 LOC e endpoints duplicados.

## Quick Wins (≤48h)
- Atualizar dependências vulneráveis (`fastapi`, `python-jose`, `ecdsa`).
- Instalar `types-PyYAML` e ajustar pacotes para mypy.
- Criar `.eslintrc.json` e instalar `@types` necessários.

## Refactors Estruturais (1–2 semanas)
- Modularizar `apps/api/src/api/v1/validation.py`, removendo duplicações.
- Implementar health checks reais e rate limiting baseado em Redis.

