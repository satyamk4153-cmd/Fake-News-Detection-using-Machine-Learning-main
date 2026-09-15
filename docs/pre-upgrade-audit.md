# TruthLens — Pre-Upgrade Engineering Audit Report

**Document Status**: COMPLETED  
**Date**: 2026-09-15  
**Auditor**: Senior Systems, Security, and ML Architecture Team  
**Scope**: Full repository audit across backend, ML subsystem, web frontend, data layer, Docker/DevOps, and mobile client.

---

## 1. Executive Summary

This report establishes the baseline status of the existing TruthLens repository prior to hardening. While the repository presents a coherent end-to-end user experience and test passing rate for its baseline unit tests, a deep line-by-line inspection revealed significant architectural, security, and scientific issues that prevent it from being deemed production-ready without remediation.

---

## 2. Itemized Findings Matrix

### 2.1 What Works
- **FastAPI Routing & Envelope**: Uniform response envelope `{"success": true, "data": ..., "error": ..., "request_id": ...}` is consistently implemented.
- **SSRF Core IP Filtering**: IP blocking against loopback, RFC 1918, link-local, and AWS metadata address (`169.254.169.254`) is operational with 3-hop redirect controls.
- **User Data Isolation**: Object-level authorization tests verify that User A cannot query or delete User B's historical analysis.
- **Language Detection**: Custom stopword and script frequency heuristic rejects non-Latin scripts and non-English text with an explicit `UNSUPPORTED_LANGUAGE` domain error.
- **Next.js Production Compilation**: Web application builds cleanly with Next.js Turbopack and zero TypeScript errors.
- **Bcrypt Password Security**: Direct bcrypt password hashing with 12 salt rounds is active without insecure fallback methods.

### 2.2 What Fails / Bugs Identified
- **Unicode Corruption in Sequence Classifier**:
  - *Location*: `ml/models/transformer_classifier.py` (line 59)
  - *Issue*: Garbled character encoding `X悵 = X.T @ (y - 0.5)` caused by an unhandled UTF-8/CP1252 file write glitch.
  - *Impact*: Corrupted variable identifier; would fail execution during clean training on specific Python runtimes.
- **Forward Reference NameError in Common Schemas**:
  - *Location*: `apps/api/app/schemas/common.py`
  - *Issue*: `APIResponse` referenced `PaginationMeta` before `PaginationMeta` was declared in the file.
- **SSRF Evaluation Sequence**:
  - *Location*: `apps/api/app/core/ssrf.py`
  - *Issue*: Port validation preceded hostname blocklist evaluation, causing requests to internal ports (e.g., `localhost:8000`) to raise port restriction errors instead of private address blocks.

### 2.3 What Is Partially Implemented
- **Evidence Retrieval Subsystem**:
  - *Location*: `apps/api/app/services/evidence_service.py`
  - *Issue*: Does not actually query live external fact-checking or journalistic APIs. Instead, it matches keywords using hardcoded switch-case rules for 5 topics (Federal Reserve, JWST, WHO, 5G/Nanochips, Moon Landing) and returns hardcoded canned text snippets.
  - *Impact*: Inauthentic external verification; gives the false impression of real-time search when it is static pattern matching.
- **Database Migrations**:
  - *Location*: `apps/api/`
  - *Issue*: No Alembic migration configuration exists. The database relies on unmanaged startup reflection (`Base.metadata.create_all`).
  - *Impact*: Schema evolutions in production environments cannot be versioned or rolled back deterministically.
- **Administrative Telemetry**:
  - *Location*: `apps/api/app/services/admin_service.py`
  - *Issue*: Latency is hardcoded as `average_inference_latency_ms = 24.5` instead of being calculated dynamically from real analysis timestamps.
- **Docker Compose Topology**:
  - *Location*: `docker-compose.yml`
  - *Issue*: Only spins up SQLite and Web. It lacks a PostgreSQL service definition despite production documentation requiring PostgreSQL.

### 2.4 What Is Insecure
- **Secret-Bearing `.env` in Repository Archive**:
  - *Location*: `/.env`
  - *Issue*: A plaintext `.env` file containing `SECRET_KEY` was committed and tracked in the root repository. Furthermore, `.gitignore` failed to ignore `.env` directly.
  - *Remediation Required*: Immediate deletion of `.env`, updating `.gitignore`, sanitizing `.env.example`, and recommending key rotation.
- **Missing `.dockerignore`**:
  - *Location*: Repository root
  - *Issue*: No `.dockerignore` existed, causing local `.env`, `.venv`, local `truthlens.db`, and caches to be copied into Docker image builds.
- **Container Execution as Root**:
  - *Location*: `docker/Dockerfile.api`
  - *Issue*: Container runs as root without an unprivileged service user.
- **Rate Limiter Memory Growth**:
  - *Location*: `apps/api/app/core/rate_limiter.py`
  - *Issue*: Client IP dictionaries stored in memory without periodic eviction of stale keys, posing an unmonitored memory leak risk.

### 2.5 What Is Scientifically Questionable
- **Misleading Model Architecture Claims**:
  - *Location*: `ml/models/transformer_classifier.py`
  - *Issue*: The model is named `TruthLensTransformerClassifier` and uses version tag `distilbert-credibility-v1.0`. However, the code contains no PyTorch, no HuggingFace Transformers, and no transformer layers. It is a Bag-of-Words ridge linear regression with temperature scaling.
  - *Impact*: Falsely claiming deep transformer architecture when running a simple linear baseline is scientifically dishonest.
  - *Remediation*: Accurately document and rename the model as a `SequenceContextualClassifier` baseline with temperature calibration.
- **Dataset Sample Size**:
  - *Location*: `ml/datasets/loader.py`
  - *Issue*: The curated benchmark dataset contains only 20 samples (14 train, 3 validation, 3 test). With only 3 test samples, claiming 100% test accuracy is statistically fragile.
  - *Remediation*: Expand benchmark dataset to include a larger, diverse set of credible and deceptive journalistic samples.
- **Artificial Frontend Delays**:
  - *Location*: `apps/web/features/AnalysisWorkspace.tsx`
  - *Issue*: Uses `setTimeout(..., 200)` and `setTimeout(..., 150)` to artificially simulate progressive stages of ML processing.
  - *Remediation*: Remove fake delays; let actual network response time govern UI progress.

### 2.6 What Is Not Reproducible
- **Fresh Machine Python Setup**:
  - Direct installation into custom virtual environments on non-primary drives under Windows Application Control triggers DLL loading errors for scientific libraries (`bit_generator`). The setup instructions must clearly advise using the system Python or a standard Linux/Docker runtime.

### 2.7 Production Blockers
1. **Plaintext `.env` committed**: Must be purged from tracking and `.gitignore` updated.
2. **Missing `.dockerignore`**: Blocks containerized release.
3. **Hardcoded Evidence**: Must be replaced with genuine search queries or an honest empty state disclaimer.
4. **Corrupted Unicode in ML Model**: Must be fixed (`X悵` -> `X_y`).
5. **Absence of Alembic Migrations**: Must establish deterministic database versioning.
6. **Scientific Naming Discrepancies**: Must align model naming with genuine implemented architectures.

---

## 3. Baseline Quality Score

| Category | Score | Notes |
|---|:---:|---|
| Architecture | 11 / 15 | Good separation of concerns, but missing migration framework & real search service. |
| Frontend | 8 / 10 | Clean Next.js implementation; minor artificial `setTimeout` delays. |
| Backend | 11 / 15 | Solid FastAPI envelope and auth; needs latency query and Alembic. |
| ML Quality | 10 / 20 | Mathematically valid linear/boosting baselines, but transformer claim is inauthentic. |
| Security | 9 / 15 | Strong SSRF and bcrypt; penalized for committed `.env` and root Docker user. |
| Testing | 7 / 10 | 20 unit tests pass, but lacks end-to-end integration and negative security fuzzing. |
| DevOps | 5 / 10 | Missing `.dockerignore`, root Docker execution, no linting or secret scans in CI. |
| Documentation | 4 / 5 | Comprehensive documentation exists, but contained stale model claims. |
| **TOTAL** | **65 / 100** | **NOT PRODUCTION READY (Requires remediation)** |
