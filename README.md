# ValidaHub 🚀

[![CI/CD](https://github.com/drapala/validahub-new/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/drapala/validahub-new/actions)
[![codecov](https://codecov.io/gh/drapala/validahub-new/branch/main/graph/badge.svg)](https://codecov.io/gh/drapala/validahub-new)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-20+-green.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

**Intelligent CSV validation and correction for e-commerce.**  
ValidaHub processes large product catalogs asynchronously, applies marketplace-specific rules, and auto-corrects errors with full observability.

> *ValidaHub é uma plataforma escalável para validação e correção inteligente de planilhas CSV de e-commerce. Já integra Mercado Livre, Shopee e Amazon, com processamento assíncrono e telemetria completa.*

---

## 🎯 Key Features

- **Multi-Marketplace Validation**: Mercado Livre, Shopee, Amazon  
- **Intelligent Auto-Correction** with preview and selective application  
- **Asynchronous Processing** via Celery + Redis for large files  
- **Complete Telemetry** with structured events and metrics  
- **Repository Pattern** for data layer abstraction  
- **Centralized Logging** with correlation IDs  
- **Rate Limiting** via Redis  
- **Flexible Authentication** (JWT & API Keys)  

## 💡 Why ValidaHub?

ValidaHub isn't just another CSV validator. It's specifically designed for the unique challenges of Brazilian and Latin American e-commerce:

- **Marketplace-Specific Rules**: Deep understanding of Mercado Livre, Shopee, and Amazon's specific requirements
- **Intelligent Corrections**: Goes beyond validation - actually fixes common errors automatically
- **Enterprise-Grade Telemetry**: Full observability for debugging and performance monitoring
- **Scalable Architecture**: Handles files with millions of products without breaking a sweat
- **Brazilian Market Focus**: Built with Brazilian marketplace nuances in mind (tax codes, shipping rules, category mappings)

## 🛠️ Tech Stack

### Backend
- **FastAPI** (0.104+) - High-performance async web framework
- **Celery** (5.3+) - Distributed task queue
- **Redis** (7+) - Cache and message broker
- **PostgreSQL** (15+) - Primary database
- **SQLAlchemy** (2.0+) - Modern ORM with async support
- **Pydantic** (2.0+) - Data validation and settings
- **Pandas** (2.0+) - Efficient CSV manipulation

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** (5.0+) - Type safety
- **Tailwind CSS** (3.3+) - Utility-first styling
- **shadcn/ui** - Accessible component library
- **TanStack Query** (5.0+) - Powerful data synchronization

### DevOps & Testing
- **Docker** & **Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **pytest** (7.4+) - Backend testing with fixtures
- **Vitest** (1.0+) - Blazing fast frontend testing
- **codecov** - Code coverage tracking

## 🚀 Quick Start

### Prerequisites
```bash
# Required versions
Node.js 20+
Python 3.11+
Docker & Docker Compose
Redis 7+
PostgreSQL 15+
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/drapala/validahub-new.git
cd validahub-new
```

2. **Set up environment**
```bash
# Copy and adjust environment variables
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

3. **Start infrastructure services**
```bash
# Start PostgreSQL, Redis, and pgAdmin
docker-compose up -d

# Verify they're running
docker-compose ps
```

4. **Set up Backend**
```bash
cd apps/api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
alembic upgrade head

# Start the server
uvicorn src.main:app --reload --port 8000
```

5. **Set up Frontend**
```bash
# In another terminal
cd apps/web
npm install
npm run dev
```

6. **Start Celery Worker** (for async processing)
```bash
# In another terminal
cd apps/api
celery -A src.workers.celery_app worker --loglevel=info
```

### Access Points
- 🌐 Frontend: http://localhost:3001
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 🗄️ pgAdmin: http://localhost:5050

## 🏗️ Architecture

### Visual Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[Next.js Application]
        FE --> |REST API| API
    end
    
    subgraph "API Layer"
        API[FastAPI Gateway]
        API --> UC[Use Cases]
    end
    
    subgraph "Business Layer"
        UC --> SVC[Services]
        SVC --> |Validation| RE[Rule Engine]
        SVC --> |Storage| ST[Storage Service]
        SVC --> |Jobs| JS[Job Service]
        SVC --> |Events| TEL[Telemetry]
    end
    
    subgraph "Infrastructure Layer"
        RE --> REPO[Repositories]
        JS --> CEL[Celery Queue]
        ST --> S3[S3 Storage]
        REPO --> PG[(PostgreSQL)]
        CEL --> REDIS[(Redis)]
        TEL --> KAFKA[Event Stream]
    end
    
    style FE fill:#61dafb
    style API fill:#009485
    style PG fill:#336791
    style REDIS fill:#dc382d
```

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │   Upload   │  │    Jobs    │  │  Results   │  │ Settings │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                            REST API
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│                         API Layer                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /validate_csv  /correct_csv  /jobs  /validate_row        │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Use Cases Layer                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ValidateCsvUseCase  CorrectCsvUseCase  ValidateRowUseCase│  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Services Layer                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ JobService  RuleEngineService  StorageService  Telemetry │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Repositories  Queue(Celery)  Cache(Redis)  Storage(S3)   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📚 API Endpoints

### CSV Validation
```http
POST /api/v1/validate_csv
Content-Type: multipart/form-data

file: file.csv
marketplace: MERCADO_LIVRE | SHOPEE | AMAZON
category: ELETRONICOS | MODA | CASA
```

### CSV Correction
```http
POST /api/v1/correct_csv
Content-Type: multipart/form-data

file: file.csv
marketplace: string
category: string
auto_fix: boolean
```

### Async Jobs
```http
# Create job
POST /api/v1/jobs
{
  "type": "validate_csv",
  "params": {...}
}

# Check status
GET /api/v1/jobs/{job_id}

# List jobs
GET /api/v1/jobs?status=pending&limit=10
```

### Single Row Validation
```http
POST /api/v1/validate_row
{
  "row_data": {...},
  "marketplace": "MERCADO_LIVRE",
  "row_number": 1
}
```

## 🧪 Testing

```bash
# Backend tests
cd apps/api
pytest                    # Run all tests
pytest tests/unit        # Unit tests only
pytest tests/integration # Integration tests only
pytest --cov            # With coverage report

# Frontend tests
cd apps/web
npm test                # Run all tests
npm run test:watch     # Watch mode
npm run test:coverage  # With coverage report
```

## 📊 Telemetry and Monitoring

The system emits structured events for complete observability:

### Event Types
- **Validation Events**: `validation.started`, `validation.completed`, `validation.failed`
- **Job Events**: `job.created`, `job.started`, `job.completed`, `job.failed`
- **Performance Metrics**: Latency, throughput, error rate
- **System Events**: Health checks, rate limiting, authentication

### Example Event
```json
{
  "event": "validation.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "abc-123",
  "data": {
    "marketplace": "MERCADO_LIVRE",
    "rows_processed": 10000,
    "errors_found": 42,
    "processing_time_ms": 1250
  }
}
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/validahub

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Security
JWT_SECRET_KEY=your-secret-key
API_KEY_SALT=your-api-salt

# Storage
S3_BUCKET_NAME=validahub-files
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Telemetry
TELEMETRY_ENABLED=true
TELEMETRY_KAFKA_ENABLED=false
TELEMETRY_WEBHOOK_URL=https://your-webhook.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

## 📈 Roadmap

### 🚧 In Development
- [ ] Split JobService into specialized components (SOLID)
- [ ] Decouple from Celery (queue abstraction layer)
- [ ] Complete dependency injection implementation
- [ ] StorageAdapter for multiple backends (S3, GCS, Azure)

### 🎯 Q1 2025
- [ ] WebSocket support for real-time updates
- [ ] Metrics and analytics dashboard
- [ ] GraphQL API alongside REST
- [ ] Webhook notifications system

### 🔮 Future
- [ ] Machine Learning for predictive corrections
- [ ] Support for more marketplaces (Magalu, Americanas, B2W)
- [ ] Multi-tenant architecture
- [ ] API SDK for Python and Node.js

## 🤝 Contributing

We love contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. **Fork the project**
2. **Create a feature branch**
   ```bash
   git checkout -b feat/amazing-feature
   ```
3. **Make your changes**
   - Follow our code style (PEP 8 for Python, ESLint for TypeScript)
   - Write tests for new features
   - Update documentation as needed
4. **Run tests and linting**
   ```bash
   # Backend
   pytest && ruff check
   
   # Frontend
   npm test && npm run lint
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
6. **Push to your fork**
   ```bash
   git push origin feat/amazing-feature
   ```
7. **Open a Pull Request**

### Good First Issues

Check out our ["good first issue"](https://github.com/drapala/validahub-new/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label for beginner-friendly tasks!

### Conventions
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)
- **Branch Naming**: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`
- **Python**: PEP 8 + type hints
- **TypeScript**: ESLint + Prettier
- **Tests**: Required for all new features

## 📝 Documentation

- [Architecture Decision Records](docs/adr/)
- [Job System Documentation](apps/api/docs/JOB_SYSTEM.md)
- [Adapter Pattern Guide](apps/api/docs/ADAPTER_PATTERN.md)
- [API Reference](http://localhost:8000/docs)
- [Technical Debt Tracker](docs/tech-debt/audit.md)

## 🏆 Acknowledgments

Built with ❤️ by the ValidaHub team.  
Special thanks to all [contributors](https://github.com/drapala/validahub-new/graphs/contributors).

## 📄 License

Proprietary - All rights reserved © 2024 ValidaHub

---

<div align="center">
  <strong>ValidaHub</strong> - Transforming data into sales with intelligent validation 🚀
  <br>
  <sub>Made in Brazil 🇧🇷</sub>
</div>