# TruthLens Methodology & Principles

## 1. Product Philosophy
TruthLens is positioned as a **machine-learning-assisted credibility assessment platform for analyzing potentially misleading news content**. It does NOT claim to determine absolute ontological truth.

In news verification, statistical classifiers detect linguistic signals, rhetorical anomalies, and source attribution patterns. TruthLens explicitly decouples:
1. Machine-learning classification probabilities
2. Source and domain indicators
3. Linguistic and structural signals
4. Claim-level evidence extraction
5. Calibration and uncertainty boundaries

---

## 2. Feature Engineering

The system extracts 20 engineered linguistic and structural features:

| Feature Name | Category | Significance |
|---|---|---|
| `word_count` | Structural | Total length metric for statistical reliability. |
| `sentence_count` | Structural | Used to compute sentence density. |
| `avg_sentence_length` | Structural | Syntactic complexity indicator. |
| `lexical_diversity` | Linguistic | Unique vocabulary ratio (Type-Token Ratio). |
| `uppercase_ratio` | Linguistic | Ratio of capital letters across the text. |
| `exclamation_density` | Linguistic | Exclamation marks per 100 words (sensationalism marker). |
| `question_density` | Linguistic | Rhetorical question density. |
| `punctuation_density` | Linguistic | Punctuation anomalies per 100 characters. |
| `emotional_word_density` | Rhetorical | Frequency of fear/shock/rage descriptors. |
| `sensational_word_density` | Rhetorical | Frequency of clickbait/conspiracy buzzwords ('bombshell', 'exposed'). |
| `modal_verb_density` | Linguistic | Frequency of speculative verbs ('might', 'allegedly'). |
| `first_person_density` | Linguistic | Personal narrative framing frequency ('I', 'we', 'our'). |
| `second_person_density` | Linguistic | Direct address framing ('you', 'your'). |
| `quote_count` | Attribution | Count of quotation marks indicating direct speech attribution. |
| `number_density` | Empirical | Frequency of digits and numerical quantities. |
| `attribution_count` | Journalistic | Named source indicators ('according to', 'officials said'). |
| `citation_count` | Academic | Formal publication or scientific references ('et al.', URLs). |
| `paragraph_count` | Structural | Document structure and formatting distribution. |
| `capitalized_word_anomalies` | Linguistic | Frequency of ALL-CAPS words (excluding acronyms). |
| `char_count` | Structural | Raw character span length. |

---

## 3. Probability Calibration
Raw model outputs (logits or uncalibrated sigmoid scores) can be overly confident. TruthLens utilizes **Isotonic Regression** fitted on holdout validation data to calibrate ensemble scores into true empirical probabilities $P(\text{Credible})$.

Calibration quality is measured using:
- **Brier Score**: $\frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$
- **Expected Calibration Error (ECE)**: Binning probabilities into intervals and measuring the weighted difference between average confidence and accuracy.

---

## 4. Uncertainty Modeling
The decision layer implements explicit thresholds documented in `configs/model/model_config.json`:
- **Uncertainty Band**: $[0.35, 0.65]$. Any score falling within this range produces `UNCERTAIN / NEEDS VERIFICATION`.
- **Model Divergence**: If the standard deviation across individual baseline predictions exceeds $0.22$, the agreement is tagged as `Low` and forces the assessment to `Uncertain`.
- **Out-of-Distribution (OOD)**: If the vocabulary mismatch and length deviation exceed $0.85$, the model flags high OOD and suppresses confident verdicts.
