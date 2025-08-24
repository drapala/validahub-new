# ValidaHub 🚀

![CI/CD](https://github.com/drapala/validahub-new/workflows/CI%2FCD%20Pipeline/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Node](https://img.shields.io/badge/node-20-green.svg)
[![codecov](https://codecov.io/gh/drapala/validahub-new/branch/main/graph/badge.svg)](https://codecov.io/gh/drapala/validahub-new)

**ValidaHub** is an enterprise-grade intelligent CSV validation and correction platform for e-commerce. It offers asynchronous processing, advanced telemetry, and scalable architecture with support for multiple marketplaces.

## 🎯 Key Features

### ✅ In Production
- **Multi-Marketplace Validation**: Specific rules for Mercado Livre, Shopee, Amazon
- **Intelligent Auto-Correction**: Correction system with preview and selective application
- **Asynchronous Processing**: Job queue with Celery + Redis for large files
- **Complete Telemetry**: Structured events, metrics, and observability
- **Repository System**: Abstract data layer with Repository pattern
- **Centralized Logging**: Unified logging system with correlation IDs
- **Rate Limiting**: Abuse protection with Redis-backed rate limiting
- **Flexible Authentication**: Support for JWT and API Keys

### 🚀 Current Architecture

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

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **Celery** - Asynchronous task processing
- **Redis** - Cache and message broker
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation and settings
- **Pandas** - Efficient CSV manipulation

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **TanStack Query** - Data fetching and caching

### DevOps
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **pytest** - Backend testing
- **Vitest** - Frontend testing

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
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

## 📚 Main API Endpoints

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
# Backend
cd apps/api
pytest                    # All tests
pytest tests/unit        # Unit tests only
pytest tests/integration # Integration tests only
pytest --cov            # With coverage

# Frontend
cd apps/web
npm test                # All tests
npm run test:watch     # Watch mode
npm run test:coverage  # With coverage
```

## 📊 Telemetry and Monitoring

The system emits structured events for complete observability:

- **Validation Events**: `validation.started`, `validation.completed`, `validation.failed`
- **Job Events**: `job.created`, `job.started`, `job.completed`, `job.failed`
- **Performance Metrics**: Latency, throughput, error rate
- **System Events**: Health checks, rate limiting, authentication

## 🔧 Advanced Configuration

### Main Environment Variables

```env
# API
DATABASE_URL=postgresql://user:pass@localhost:5432/validahub
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
JWT_SECRET_KEY=your-secret-key
S3_BUCKET_NAME=validahub-files

# Telemetry
TELEMETRY_ENABLED=true
TELEMETRY_KAFKA_ENABLED=false
TELEMETRY_WEBHOOK_URL=https://your-webhook.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

## 📈 Roadmap

### In Development
- [ ] Split JobService into specialized components
- [ ] Decouple from Celery (queue generalization)
- [ ] Complete dependency injection
- [ ] StorageAdapter for multiple backends

### Planned
- [ ] WebSocket support for real-time updates
- [ ] Metrics and analytics dashboard
- [ ] GraphQL API
- [ ] Machine Learning for predictive corrections
- [ ] Support for more marketplaces (Magalu, Americanas, B2W)

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

### Conventions
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- Python code follows PEP 8
- TypeScript follows ESLint config
- Tests are required for new features

## 📝 Documentation

- [Detailed Architecture](docs/architecture/ARCHITECTURE.md)
- [Job System](apps/api/docs/JOB_SYSTEM.md)
- [Adapter Pattern](apps/api/docs/ADAPTER_PATTERN.md)
- [Technical Debt](docs/tech-debt/audit.md)

## 📄 License

Proprietary - All rights reserved © 2024 ValidaHub

---

**ValidaHub** - Transforming data into sales with intelligent validation 🚀