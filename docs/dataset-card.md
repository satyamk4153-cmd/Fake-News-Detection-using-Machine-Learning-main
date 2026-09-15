# TruthLens Dataset Card — Benchmark Corpus v1.0

## Dataset Summary
- **Dataset Name**: `truthlens_credibility_benchmark`
- **Version**: `v1.0`
- **Language**: English (`en`)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Record Count**: 20 leakage-controlled verified articles across domains (economy, science, health, politics, history, conspiracy, and deceptive clickbait).

---

## Provenance & Sources
- **Credible Corpus**: Sourced from official institutional and peer-reviewed press releases (Reuters, Associated Press, Nature, WHO, NASA, Federal Reserve).
- **Misleading / Deceptive Corpus**: Sourced from documented debunked archives (PolitiFact, Snopes, ISOT Fake News benchmarks), covering 5G conspiracy theories, fake cancer cures, fabricated election fraud claims, and celebrity scam loops.

---

## Data Splits & Leakage Prevention
To prevent data leakage:
1. Deduplication was executed across body text and title hashes.
2. Dataset was strictly partitioned into **Train (70%)**, **Validation (15%)**, and **Test (15%)** splits **before** fitting vectorizers, scalers, or classifiers.
3. Vocabulary fitting was strictly restricted to training data.

Split Counts:
- Train: 14 records
- Validation: 3 records
- Test: 3 records
