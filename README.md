# ValidaHub (Frontend)

App web dark-first para validar e corrigir CSV/Sheets por marketplace×categoria.

## Stack

- Next.js 14 (App Router) + TypeScript
- Tailwind + shadcn-style (cards, table, form, dialog, toast)
- Framer Motion (micro-animações)
- TanStack Query (fetch/polling)
- react-hook-form + zod
- react-dropzone, @tanstack/react-virtual
- Auth via cookies httpOnly (`credentials: 'include'`)

## Rotas

Público:
- `/`, `/pricing`, `/docs`, `/status`, `/auth/login`, `/auth/register`

App (autenticado):
- `/upload`, `/results/[jobId]`, `/jobs`, `/connectors`, `/webhooks`, `/mappings`, `/settings/billing`

## Ambiente

1. Copie variáveis:
   - `cp .env.example .env.local`
2. Instale dependências:
   - `npm install`
3. Rode:
   - `npm run dev`

## Integração (assumido)

- `POST /auth/login` (cookie)
- `GET /status`
- `POST /validate_csv`
- `POST /upload/init`
- `POST /jobs`, `GET /jobs/:id`
- `POST /webhook/subscribe`
- `GET /rulesets`, `GET /diff`

## Próximos passos

- ResultsTable virtualizada (5k linhas).
- ApplyFixesBar com preview + download via signed URL.
- Conectores (S3/SFTP/Drive) e testes, WebhookForm com envio de teste.
- JsonEditor (lazy) com zod para `mapping.json`.
- Telemetria (PostHog): eventos `upload_started/completed`, `validate_done`, `job_created`, `results_viewed`, `download_clicked`, `apply_fixes_clicked`.
- A11y audit, LCP/CLS, CSP/SRI, banner “Rules updated”.