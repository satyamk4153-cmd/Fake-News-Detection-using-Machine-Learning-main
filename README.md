# TruthLens — Production-Grade Fake News Detection & Credibility Analysis Platform

TruthLens is a machine-learning-assisted news credibility assessment platform designed to analyze news headlines, full articles, and public URLs. It produces transparent, calibrated credibility assessments:

- **Likely Credible**
- **Uncertain / Needs Verification**
- **Likely Misleading**

The system does **NOT** claim to determine absolute truth. It explicitly isolates:
1. Multi-model consensus classifications
2. Linguistic and structural rhetorical signals
3. Verifiable claim extraction
4. Transparent evidence attribution
5. Statistical uncertainty and calibrated confidence intervals

---

## 1. System Architecture

```
                        ┌─────────────────────┐
                        │      Frontend       │
                        │  Next.js 14+ / TS   │
                        └──────────┬──────────┘
                                   │
                              HTTPS / REST
                                   │
                        ┌──────────▼──────────┐
                        │     API Backend     │
                        │       FastAPI       │
                        └──────────┬──────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
               ▼                   ▼                   ▼
        ┌────────────┐      ┌─────────────┐     ┌────────────┐
        │ PostgreSQL │      │    Redis    │     │ ML Service │
        │  / SQLite  │      │  Rate/Cache │     │  Pipeline  │
        └────────────┘      └─────────────┘     └─────┬──────┘
                                                       │
                                      ┌────────────────┼───────────────┐
                                      │                │               │
                                      ▼                ▼               ▼
                               TF-IDF + Linear      Boosting      Transformer
                                  Models             Models          Model
                                      │                │               │
                                      └────────────────┼───────────────┘
                                                       ▼
                                             Ensemble / Calibration
                                                       │
                                                       ▼
                                             Explainability Layer
                                                       │
                                                       ▼
                                             Credibility Assessment
```

---

## 2. Technology Stack

- **Frontend**: Next.js 14+ (App Router), TypeScript, React 19, Tailwind CSS v4, Lucide Icons.
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), SQLite / PostgreSQL (`asyncpg`).
- **Machine Learning**: Scikit-learn, NumPy, Pandas, SciPy, Joblib.
- **Security**: SSRF URL guardrails (DNS resolution IP filtering), bcrypt password hashing (12 rounds), JWT tokens, sliding-window rate limiting.
- **Testing**: Pytest, Pytest-asyncio, HTTPX AsyncClient.
- **DevOps**: Docker, Docker Compose, GitHub Actions CI/CD.

---

## 3. Monorepo Structure

```text
truthlens/
├── apps/
│   ├── web/                          # Next.js frontend
│   │   ├── app/                      # Pages and layouts
│   │   ├── components/               # Navbar, Footer, AuthModal
│   │   ├── features/                 # AnalysisWorkspace, ResultView, HistoryView, ModelsView, AdminView
│   │   ├── lib/api.ts                # Typed API client
│   │   └── types/                    # Shared TypeScript interfaces
│   └── api/                          # FastAPI backend
│       ├── app/
│       │   ├── api/v1/               # Versioned routers (auth, analysis, models, claims, admin, health)
│       │   ├── core/                 # Config, security, SSRF filter, rate limiter, exceptions
│       │   ├── db/                   # Async session and Base
│       │   ├── models/               # SQLAlchemy ORM tables
│       │   ├── schemas/              # Pydantic request/response schemas
│       │   ├── services/             # Business logic & orchestration
│       │   └── main.py               # Application entrypoint
│       └── tests/                    # Backend API test suite
├── ml/
│   ├── datasets/                     # Dataset registry, benchmark curation, leakage prevention
│   ├── preprocessing/                # Dual preprocessing: traditional cleaner vs transformer tokenizer
│   ├── features/                     # 20 engineered linguistic & structural extractors
│   ├── models/                       # Logistic Regression, SVM, Boosting, Transformer, Ensemble
│   ├── training/                     # Reproducible training CLI (`python -m ml.training.train`)
│   ├── evaluation/                   # Evaluation suite (Accuracy, F1, Brier, ECE, Confusion Matrix)
│   ├── explainability/               # Token attribution, phrase highlighting, claims extractor
│   ├── inference/                    # Prediction CLI & production inference engine
│   └── artifacts/                    # Serialized models and evaluation reports
├── configs/                          # Model thresholds, training splits, application defaults
├── docs/                             # Complete documentation suite
│   ├── architecture.md
│   ├── api.md
│   ├── methodology.md
│   ├── security.md
│   ├── deployment.md
│   ├── troubleshooting.md
│   ├── model-card.md
│   ├── dataset-card.md
│   ├── ml-pipeline.md
│   └── decision-logic.md
├── docker/
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Install Dependencies & Train Models
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run reproducible training & calibration pipeline
python -m ml.training.train
```

### 2. Start Backend API Server
```bash
uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI documentation will be available at `http://127.0.0.1:8000/docs`.

### 3. Start Next.js Frontend
```bash
cd apps/web
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 5. Running Automated Tests

Run the full backend and ML test suite:
```bash
python -m pytest apps/api/tests ml/tests --verbose
```

Build the frontend production bundle:
```bash
cd apps/web
npm run build
```

---

## 6. Docker Deployment

Deploy full stack with Docker Compose:
```bash
docker compose up --build -d
```

Verify service health:
```bash
curl http://localhost:8000/api/v1/health/ready
```

---

## 7. Responsible AI & Limitations

- **Probabilistic Scoring**: TruthLens generates empirical probability distributions, not absolute determinations of truth.
- **Out-of-Distribution Guardrails**: Articles differing sharply in length, syntax, or vocabulary from journalistic standards trigger an explicit `Uncertain` status.
- **Attribution Transparency**: External evidence citations link directly to verified public and institutional registries. The system never fabricates citations.

For comprehensive details, refer to [docs/methodology.md](docs/methodology.md) and [docs/model-card.md](docs/model-card.md).
