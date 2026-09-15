'use client';

import React from 'react';
import {
  FileText,
  Layers,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Cpu,
  BookOpen,
  ArrowRight,
  Compass,
} from 'lucide-react';

export const MethodologyView: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: 'Input Validation & Unicode Normalization',
      desc: 'Content undergoes NFKC Unicode normalization, whitespace collapsing, and security sanitization. For URL inputs, a strict SSRF filter verifies DNS records against private RFC1918, link-local, and cloud metadata endpoints before fetching HTML with Readability heuristics.',
    },
    {
      num: '02',
      title: 'Language Detection & Guardrails',
      desc: 'Text is parsed through a statistical language detector. TruthLens v1.0 explicitly targets English content. Content in unsupported languages or containing fewer than 20 characters is routed to an explicit "Uncertain / Verification Required" state with descriptive guidance.',
    },
    {
      num: '03',
      title: 'Dual-Path Feature Extraction',
      desc: 'To preserve semantic context for neural representations while preparing linear models, we maintain two parallel preprocessing branches: traditional TF-IDF word/char n-grams and 20 engineered linguistic/structural metrics (emotional density, attribution markers, capitalization anomalies, lexical diversity).',
    },
    {
      num: '04',
      title: 'Multi-Model Baseline Classification',
      desc: 'Predictions are independently computed across four diverse architectures: (1) L2-regularized Logistic Regression, (2) Calibrated Linear SVM, (3) HistGradientBoosting on linguistic vectors, and (4) Contextual Sequence Transformer with temperature scaling.',
    },
    {
      num: '05',
      title: 'Probability Calibration & Consensus Modeling',
      desc: 'Raw scores are mapped into true empirical probabilities using isotonic regression. Model consensus is calculated using variance across model outputs: low variance yields High agreement, while divergence triggers uncertainty flags.',
    },
    {
      num: '06',
      title: 'Out-Of-Distribution (OOD) Scoring',
      desc: 'An empirical vocabulary and length deviation scorer tests whether the submission differs substantially from verified journalistic reference distributions. High OOD scores prevent falsely confident outputs.',
    },
    {
      num: '07',
      title: 'Uncertainty Decision Boundary',
      desc: 'Calibrated probabilities falling between 0.35 and 0.65, or cases where model agreement is Low or OOD is High, automatically resolve to "UNCERTAIN / NEEDS VERIFICATION". Only strong consensus pushes the assessment into "Likely Credible" or "Likely Misleading".',
    },
    {
      num: '08',
      title: 'Token Attribution & Phrase Highlighting',
      desc: 'Feature weights and sub-sentence perturbation scoring isolate spans that statistically drove model classifications. Highlighting is displayed with clear disclaimers that it represents model attention, not objective falsehood.',
    },
    {
      num: '09',
      title: 'Claim Extraction & Evidence Attribution',
      desc: 'The article is segmented into sentences, identifying and classifying factual, numerical, causal, and attribution claims. High-priority claims are cross-referenced with public registries, showing transparent source links without fabricated citations.',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-12 animate-fadeIn pb-12">
      
      {/* Editorial Title */}
      <div className="border-b border-zinc-200 dark:border-zinc-800 pb-6 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-semibold bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">
          <BookOpen className="w-3.5 h-3.5" />
          Technical Transparency & Principles
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
          TruthLens Analysis Methodology
        </h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed max-w-2xl">
          A machine-learning-assisted credibility framework designed for journalistic analysis. 
          TruthLens measures statistical signals, linguistic markers, and model agreement while communicating uncertainty.
        </p>
      </div>

      {/* Decision Logic Formula Box */}
      <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 shadow-xs space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
          <Compass className="w-4 h-4 text-zinc-500" />
          Assessment Decision Logic Architecture
        </h3>
        <div className="font-mono text-xs p-4 rounded-xl bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-300 space-y-1.5 overflow-x-auto">
          <div>Input Quality (Length &gt;= 20 chars, English Confirmed)</div>
          <div>&nbsp;&nbsp;+ Multi-Model Ensemble Raw Score (LR, SVM, Boosting, Transformer)</div>
          <div>&nbsp;&nbsp;+ Isotonic Probability Calibration: P(Credible)</div>
          <div>&nbsp;&nbsp;+ Model Agreement Variance (High, Medium, Low)</div>
          <div>&nbsp;&nbsp;+ Out-of-Distribution Deviation Scoring (OOD)</div>
          <div className="border-t border-zinc-300 dark:border-zinc-700 pt-1.5 text-zinc-900 dark:text-white font-bold">
            =&gt; Calibrated Output: [ LIKELY CREDIBLE | UNCERTAIN | LIKELY MISLEADING ]
          </div>
        </div>
        <p className="text-xs text-zinc-500 leading-relaxed">
          If P(Credible) &ge; 0.65 and agreement is High/Medium &rarr; <strong>LIKELY CREDIBLE</strong>.<br />
          If P(Credible) &le; 0.35 and agreement is High/Medium &rarr; <strong>LIKELY MISLEADING</strong>.<br />
          If 0.35 &lt; P &lt; 0.65, or agreement is Low, or OOD &ge; 0.85 &rarr; <strong>UNCERTAIN / NEEDS VERIFICATION</strong>.
        </p>
      </div>

      {/* 9-Step Pipeline Details */}
      <section className="space-y-6">
        <h2 className="text-lg font-bold text-zinc-900 dark:text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-zinc-500" />
          The Nine-Stage Analysis Pipeline
        </h2>

        <div className="space-y-4">
          {steps.map((step) => (
            <div
              key={step.num}
              className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs flex items-start gap-4"
            >
              <span className="font-mono font-black text-sm text-zinc-400 dark:text-zinc-500 shrink-0 mt-0.5">
                {step.num}
              </span>
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-zinc-900 dark:text-white">
                  {step.title}
                </h4>
                <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">
                  {step.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Known Limitations and Responsible AI */}
      <section className="p-6 rounded-2xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/50 dark:bg-amber-950/20 space-y-3">
        <h3 className="text-sm font-bold text-amber-900 dark:text-amber-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          Documented Limitations & Ethical Guidelines
        </h3>
        <ul className="text-xs text-amber-900/80 dark:text-amber-300/80 space-y-2 list-disc pl-4 leading-relaxed">
          <li>
            <strong>Probabilistic Nature:</strong> TruthLens models statistical patterns associated with verified reporting vs. sensational disinformation. Models cannot verify physical real-world facts autonomously.
          </li>
          <li>
            <strong>Satire & Opinion:</strong> Emotionally expressive commentary or parody may trigger sensational linguistic signals even if the author had no deceptive intent.
          </li>
          <li>
            <strong>Temporal Shifts:</strong> Breaking events that deviate from historical corpora may exhibit higher Out-of-Distribution scores until verified sources publish authoritative coverage.
          </li>
          <li>
            <strong>Human Verification:</strong> Important medical, legal, and financial assertions must always be corroborated by domain experts and independent primary sources.
          </li>
        </ul>
      </section>

    </div>
  );
};
