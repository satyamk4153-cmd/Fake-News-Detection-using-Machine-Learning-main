# TruthLens Troubleshooting & Operations Guide

## Common Issues & Diagnoses

### 1. `ModelInferenceError: Model artifacts not found`
- **Cause**: The application was started before model weights and calibrated artifacts were generated.
- **Remedy**:
  ```bash
  python -m ml.training.train
  ```
  Verify that `ml/artifacts/ensemble_meta.joblib` exists.

---

### 2. `URLFetchError: Access to private, link-local, or loopback network address is forbidden`
- **Cause**: The submitted URL points to an internal network address (e.g. `http://127.0.0.1`, `http://192.168.1.1`, or `http://169.254.169.254`).
- **Remedy**: This is the expected behavior of the SSRF guardrail. Only publicly routable HTTP/HTTPS domains can be analyzed.

---

### 3. `ArticleExtractionError: Could not extract meaningful article text from webpage`
- **Cause**: The target page is paywalled, protected by aggressive CAPTCHA/bot-blockers, or rendered entirely via client-side JavaScript.
- **Remedy**: Copy the readable article body text directly from your browser and paste it into the **Full Article** tab of the Analysis Workspace.

---

### 4. `RateLimitError: Rate limit exceeded`
- **Cause**: Anonymous clients are limited to 15 requests/minute to protect ML inference resources.
- **Remedy**: Log in or register an account for higher quotas (60 req/min for authenticated users, 120 req/min for admins).
