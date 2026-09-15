'use client';

import React, { useState } from 'react';
import {
  FileText,
  Type,
  Link2,
  Sparkles,
  AlertCircle,
  Loader2,
  CheckCircle,
  ArrowRight,
  Shield,
  HelpCircle,
} from 'lucide-react';
import { api } from '../lib/api';
import { AnalysisResponse } from '../types';
import { ResultView } from './ResultView';

// Curated interactive samples for immediate user evaluation
const CREDIBLE_SAMPLE = {
  headline: "Federal Reserve Holds Benchmark Rates Steady Following Inflation Moderation",
  text: "The Federal Reserve concluded its policy meeting Wednesday by maintaining its benchmark interest rate in the target range of 5.25% to 5.50%. Federal Reserve officials stated that inflation has eased over the past year but remains slightly above the central bank's 2% objective. 'The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent,' the central bank noted in its official policy statement. Economic growth continues at a solid pace, with nonfarm payrolls expanding moderately and unemployment remaining at 3.9%. Financial analysts surveyed by major institutions anticipate potential rate adjustments later this year depending on incoming labor market metrics and consumer price indices."
};

const SENSATIONAL_SAMPLE = {
  headline: "BOMBSHELL: Secret Globalist Cabal Caught Poisoning Municipal Water with Mind-Control Nanochips!",
  text: "SHOCKING EXPOSED PROOF! Whistleblowers have finally leaked classified military documents proving that deep state elites and global billionaires are secretly installing 5G liquid nanotechnology into city water supplies across the nation! They want you sick and compliant! Doctors who tried to expose the horrifying truth have been mysteriously silenced and banned from social media! Look at what they are hiding from you! Wake up before it is too late! Share this breaking alert with everyone before the government blocks this page! It has been 100% proven that every major tap water source contains microscopic robotic transmitters activated by cell phone towers!"
};

interface AnalysisWorkspaceProps {
  onNavigateToMethodology: () => void;
}

export const AnalysisWorkspace: React.FC<AnalysisWorkspaceProps> = ({ onNavigateToMethodology }) => {
  const [inputType, setInputType] = useState<'article' | 'headline' | 'url'>('article');
  const [headline, setHeadline] = useState('');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);

  const charCount = inputType === 'url' ? url.length : text.length;
  const wordCount = inputType === 'url' ? 0 : (text.trim() ? text.trim().split(/\s+/).length : 0);

  const handleLoadSample = (sample: typeof CREDIBLE_SAMPLE) => {
    setInputType('article');
    setHeadline(sample.headline);
    setText(sample.text);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      setLoadingStage('Validating input parameters and verifying language...');

      let result: AnalysisResponse;
      if (inputType === 'url') {
        setLoadingStage('Connecting to source URL and enforcing SSRF security filters...');
        result = await api.analyzeURL(url);
      } else {
        setLoadingStage('Extracting linguistic, emotional, and structural signals...');
        result = await api.analyzeText({
          text,
          headline: headline || undefined,
          input_type: inputType,
        });
      }

      setLoadingStage('Finalizing calibrated assessment...');
      setCurrentAnalysis(result);
    } catch (err: any) {
      setError(err.message || 'An error occurred during credibility assessment.');
    } finally {
      setLoading(false);
      setLoadingStage('');
    }
  };

  if (currentAnalysis) {
    return (
      <ResultView
        analysis={currentAnalysis}
        onBack={() => setCurrentAnalysis(null)}
      />
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-10 animate-fadeIn">
      
      {/* Editorial Header */}
      <div className="text-center space-y-3 pt-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">
          <Shield className="w-3.5 h-3.5 text-zinc-500" />
          Probabilistic Credibility Intelligence
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-white">
          Assess News Credibility with Transparent Model Signals
        </h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto leading-relaxed">
          Analyze full news articles, standalone headlines, or public URLs. TruthLens evaluates linguistic discipline, 
          model consensus, and empirical claim structures without claiming absolute truth.
        </p>
      </div>

      {/* Quick Preload Sample Bar */}
      <div className="flex flex-wrap items-center justify-center gap-3 text-xs">
        <span className="text-zinc-400 font-medium">Quick Benchmarks:</span>
        <button
          type="button"
          onClick={() => handleLoadSample(CREDIBLE_SAMPLE)}
          className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-emerald-500 dark:hover:border-emerald-500 text-zinc-700 dark:text-zinc-300 transition-colors flex items-center gap-1.5 shadow-xs"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          Load Credible Sample (Federal Reserve)
        </button>
        <button
          type="button"
          onClick={() => handleLoadSample(SENSATIONAL_SAMPLE)}
          className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-rose-500 dark:hover:border-rose-500 text-zinc-700 dark:text-zinc-300 transition-colors flex items-center gap-1.5 shadow-xs"
        >
          <span className="w-2 h-2 rounded-full bg-rose-500" />
          Load Misleading Sample (Conspiracy Narrative)
        </button>
      </div>

      {/* Main Analysis Card */}
      <div className="p-6 sm:p-8 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm">
        
        {/* Input Mode Selector */}
        <div className="flex border-b border-zinc-200 dark:border-zinc-800 pb-5 mb-6 gap-2">
          {[
            { id: 'article', label: 'Full Article', icon: FileText },
            { id: 'headline', label: 'Headline Only', icon: Type },
            { id: 'url', label: 'Article URL', icon: Link2 },
          ].map((tab) => {
            const Icon = tab.icon;
            const isSelected = inputType === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => { setInputType(tab.id as any); setError(null); }}
                className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                  isSelected
                    ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 shadow-xs'
                    : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {error && (
          <div className="p-4 mb-6 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <div className="font-semibold">Analysis Notice</div>
              <div>{error}</div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          
          {inputType === 'url' ? (
            <div>
              <label className="block text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1.5">
                News Article URL
              </label>
              <div className="relative">
                <Link2 className="w-4 h-4 text-zinc-400 absolute left-3.5 top-3.5" />
                <input
                  type="url"
                  required
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.reuters.com/world/article-slug..."
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500 font-mono"
                />
              </div>
              <p className="text-[11px] text-zinc-500 mt-1.5">
                SSRF-safe parser. Localhost, RFC1918 private IPs, and cloud metadata targets are strictly blocked.
              </p>
            </div>
          ) : (
            <>
              {inputType === 'article' && (
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 dark:text-zinc-300 mb-1.5">
                    Headline (Optional)
                  </label>
                  <input
                    type="text"
                    value={headline}
                    onChange={(e) => setHeadline(e.target.value)}
                    placeholder="Enter the article title or headline..."
                    className="w-full px-3.5 py-2 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500"
                  />
                </div>
              )}

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-semibold text-zinc-700 dark:text-zinc-300">
                    {inputType === 'headline' ? 'Headline Text' : 'Article Body Content'}
                  </label>
                  <span className="text-[11px] text-zinc-400 font-mono">
                    {wordCount} words | {charCount} chars
                  </span>
                </div>
                <textarea
                  required
                  rows={inputType === 'headline' ? 3 : 7}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={
                    inputType === 'headline'
                      ? 'Paste headline to evaluate structural and emotional rhetoric...'
                      : 'Paste complete article body or statement text here for comprehensive multi-model assessment...'
                  }
                  className="w-full p-3.5 text-sm rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500 leading-relaxed font-sans"
                />
              </div>
            </>
          )}

          {/* Submit / Progress State */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-zinc-500">
              {loading ? (
                <div className="flex items-center gap-2 text-zinc-700 dark:text-zinc-300 font-medium animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin text-zinc-900 dark:text-white" />
                  <span>{loadingStage || 'Processing...'}</span>
                </div>
              ) : (
                <span>English text supported • Calibrated Isotonic Decision Layer</span>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || (inputType === 'url' ? !url.trim() : !text.trim())}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white dark:bg-zinc-100 dark:hover:bg-zinc-200 dark:text-zinc-900 text-sm font-semibold transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing Content...
                </>
              ) : (
                <>
                  Analyze Credibility
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>

        </form>

      </div>

      {/* Feature Explanatory Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs space-y-2">
          <div className="w-8 h-8 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-700 dark:text-zinc-300 font-bold text-xs">
            01
          </div>
          <h3 className="text-sm font-bold text-zinc-900 dark:text-white">
            Multi-Model Consensus
          </h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
            Combines TF-IDF linear baselines, gradient boosting on linguistic features, and sequence contextual representations.
          </p>
        </div>

        <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs space-y-2">
          <div className="w-8 h-8 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-700 dark:text-zinc-300 font-bold text-xs">
            02
          </div>
          <h3 className="text-sm font-bold text-zinc-900 dark:text-white">
            Calibrated Uncertainty
          </h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
            Scores falling into the ambiguous range [0.35, 0.65] or showing model disagreement explicitly yield 'Uncertain'.
          </p>
        </div>

        <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 shadow-xs space-y-2">
          <div className="w-8 h-8 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-700 dark:text-zinc-300 font-bold text-xs">
            03
          </div>
          <h3 className="text-sm font-bold text-zinc-900 dark:text-white">
            Claims & Attribution
          </h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
            Extracts verifiable factual, numerical, and causal claims with external references. Never fabricates citations.
          </p>
        </div>
      </div>

    </div>
  );
};
