'use client';

import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Trash2,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Calendar,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { api } from '../lib/api';
import { AnalysisListItem, AnalysisResponse } from '../types';

interface HistoryViewProps {
  onSelectAnalysis: (analysis: AnalysisResponse) => void;
  onOpenAuth: () => void;
  isAuthenticated: boolean;
}

export const HistoryView: React.FC<HistoryViewProps> = ({
  onSelectAnalysis,
  onOpenAuth,
  isAuthenticated,
}) => {
  const [items, setItems] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [assessmentFilter, setAssessmentFilter] = useState('');
  const [inputTypeFilter, setInputTypeFilter] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listAnalyses({
        search: search || undefined,
        assessment: assessmentFilter || undefined,
        input_type: inputTypeFilter || undefined,
      });
      setItems(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [assessmentFilter, inputTypeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleOpenItem = async (id: string) => {
    try {
      const full = await api.getAnalysis(id);
      onSelectAnalysis(full);
    } catch (err: any) {
      alert(err.message || 'Unable to open analysis record.');
    }
  };

  const handleDeleteItem = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this analysis record?')) return;
    setDeletingId(id);
    try {
      await api.deleteAnalysis(id);
      setItems(prev => prev.filter(i => i.id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete record.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fadeIn">
      
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-zinc-200 dark:border-zinc-800 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-white">
            Analysis History
          </h2>
          <p className="text-xs text-zinc-500 mt-0.5">
            Review past credibility assessments and inspect immutable model results.
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={loading}
          className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-3">
        <form onSubmit={handleSearchSubmit} className="sm:col-span-6 relative">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search analysis titles..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500"
          />
        </form>

        <div className="sm:col-span-3">
          <select
            value={assessmentFilter}
            onChange={(e) => setAssessmentFilter(e.target.value)}
            className="w-full py-2 px-3 text-xs rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500"
          >
            <option value="">All Assessments</option>
            <option value="CREDIBLE">Likely Credible</option>
            <option value="UNCERTAIN">Uncertain / Verification</option>
            <option value="MISLEADING">Likely Misleading</option>
          </select>
        </div>

        <div className="sm:col-span-3">
          <select
            value={inputTypeFilter}
            onChange={(e) => setInputTypeFilter(e.target.value)}
            className="w-full py-2 px-3 text-xs rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-zinc-500"
          >
            <option value="">All Input Types</option>
            <option value="article">Article</option>
            <option value="headline">Headline</option>
            <option value="url">URL</option>
          </select>
        </div>
      </div>

      {/* List Content */}
      {loading ? (
        <div className="py-20 text-center flex flex-col items-center justify-center gap-3 text-zinc-400">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-xs">Loading historical analyses...</span>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs">
          {error}
        </div>
      ) : items.length === 0 ? (
        <div className="py-20 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl p-8">
          <HelpCircle className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mx-auto mb-2" />
          <h4 className="text-sm font-bold text-zinc-900 dark:text-white">No analyses found</h4>
          <p className="text-xs text-zinc-500 mt-1 max-w-sm mx-auto">
            {search || assessmentFilter || inputTypeFilter
              ? 'No historical analyses match the selected filters.'
              : 'Analyze an article or headline in the workspace to build your verification record history.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => {
            const isCredible = item.label?.includes('CREDIBLE');
            const isMisleading = item.label?.includes('MISLEADING');
            const isUncertain = !isCredible && !isMisleading;

            return (
              <div
                key={item.id}
                onClick={() => handleOpenItem(item.id)}
                className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-zinc-400 dark:hover:border-zinc-600 transition-all cursor-pointer shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 group"
              >
                <div className="space-y-1 max-w-xl">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-zinc-900 dark:text-white group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors line-clamp-1">
                      {item.title}
                    </span>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-500">
                      {item.input_type}
                    </span>
                  </div>
                  <div className="text-[11px] text-zinc-400 flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {(() => {
                        try {
                          const d = new Date(item.created_at);
                          return isNaN(d.getTime()) ? 'Recent' : `${d.toLocaleDateString()} at ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
                        } catch {
                          return 'Recent';
                        }
                      })()}
                    </span>
                    {item.source_url && (
                      <span className="truncate max-w-xs text-zinc-500">
                        {item.source_url}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-4 shrink-0">
                  {item.label && (
                    <span
                      className={`px-2.5 py-1 rounded-md text-[11px] font-bold tracking-tight uppercase ${
                        isCredible
                          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/50'
                          : isMisleading
                          ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300 border border-rose-200 dark:border-rose-800/50'
                          : 'bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800/50'
                      }`}
                    >
                      {item.label}
                    </span>
                  )}

                  <button
                    onClick={(e) => handleDeleteItem(item.id, e)}
                    disabled={deletingId === item.id}
                    title="Delete record"
                    className="p-1.5 text-zinc-400 hover:text-rose-600 transition-colors rounded"
                  >
                    {deletingId === item.id ? (
                      <Loader2 className="w-4 h-4 animate-spin text-rose-600" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
