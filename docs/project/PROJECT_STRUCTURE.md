# ValidaHub Project Structure

## 📁 Directory Organization

```
validahub-new/
│
├── 📱 apps/                      # Monorepo applications
│   ├── api/                      # Backend (FastAPI)
│   │   ├── src/                  # Source code
│   │   │   ├── api/              # API endpoints
│   │   │   ├── core/             # Core business logic
│   │   │   │   ├── engines/      # Rule and correction engines
│   │   │   │   ├── interfaces/   # Abstract interfaces
│   │   │   │   └── pipeline/     # Validation/correction pipelines
│   │   │   ├── db/               # Database configuration
│   │   │   ├── models/           # SQLAlchemy models
│   │   │   ├── rules/            # Validation rules
│   │   │   │   ├── base/         # Base rule implementations
│   │   │   │   └── marketplaces/ # Marketplace-specific rules
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   └── services/         # Business services
│   │   ├── tests/                # Backend tests
│   │   ├── alembic/              # Database migrations
│   │   └── requirements.txt      # Python dependencies
│   │
│   └── web/                      # Frontend (Next.js)
│       ├── src/                  # Source code
│       │   ├── components/       # React components
│       │   ├── lib/              # Utilities
│       │   └── app/              # Next.js app router
│       ├── public/               # Static assets
│       └── package.json          # Node dependencies
│
├── 📝 docs/                      # Documentation
│   ├── api/                      # API documentation
│   ├── database-setup.md         # Database guide
│   └── testing/                  # Testing documentation
│       └── golden-tests.md       # Golden tests guide
│
├── 🧪 tests/                     # Test infrastructure
│   └── golden/                   # Golden test framework
│       ├── config_schema.py      # Test configuration
│       ├── normalizers.py        # Data normalization
│       ├── comparators.py        # Comparison logic
│       ├── golden_runner.py      # Test runner
│       ├── conftest.py           # Pytest configuration
│       └── {marketplace}/        # Test cases per marketplace
│           └── {category}/
│               └── case_xxx/
│                   ├── input.csv
│                   ├── expected_output.csv
│                   └── config.yaml
│
├── 🔧 scripts/                   # Utility scripts
│   ├── db.sh                     # Database management
│   └── init.sql                  # Initial DB setup
│
├── 🐳 Docker files               # Container configuration
│   ├── docker-compose.yml        # Service orchestration
│   └── Dockerfile                # (future) App container
│
├── ⚙️ Configuration files        # Project configuration
│   ├── .env.example              # Environment template
│   ├── .gitignore                # Git ignore rules
│   ├── Makefile                  # Common commands
│   ├── package.json              # Root package.json
│   ├── pnpm-workspace.yaml       # Monorepo config
│   ├── tsconfig.base.json        # TypeScript base config
│   └── turbo.json                # Turborepo config
│
├── 📚 Documentation files        # Project docs
│   ├── README.md                 # Main documentation
│   ├── BACKLOG.md                # Product backlog
│   ├── ARCHITECTURE.md           # System architecture
│   ├── API_AUDIT.md              # API security audit
│   ├── CLAUDE.md                 # AI assistant instructions
│   ├── PROJECT_STRUCTURE.md     # This file
│   ├── PRAGMATIC_REFACTORING_PLAN.md  # Refactoring strategy
│   └── BRANCHLESS_REFACTORING_PLAN.md # Branchless analysis
│
└── 🗑️ Generated/Temp            # Not in git
    ├── .next/                    # Next.js build
    ├── .turbo/                   # Turborepo cache
    ├── node_modules/             # Node dependencies
    └── __pycache__/              # Python cache
```

## 🎯 Organization Principles

### 1. **Monorepo Structure**
- Each app in `apps/` is independent but shares common configs
- Root manages shared dependencies and scripts

### 2. **Clear Separation**
- **Source Code**: In `apps/*/src/`
- **Tests**: Colocated with code + global test infrastructure in `/tests/`
- **Documentation**: Centralized in `/docs/`
- **Configuration**: Root level for shared, app level for specific

### 3. **Naming Conventions**
- **Files**: `snake_case.py` for Python, `kebab-case.ts` for TypeScript
- **Directories**: `lowercase` or `kebab-case`
- **Components**: `PascalCase` for React components
- **Documentation**: `UPPERCASE.md` for important docs

## 🧹 Cleanup Suggestions

To better organize the project:

1. **Move documentation**:
   ```bash
   mkdir -p docs/architecture docs/planning
   mv ARCHITECTURE.md docs/architecture/
   mv API_AUDIT.md docs/architecture/
   mv PRAGMATIC_REFACTORING_PLAN.md docs/planning/
   mv BRANCHLESS_REFACTORING_PLAN.md docs/planning/
   ```

2. **Group configuration**:
   ```bash
   mkdir config
   # Move non-critical configs to config/
   ```

3. **Create workspace docs**:
   ```bash
   mkdir -p docs/workspace
   mv CLAUDE.md docs/workspace/
   ```

## 📋 Quick Navigation

### For Developers
- Backend code: `apps/api/src/`
- Frontend code: `apps/web/src/`
- Database models: `apps/api/src/models/`
- API endpoints: `apps/api/src/api/`

### For Testing
- Run tests: `make test-golden`
- Add test case: `tests/golden/{marketplace}/{category}/`
- Test docs: `docs/testing/golden-tests.md`

### For DevOps
- Docker setup: `docker-compose.yml`
- Database: `./scripts/db.sh`
- CI/CD: `.github/workflows/`

### For Documentation
- API docs: http://localhost:8000/docs (when running)
- Project docs: `/docs/`
- Architecture: `ARCHITECTURE.md`

## 🚀 Common Commands

```bash
# Start everything
./scripts/db.sh up && pnpm dev

# Database management
./scripts/db.sh [up|down|shell|status]

# Run tests
make test-golden

# Build project
pnpm build

# Clean everything
docker-compose down -v
rm -rf node_modules .next .turbo
```