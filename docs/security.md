# TruthLens Security Architecture

## 1. Server-Side Request Forgery (SSRF) Protection

When users submit arbitrary URLs for analysis, TruthLens enforces strict validation before initiating any HTTP connection:

1. **Protocol Restriction**: Only `http://` and `https://` schemes are allowed. `file://`, `ftp://`, `gopher://`, etc., are rejected.
2. **DNS Pre-Resolution**: Hostnames are resolved to IP addresses via `socket.getaddrinfo`.
3. **IP Blacklisting & Filter Verification**:
   - Loopback: `127.0.0.0/8`, `::1`
   - RFC 1918 Private Ranges: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
   - Link-Local: `169.254.0.0/16`, `fe80::/10`
   - Cloud Metadata Service: `169.254.169.254`, `metadata.google.internal`
   - Internal Hostnames: `localhost`, `*.local`, `*.internal`, `kubernetes.default.svc`
4. **Redirect Enforcement**: Max 3 redirects followed manually; each intermediate hop's resolved IP is checked against the SSRF filter before connecting.
5. **Payload Bounds**: Maximum response payload of 5 MB (`MAX_URL_CONTENT_BYTES`).
6. **Timeouts**: Strict 8-second request timeout (`URL_REQUEST_TIMEOUT_SECONDS`).
7. **Content-Type Whitelisting**: Only `text/html` and `application/xhtml+xml` MIME types are accepted.

---

## 2. Authentication & Authorization Security

- **Password Hashing**: Passwords are salted and hashed using `bcrypt` (12 rounds). Plaintext passwords and hashes are never exposed through API responses or logs.
- **JWT Cryptography**: Signed using HMAC-SHA256 (`HS256`) with a configurable secret key (`SECRET_KEY`).
- **Role-Based Access Control (RBAC)**:
  - `USER`: May submit analyses, view their own analysis history, delete their own analyses, and submit feedback.
  - `ADMIN`: Has access to system-wide telemetry, model promotion/rollback endpoints, evaluation runs, and audit logs.
- **Data Isolation**: Database queries enforce user isolation; users cannot view, query, or delete analyses created by other accounts.

---

## 3. Rate Limiting & Denial of Service Defense

- Sliding-window in-memory rate limiting per client IP or authenticated user ID:
  - Anonymous requests: 15 requests / minute
  - Authenticated requests: 60 requests / minute
  - Administrative requests: 120 requests / minute
  - URL ingestion: 15 requests / minute

---

## 4. Input Sanitization & XSS Defense

- All incoming HTML is parsed with BeautifulSoup, stripping `<script>`, `<style>`, `<iframe>`, `<form>`, `<noscript>`, and inline event handlers before article extraction.
- React renders text safely without `dangerouslySetInnerHTML`.
