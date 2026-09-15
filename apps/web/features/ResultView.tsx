'use client';

import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  ArrowLeft,
  Download,
  Share2,
  Printer,
  CheckCircle2,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  Info,
  Layers,
  Sparkles,
  BarChart3,
  Quote,
  Check,
} from 'lucide-react';
import { AnalysisResponse, HighlightSpan } from '../types';
import { api } from '../lib/api';

interface ResultViewProps {
  analysis: AnalysisResponse;
  onBack: () => void;
}

export const ResultView: React.FC<ResultViewProps> = ({ analysis, onBack }) => {
  const [copied, setCopied] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackUseful, setFeedbackUseful] = useState<boolean | null>(null);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [activeHighlightFilter, setActiveHighlightFilter] = useState<'all' | 'high' | 'medium'>('all');

  const pred = analysis.prediction;
  const expl = analysis.explanation;

  // Determine visual styling based on calibrated assessment
  const label = pred?.label || 'UNCERTAIN';
  const isCredible = label.includes('CREDIBLE');
  const isMisleading = label.includes('MISLEADING');
  const isUncertain = !isCredible && !isMisleading;

  const getStatusBadge = () => {
    if (isCredible) {
      return {
        bg: 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800',
        text: 'text-emerald-800 dark:text-emerald-300',
        icon: <ShieldCheck className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />,
        badge: 'bg-emerald-600 text-white',
        title: 'LIKELY CREDIBLE',
      };
    }
    if (isMisleading) {
      return {
        bg: 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800',
        text: 'text-rose-800 dark:text-rose-300',
        icon: <AlertTriangle className="w-6 h-6 text-rose-600 dark:text-rose-400" />,
        badge: 'bg-rose-600 text-white',
        title: 'LIKELY MISLEADING',
      };
    }
    return {
      bg: 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800',
      text: 'text-amber-800 dark:text-amber-300',
      icon: <HelpCircle className="w-6 h-6 text-amber-600 dark:text-amber-400" />,
      badge: 'bg-amber-600 text-white',
      title: 'UNCERTAIN / NEEDS VERIFICATION',
    };
  };

  const status = getStatusBadge();

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJSON = () => {
    const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `truthlens-analysis-${analysis.id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleFeedback = async (isUseful: boolean) => {
    try {
      await api.submitFeedback(analysis.id, {
        is_useful: isUseful,
        comment: feedbackComment || undefined,
      });
      setFeedbackUseful(isUseful);
      setFeedbackSent(true);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-16">
      
      {/* Top Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-200 dark:border-zinc-800 pb-4">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Analyze
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyLink}
            className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center gap-1.5 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Share2 className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Share'}
          </button>
          <button
            onClick={() => window.print()}
            className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center gap-1.5 transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />
            Print
          </button>
          <button
            onClick={handleDownloadJSON}
            className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Primary Assessment Banner */}
      <div className={`p-6 sm:p-8 rounded-2xl border ${status.bg} transition-all shadow-sm`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-white/80 dark:bg-zinc-900/80 shadow-xs border border-zinc-200/60 dark:border-zinc-700/60">
              {status.icon}
            </div>
            <div>
              <div className="flex items-center gap-2.5 mb-1.5">
                <span className="text-xs uppercase tracking-wider font-bold text-zinc-500 dark:text-zinc-400">
                  Model Consensus Assessment
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded font-mono font-semibold bg-zinc-200/70 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
                  Calibrated v1.0
                </span>
              </div>
              <h2 className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${status.text}`}>
                {status.title}
              </h2>
              <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-1 max-w-xl leading-relaxed">
                {pred?.summary}
              </p>
            </div>
          </div>

          {/* Calibrated Probability & Confidence Gauge */}
          <div className="flex sm:flex-row md:flex-col items-start md:items-end justify-between border-t md:border-t-0 md:border-l border-zinc-200/80 dark:border-zinc-800/80 pt-4 md:pt-0 md:pl-6 gap-3 shrink-0">
            <div className="text-left md:text-right">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
                Calibrated Credibility
              </span>
              <div className="text-3xl font-black text-zinc-900 dark:text-white font-mono mt-0.5">
                {((pred?.calibrated_probability || 0.5) * 100).toFixed(1)}%
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs">
              <div>
                <span className="text-zinc-500">Confidence:</span>{' '}
                <span className="font-semibold text-zinc-900 dark:text-white">
                  {pred?.confidence}% ({pred?.confidence_level})
                </span>
              </div>
              <span className="text-zinc-300 dark:text-zinc-700">|</span>
              <div>
                <span className="text-zinc-500">Model Agreement:</span>{' '}
                <span className={`font-semibold ${pred?.model_agreement === 'High' ? 'text-emerald-700 dark:text-emerald-400' : 'text-zinc-900 dark:text-white'}`}>
                  {pred?.model_agreement}
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Multi-Model Breakdown */}
      {pred?.model_scores && (
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-zinc-500" />
              Constituent Model Breakdown
            </h3>
            <span className="text-xs text-zinc-500">Individual Model Probabilities P(Credible)</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              { name: 'TF-IDF Logistic Regression', score: pred.model_scores.logistic_regression, desc: 'N-gram patterns & token distributions' },
              { name: 'Calibrated Linear SVM', score: pred.model_scores.linear_svm, desc: 'High-dimensional text boundary classification' },
              { name: 'HistGradientBoosting', score: pred.model_scores.gradient_boosting, desc: '20 engineered linguistic & structural signals' },
              { name: 'Transformer Classifier', score: pred.model_scores.transformer, desc: 'Contextual sequence embeddings' },
            ].map((m, idx) => {
              const s = m.score ?? 0.5;
              const pct = (s * 100).toFixed(1);
              return (
                <div key={idx} className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-200 block truncate">
                      {m.name}
                    </span>
                    <span className="text-[11px] text-zinc-400 block mt-0.5 line-clamp-1">
                      {m.desc}
                    </span>
                  </div>
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-xs font-mono font-bold mb-1.5">
                      <span className="text-zinc-500 text-[11px]">Score</span>
                      <span className="text-zinc-900 dark:text-white">{pct}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${s >= 0.65 ? 'bg-emerald-600' : s <= 0.35 ? 'bg-rose-600' : 'bg-amber-500'}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Influential Signals & Explainability */}
      {expl && (
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Supporting Credible Signals */}
          <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Signals Supporting Credibility
            </h4>
            {(expl?.supporting_signals ?? []).length > 0 ? (
              <ul className="space-y-2">
                {expl!.supporting_signals.map(([term, weight], idx) => (
                  <li key={idx} className="flex items-center justify-between text-xs py-1 px-2.5 rounded bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30">
                    <span className="font-mono text-zinc-800 dark:text-zinc-200 font-medium">"{term}"</span>
                    <span className="font-mono text-emerald-700 dark:text-emerald-400 font-bold">+{weight}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-zinc-400 italic">No significant positive credibility signals observed.</p>
            )}
          </div>

          {/* Signals Supporting Misleading Classification */}
          <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs">
            <h4 className="text-xs font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Signals Supporting Misleading Score
            </h4>
            {(expl?.counter_signals ?? []).length > 0 ? (
              <ul className="space-y-2">
                {expl!.counter_signals.map(([term, weight], idx) => (
                  <li key={idx} className="flex items-center justify-between text-xs py-1 px-2.5 rounded bg-rose-50/50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/30">
                    <span className="font-mono text-zinc-800 dark:text-zinc-200 font-medium">"{term}"</span>
                    <span className="font-mono text-rose-700 dark:text-rose-400 font-bold">-{weight}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-zinc-400 italic">No severe sensational or deceptive phrases observed.</p>
            )}
          </div>

        </section>
      )}

      {/* Interactive Phrase Highlighting */}
      {(expl?.highlighted_spans ?? []).length > 0 && (
        <section className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
                <Quote className="w-4 h-4 text-zinc-500" />
                Detected Linguistic Spans & Phrase Influence
              </h3>
              <p className="text-xs text-zinc-500 mt-0.5">
                Model attention spans. Highlighting indicates statistical influence on the model, not an objective truth verdict.
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-400 mr-1">Filter:</span>
              {(['all', 'high', 'medium'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setActiveHighlightFilter(f)}
                  className={`px-2.5 py-1 rounded text-xs capitalize font-medium transition-colors ${
                    activeHighlightFilter === f
                      ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 font-semibold'
                      : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-2 pt-2">
            {expl!.highlighted_spans
              .filter(s => activeHighlightFilter === 'all' || s.influence_level === activeHighlightFilter)
              .map((span, idx) => {
                const isMisleadingDir = span.direction === 'supports_misleading';
                return (
                  <div
                    key={idx}
                    className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs ${
                      isMisleadingDir
                        ? 'bg-rose-50 dark:bg-rose-950/30 border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300'
                        : 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-900 text-emerald-800 dark:text-emerald-300'
                    }`}
                  >
                    <span className="font-semibold underline decoration-dotted">"{span.text}"</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/70 dark:bg-black/30 font-medium">
                      {span.explanation}
                    </span>
                    <span className="text-[10px] font-mono font-bold uppercase opacity-75">
                      {span.influence_level}
                    </span>
                  </div>
                );
              })}
          </div>
        </section>
      )}

      {/* Extracted Claims Section */}
      {(analysis.claims ?? []).length > 0 && (
        <section className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-zinc-500" />
              Extracted Verifiable Claims ({analysis.claims.length})
            </h3>
            <span className="text-xs text-zinc-500">Segmented and ranked for independent verification</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-zinc-200 dark:border-zinc-800 text-zinc-400 font-semibold uppercase tracking-wider">
                  <th className="py-2.5 px-3">#</th>
                  <th className="py-2.5 px-3">Claim Assertion</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Priority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {analysis.claims.map((claim, idx) => (
                  <tr key={claim.claim_id || `claim-${idx}`} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
                    <td className="py-3 px-3 font-mono text-zinc-400 font-semibold">{idx + 1}</td>
                    <td className="py-3 px-3 font-medium text-zinc-800 dark:text-zinc-200 max-w-lg leading-relaxed">
                      {claim.text}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
                        {claim.claim_type}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        claim.verification_priority === 'High' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' : 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400'
                      }`}>
                        {claim.verification_priority}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Attributed Evidence References */}
      {(analysis.evidence ?? []).length > 0 ? (
        <section className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
              <ExternalLink className="w-4 h-4 text-zinc-500" />
              Attributed Reference Evidence ({analysis.evidence.length})
            </h3>
            <span className="text-xs text-zinc-500">Transparent citations from verified public registries</span>
          </div>

          <div className="space-y-3">
            {analysis.evidence.map((ev, idx) => (
              <div key={idx} className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 flex flex-col sm:flex-row items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-zinc-900 dark:text-white">
                      {ev.title}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                      ev.evidence_type === 'supporting'
                        ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300'
                        : ev.evidence_type === 'contradicting'
                        ? 'bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300'
                        : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300'
                    }`}>
                      {ev.evidence_type}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed max-w-3xl">
                    {ev.summary}
                  </p>
                  <div className="text-[11px] text-zinc-400 flex items-center gap-3 pt-1">
                    <span>Source: <strong className="text-zinc-600 dark:text-zinc-300">{ev.source_name}</strong></span>
                    {ev.publisher && <span>Publisher: {ev.publisher}</span>}
                  </div>
                </div>

                {ev.url && (
                  <a
                    href={ev.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 px-3 py-1.5 rounded-lg border border-zinc-300 dark:border-zinc-700 text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:bg-white dark:hover:bg-zinc-800 inline-flex items-center gap-1.5 transition-colors"
                  >
                    View Source
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>
      ) : (
        <section className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/40 shadow-xs space-y-2">
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-zinc-500" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
              External Knowledge Base Attribution
            </h3>
          </div>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
            No direct encyclopedic citations or public fact-check records were indexed for the specific entities in this submission. 
            TruthLens strictly does not fabricate mock citations when verified external records are unavailable. 
            Users should independently cross-verify these claims against primary journalistic and institutional archives.
          </p>
        </section>
      )}

      {/* Limitations Notice */}
      <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/60 flex items-start gap-3">
        <Info className="w-5 h-5 text-zinc-400 shrink-0 mt-0.5" />
        <div className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
          <strong className="text-zinc-900 dark:text-zinc-200">System Limitations:</strong> {pred?.limitations}
        </div>
      </div>

      {/* User Feedback Widget */}
      <section className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs">
        {feedbackSent ? (
          <div className="text-center py-4 text-xs font-medium text-emerald-700 dark:text-emerald-400 flex items-center justify-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            Thank you for your feedback. Responses are stored anonymously to monitor model drift and calibration quality.
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h4 className="text-xs font-bold text-zinc-900 dark:text-white uppercase tracking-wider">
                Was this credibility assessment helpful?
              </h4>
              <p className="text-xs text-zinc-500">
                Your feedback helps evaluate model uncertainty and identify out-of-distribution reporting styles.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleFeedback(true)}
                className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800 text-xs font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5 transition-colors"
              >
                <ThumbsUp className="w-3.5 h-3.5 text-emerald-600" />
                Yes
              </button>
              <button
                onClick={() => handleFeedback(false)}
                className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800 text-xs font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5 transition-colors"
              >
                <ThumbsDown className="w-3.5 h-3.5 text-rose-600" />
                No
              </button>
            </div>
          </div>
        )}
      </section>

    </div>
  );
};
