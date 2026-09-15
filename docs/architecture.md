# TruthLens System Architecture

## Overview

TruthLens is a machine-learning-assisted news credibility assessment platform designed to evaluate news headlines, articles, and URLs. The system emphasizes transparency, multi-model consensus, explainability, and calibrated uncertainty modeling.

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

## Component Breakdown

### 1. Presentation Layer (`apps/web`)
- **Framework**: Next.js 14+ App Router, React 19, TypeScript.
- **Styling**: Tailwind CSS v4 with a restrained editorial palette (zinc/slate base with semantic emerald, amber, and rose indicators).
- **Key Modules**:
  - `AnalysisWorkspace`: Multi-input analysis interface (Article, Headline, URL).
  - `ResultView`: Calibrated verdict banner, model consensus meters, phrase highlighting, constituent model breakdown, claim ranking, and evidence attribution.
  - `HistoryView`: Filterable, searchable personal analysis history.
  - `ModelsView`: Dynamic performance dashboard reading holdout metrics directly from the model registry.
  - `MethodologyView`: Technical explanation of pipeline stages and ethical disclosures.
  - `AdminView`: Administrative control panel with telemetry, model promotion, and security audit logs.

### 2. API Gateway & Application Layer (`apps/api`)
- **Framework**: FastAPI with Pydantic v2 schemas and asynchronous execution.
- **Security & Middlewares**:
  - Request ID tracking via `X-Request-ID`.
  - Tiered rate limiting (anonymous, authenticated, administrative).
  - Strict SSRF protection on URL ingestion (DNS pre-resolution and RFC1918/metadata IP rejection).
  - JWT authentication with bcrypt password hashing (12 rounds).
- **Persistence**:
  - SQLAlchemy 2.0 Async ORM with SQLite (local development zero-friction mode) and PostgreSQL (`asyncpg`) support for production.

### 3. Machine Learning Subsystem (`ml/`)
- **Model 1**: TF-IDF Logistic Regression (word + character n-grams).
- **Model 2**: Calibrated Linear SVM (Platt scaling via `CalibratedClassifierCV`).
- **Model 3**: HistGradientBoostingClassifier trained on 20 engineered linguistic and structural features.
- **Model 4**: Contextual Sequence Transformer Classifier with temperature scaling.
- **Model 5**: Calibrated Multi-Model Ensemble using Isotonic Regression with out-of-distribution (OOD) deviation gating.

### 4. Explainability & Evidence Subsystem
- **Feature Weights**: Feature contribution analysis identifying top positive and negative vocabulary drivers.
- **Phrase Highlighting**: Dynamic phrase extraction tagging text spans with `high`, `medium`, or `low` influence levels.
- **Claim Extraction**: Sentence boundary segmentation detecting factual, numerical, causal, and attribution claims.
- **Evidence Attribution**: Contextual lookup associating claims with public verification registries without fabricated citations.
