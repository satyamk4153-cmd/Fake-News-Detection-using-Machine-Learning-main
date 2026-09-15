# TruthLens — Security Engineering & Threat Audit

**Audit Date:** 2026-09-15  
**Auditor / Engineering Role:** Principal Security Engineer & Infrastructure Architect  
**Security Posture:** HARDENED & PRODUCTION-VERIFIED  
**Overall Security Grade:** A- (Enterprise Production Ready)  

---

## 1. Threat Model & Surface Analysis

TruthLens processes unauthenticated public text and arbitrary external URLs to evaluate news credibility. This creates several key attack vectors:
1. **Server-Side Request Forgery (SSRF):** Malicious URLs targeting internal cloud metadata (AWS `169.254.169.254`, GCP metadata), local loopback services (FastAPI, Redis, PostgreSQL), or intranet devices.
2. **Denial of Service (DoS / Resource Exhaustion):** Infinite redirect loops, gigantic content payloads (decompression bombs), slowloris connections, or recursive regex execution.
3. **Privilege Escalation & Horizontal Infiltration:** Insecure Direct Object References (IDOR) allowing users to view or delete another tenant's analyses.
4. **Secret Leakage:** Plaintext environment files (`.env`) or JWT signing keys stored in git or baked into container images.
5. **Container Escape / Root Exploits:** Docker containers executing processes as root (UID 0).

---

## 2. SSRF Protection Architecture & Verification Matrix

The URL extraction pipeline in `apps/api/app/services/url_extractor.py` enforces a defense-in-depth security perimeter.

### 2.1 Defense Mechanisms
* **Scheme Whitelisting:** Strictly permits `http` and `https`. Schemes such as `file://`, `ftp://`, `gopher://`, `dict://`, and `ldap://` are rejected at the parsing boundary.
* **DNS Resolution & IP Filtering:** Before initiating any HTTP request, the destination hostname is resolved to its IP addresses. Every resolved IP is evaluated against RFC 1918 (private networks), RFC 3927 (link-local), RFC 5735, and IPv6 loopback (`::1`, `fe80::/10`).
* **Cloud Metadata Protection:** Explicitly blocks AWS/GCP instance metadata endpoint `169.254.169.254`.
* **Bounded Resource Consumption:** Enforces `MAX_URL_REDIRECTS = 3`, `URL_REQUEST_TIMEOUT_SECONDS = 8`, and streaming byte cap `MAX_URL_CONTENT_BYTES = 5,242,880` (5 MB).

### 2.2 Automated SSRF Test Suite Results

All SSRF defenses are validated via `apps/api/tests/test_ssrf.py`:

| Test Vector | Input URL / Host | Expected Result | Automated Test Status |
| :--- | :--- | :--- | :---: |
| **Localhost IPv4** | `http://127.0.0.1:8000/secret` | Blocked (`InvalidUrlError`) | **PASS** |
| **Localhost Name** | `http://localhost/admin` | Blocked (`InvalidUrlError`) | **PASS** |
| **Private Subnet 10.x** | `http://10.0.0.1/internal` | Blocked (`InvalidUrlError`) | **PASS** |
| **Private Subnet 192.168.x** | `http://192.168.1.1/router` | Blocked (`InvalidUrlError`) | **PASS** |
| **Cloud Metadata** | `http://169.254.169.254/latest/meta-data` | Blocked (`InvalidUrlError`) | **PASS** |
| **Disallowed Protocol** | `file:///etc/passwd` | Blocked (`InvalidUrlError`) | **PASS** |
| **Public Valid HTTPS** | `https://example.com` | Allowed / Resolves normally | **PASS** |

---

## 3. Authentication, Authorization & Tenant Isolation

### 3.1 Cryptographic Controls
* **Password Hashing:** Bcrypt with 12 salt rounds (via `passlib.context.CryptContext`).
* **JWT Signing:** Cryptographic HMAC-SHA256 tokens carrying `sub` (user_id), `role` (`user` | `admin`), and expiration `exp` timestamps.
* **Secret Key Enforcement:** In production (`APP_ENV=production`), the application refuses to start if `SECRET_KEY` is missing or matches development placeholders.

### 3.2 Access Control & IDOR Prevention
* **Analysis Ownership:** Every persisted analysis is attributed to `user_id` or marked anonymous (`None`).
* **Strict Tenant Scoping:** Retrieval (`GET /analyses/{id}`) and deletion (`DELETE /analyses/{id}`) in `AnalysisService` verify that `analysis.user_id == requesting_user_id` or that the requester possesses the `admin` role. Cross-tenant access throws an explicit `AuthorizationError` (HTTP 403).
* **Automated Isolation Test:** Verified by `apps/api/tests/test_analysis.py::test_user_analysis_isolation_and_delete` (**PASS**).

---

## 4. Container & Infrastructure Security

### 4.1 Non-Root Container Execution
* Both `docker/Dockerfile.api` and `docker/Dockerfile.web` execute under unprivileged user identities:
  * Backend: `truthlens:truthlens` (UID:GID `1001:1001`).
  * Frontend: Node unprivileged execution mode.

### 4.2 Docker Compose Network Isolation
* Network segregation is enforced in `docker-compose.yml`:
  * `backend` bridge network: houses `db` (PostgreSQL) and `redis`. These ports are not exposed to the host machine.
  * `frontend` bridge network: bridges `api` and `web`.

### 4.3 Secret Hygiene & Repository Sanitation
* `.env` file permanently removed from version control and git history.
* `.gitignore` and `.dockerignore` updated with strict rules preventing accidental staging of `.env*` (preserving only `.env.example`), `.venv`, `truthlens.db`, and build caches.
* GitHub Actions CI pipeline enforces a dedicated `security-audit` job that aborts if `.env` is detected.

---

## 5. Rate Limiting & Denial of Service Defenses

* **Rate Limiting Middleware:** `apps/api/app/middleware/rate_limit.py` enforces sliding-window token limits:
  * Anonymous clients: 60 requests / min.
  * Authenticated users: 120 requests / min.
  * Admin accounts: 300 requests / min.
* **Input Sanitization:** Strips HTML/XSS payloads, enforces unicode normalization (`NFKC`), and caps maximum text size to 50,000 characters.
