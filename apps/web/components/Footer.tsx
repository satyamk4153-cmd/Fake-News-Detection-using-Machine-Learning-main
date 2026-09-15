import React from 'react';
import { ShieldCheck, AlertCircle } from 'lucide-react';

interface FooterProps {
  onNavigate: (tab: 'analyze' | 'history' | 'models' | 'methodology' | 'admin') => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 mt-20 text-zinc-600 dark:text-zinc-400 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Ethical Disclaimer Callout */}
        <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 mb-10 flex items-start gap-3.5 shadow-sm">
          <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-500 shrink-0 mt-0.5" />
          <div className="text-xs leading-relaxed">
            <span className="font-semibold text-zinc-900 dark:text-white">Responsible AI & Verification Notice:</span>{' '}
            TruthLens is a statistical, machine-learning-assisted credibility analysis system. 
            Assessments reflect linguistic, structural, and benchmark patterns, not absolute factual truth. 
            The system explicitly isolates machine learning classifications, claim signals, and external citations. 
            All critical assertions should be verified with independent, primary journalistic and scientific sources.
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-7 h-7 rounded bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center text-white dark:text-zinc-900 font-bold text-xs">
                TL
              </div>
              <span className="font-bold text-zinc-900 dark:text-white text-base">
                TruthLens Platform
              </span>
            </div>
            <p className="text-xs leading-relaxed max-w-md text-zinc-500 dark:text-zinc-400">
              Open research architecture combining classical linear baselines, gradient boosting on linguistic features, 
              sequence transformer contextualization, and calibrated uncertainty modeling for transparent content analysis.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-900 dark:text-zinc-200 mb-3">
              Platform & Models
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <button onClick={() => onNavigate('analyze')} className="hover:text-zinc-900 dark:hover:text-white transition-colors">
                  Analysis Workspace
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('models')} className="hover:text-zinc-900 dark:hover:text-white transition-colors">
                  Production Models & Metrics
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('methodology')} className="hover:text-zinc-900 dark:hover:text-white transition-colors">
                  Analysis Methodology & Calibration
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-900 dark:text-zinc-200 mb-3">
              Standards & Security
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <span className="text-zinc-500">SSRF Safe Article Extraction</span>
              </li>
              <li>
                <span className="text-zinc-500">Dual Preprocessing Architecture</span>
              </li>
              <li>
                <span className="text-zinc-500">Calibrated Multi-Model Consensus</span>
              </li>
              <li>
                <span className="text-zinc-500">Zero Fabricated Citations</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-zinc-400 dark:text-zinc-500">
          <div>
            &copy; {new Date().getFullYear()} TruthLens Credibility Research. MIT Licensed open system.
          </div>
          <div className="flex items-center gap-6">
            <span>Deterministic Pipelines</span>
            <span>Platt & Isotonic Calibration</span>
            <span>English v1.0</span>
          </div>
        </div>

      </div>
    </footer>
  );
};
