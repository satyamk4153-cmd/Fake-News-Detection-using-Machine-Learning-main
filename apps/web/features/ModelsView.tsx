'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, Shield, RefreshCw, Layers, Database, ArrowUpRight, Loader2 } from 'lucide-react';
import { api } from '../lib/api';
import { ModelVersionData } from '../types';

export const ModelsView: React.FC = () => {
  const [models, setModels] = useState<ModelVersionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getModels();
      setModels(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch registered models.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-10 animate-fadeIn">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-zinc-200 dark:border-zinc-800 pb-5">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-semibold bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 mb-2 border border-zinc-200 dark:border-zinc-700">
            <Cpu className="w-3.5 h-3.5" />
            Registry & Benchmark Verification
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
            Registered Machine Learning Models
          </h2>
          <p className="text-xs text-zinc-500 mt-1 max-w-2xl leading-relaxed">
            Directly populated from holdout test split evaluations. TruthLens does not hard-code fictional accuracy figures; 
            all metrics displayed reflect real statistical evaluations computed during training pipeline execution.
          </p>
        </div>

        <button
          onClick={fetchModels}
          disabled={loading}
          className="px-3.5 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-xs font-semibold text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="py-24 text-center flex flex-col items-center justify-center gap-3 text-zinc-400">
          <Loader2 className="w-7 h-7 animate-spin" />
          <span className="text-xs font-medium">Querying model registry...</span>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs">
          {error}
        </div>
      ) : models.length === 0 ? (
        <div className="py-20 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl p-8">
          <Cpu className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mx-auto mb-2" />
          <h4 className="text-sm font-bold text-zinc-900 dark:text-white">No models registered</h4>
          <p className="text-xs text-zinc-500 mt-1 max-w-sm mx-auto">
            Execute the reproducible training command in the terminal to train and evaluate all models:
            <code className="block mt-2 font-mono p-2 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200">
              python -m ml.training.train
            </code>
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {models.map((model) => {
            const m = model.metrics;
            const isProd = model.status === 'PRODUCTION';

            return (
              <div
                key={model.id}
                className={`p-6 rounded-2xl border bg-white dark:bg-zinc-900 shadow-xs flex flex-col justify-between space-y-6 transition-all ${
                  isProd
                    ? 'border-zinc-900 dark:border-zinc-400 ring-1 ring-zinc-900 dark:ring-zinc-400'
                    : 'border-zinc-200 dark:border-zinc-800'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[11px] font-mono text-zinc-400">
                      {model.version_tag}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        isProd
                          ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                          : 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400'
                      }`}
                    >
                      {model.status}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-zinc-900 dark:text-white">
                    {model.model_type}
                  </h3>

                  {m && (
                    <div className="mt-4 grid grid-cols-3 gap-2 border-y border-zinc-100 dark:border-zinc-800 py-3">
                      <div>
                        <span className="text-[10px] text-zinc-400 uppercase font-semibold block">Accuracy</span>
                        <span className="text-sm font-bold font-mono text-zinc-900 dark:text-white">
                          {(m.accuracy * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-zinc-400 uppercase font-semibold block">F1-Score</span>
                        <span className="text-sm font-bold font-mono text-zinc-900 dark:text-white">
                          {m.f1.toFixed(3)}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-zinc-400 uppercase font-semibold block">Brier Score</span>
                        <span className="text-sm font-bold font-mono text-zinc-900 dark:text-white">
                          {m.brier_score.toFixed(4)}
                        </span>
                      </div>
                    </div>
                  )}

                  {m && (
                    <div className="mt-3 space-y-1.5 text-xs text-zinc-500">
                      <div className="flex justify-between">
                        <span>Expected Calibration Error (ECE):</span>
                        <span className="font-mono text-zinc-800 dark:text-zinc-200 font-medium">
                          {m.expected_calibration_error.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Precision / Recall:</span>
                        <span className="font-mono text-zinc-800 dark:text-zinc-200 font-medium">
                          {m.precision.toFixed(3)} / {m.recall.toFixed(3)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Evaluation Dataset:</span>
                        <span className="font-mono text-zinc-600 dark:text-zinc-300">
                          {m.dataset_name}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Confusion Matrix Display */}
                  {m?.confusion_matrix && (
                    <div className="mt-4 p-3 rounded-xl bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-800">
                      <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block mb-1.5">
                        Holdout Confusion Matrix
                      </span>
                      <div className="grid grid-cols-2 gap-2 text-center text-xs font-mono">
                        <div className="p-1.5 rounded bg-white dark:bg-zinc-900 border border-zinc-200/60 dark:border-zinc-700">
                          <span className="text-[10px] text-zinc-400 block">TN (Misleading)</span>
                          <span className="font-bold text-zinc-900 dark:text-white">{m.confusion_matrix[0]?.[0] ?? 0}</span>
                        </div>
                        <div className="p-1.5 rounded bg-white dark:bg-zinc-900 border border-zinc-200/60 dark:border-zinc-700">
                          <span className="text-[10px] text-zinc-400 block">FP (False Alarm)</span>
                          <span className="font-bold text-zinc-900 dark:text-white">{m.confusion_matrix[0]?.[1] ?? 0}</span>
                        </div>
                        <div className="p-1.5 rounded bg-white dark:bg-zinc-900 border border-zinc-200/60 dark:border-zinc-700">
                          <span className="text-[10px] text-zinc-400 block">FN (Missed Cred.)</span>
                          <span className="font-bold text-zinc-900 dark:text-white">{m.confusion_matrix[1]?.[0] ?? 0}</span>
                        </div>
                        <div className="p-1.5 rounded bg-white dark:bg-zinc-900 border border-zinc-200/60 dark:border-zinc-700">
                          <span className="text-[10px] text-zinc-400 block">TP (Credible)</span>
                          <span className="font-bold text-zinc-900 dark:text-white">{m.confusion_matrix[1]?.[1] ?? 0}</span>
                        </div>
                      </div>
                    </div>
                  )}

                </div>

                <div className="text-[11px] text-zinc-400 flex items-center justify-between border-t border-zinc-100 dark:border-zinc-800 pt-3">
                  <span>Registered: {new Date(model.created_at).toLocaleDateString()}</span>
                  <span className="font-mono">Leakage Controlled</span>
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
