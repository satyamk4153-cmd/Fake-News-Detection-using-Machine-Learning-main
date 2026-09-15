'use client';

import React, { useState, useEffect } from 'react';
import {
  Settings,
  Activity,
  Cpu,
  BarChart3,
  ShieldAlert,
  Loader2,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import { api } from '../lib/api';
import { AnalyticsOverview, SystemHealthData, ModelVersionData, AuditLogItem } from '../types';

export const AdminView: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [health, setHealth] = useState<SystemHealthData | null>(null);
  const [models, setModels] = useState<ModelVersionData[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingModelId, setUpdatingModelId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [analyticsData, healthData, modelsData, logsData] = await Promise.all([
        api.getAdminAnalytics(),
        api.getSystemHealth(),
        api.getAdminModels(),
        api.getAuditLogs(25),
      ]);
      setAnalytics(analyticsData);
      setHealth(healthData);
      setModels(modelsData);
      setAuditLogs(logsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load administrative telemetry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleStatusChange = async (modelId: string, newStatus: string) => {
    setUpdatingModelId(modelId);
    try {
      await api.updateModelStatus(modelId, newStatus);
      await fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to update model status.');
    } finally {
      setUpdatingModelId(null);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center flex flex-col items-center justify-center gap-3 text-zinc-400">
        <Loader2 className="w-7 h-7 animate-spin" />
        <span className="text-xs font-medium">Gathering administrative telemetry...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs">
        <h4 className="font-bold text-sm mb-1">Administrative Access Error</h4>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-10 animate-fadeIn pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-zinc-200 dark:border-zinc-800 pb-5">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-semibold bg-amber-50 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 mb-2 border border-amber-200 dark:border-amber-800">
            <Settings className="w-3.5 h-3.5" />
            Administrative Control Panel
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
            System Telemetry & Model Governance
          </h2>
          <p className="text-xs text-zinc-500 mt-1">
            Real-time server metrics, database counts, model promotion controls, and security audit logs.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="px-3.5 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-xs font-semibold text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Subsystem Health Cards */}
      {health && (
        <section className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            <span className="text-[11px] text-zinc-400 uppercase font-semibold block">System Status</span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1.5 font-mono">
              <CheckCircle className="w-4 h-4" />
              {health.status.toUpperCase()}
            </span>
          </div>

          <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            <span className="text-[11px] text-zinc-400 uppercase font-semibold block">Database</span>
            <span className="text-sm font-bold text-zinc-900 dark:text-white mt-1 font-mono">
              {health.database}
            </span>
          </div>

          <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            <span className="text-[11px] text-zinc-400 uppercase font-semibold block">Active Model</span>
            <span className="text-sm font-bold text-zinc-900 dark:text-white mt-1 font-mono">
              {health.active_model_version}
            </span>
          </div>

          <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            <span className="text-[11px] text-zinc-400 uppercase font-semibold block">Mean Latency</span>
            <span className="text-sm font-bold text-zinc-900 dark:text-white mt-1 font-mono">
              {analytics?.average_inference_latency_ms} ms
            </span>
          </div>
        </section>
      )}

      {/* Analytics Overview Cards */}
      {analytics && (
        <section className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-zinc-500" />
            Platform Aggregate Usage Analytics
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs">
              <span className="text-xs text-zinc-400 font-semibold block">Total Analyses Completed</span>
              <span className="text-2xl font-black font-mono text-zinc-900 dark:text-white mt-1 block">
                {analytics.total_analyses}
              </span>
              <span className="text-[11px] text-zinc-500 mt-2 block">
                Articles: {analytics.analyses_by_input_type?.article || 0} | Headlines: {analytics.analyses_by_input_type?.headline || 0} | URLs: {analytics.analyses_by_input_type?.url || 0}
              </span>
            </div>

            <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs">
              <span className="text-xs text-zinc-400 font-semibold block">Mean Model Confidence</span>
              <span className="text-2xl font-black font-mono text-zinc-900 dark:text-white mt-1 block">
                {analytics.average_confidence}%
              </span>
              <span className="text-[11px] text-zinc-500 mt-2 block">
                Uncertain Rate: {analytics.uncertain_rate}%
              </span>
            </div>

            <div className="p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xs">
              <span className="text-xs text-zinc-400 font-semibold block">User Feedback Submissions</span>
              <span className="text-2xl font-black font-mono text-zinc-900 dark:text-white mt-1 block">
                {analytics.total_feedbacks}
              </span>
              <span className="text-[11px] text-zinc-500 mt-2 block">
                Failure Rate: {analytics.failure_rate}%
              </span>
            </div>
          </div>
        </section>
      )}

      {/* Model Version Promotion and Lifecycle Management */}
      <section className="space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-zinc-500" />
          Model Lifecycle & Promotion Management
        </h3>

        <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-zinc-200 dark:border-zinc-800 text-zinc-400 font-semibold uppercase">
                <th className="py-3 px-4">Version Tag</th>
                <th className="py-3 px-4">Architecture</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {models.map((m) => (
                <tr key={m.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/40">
                  <td className="py-3 px-4 font-mono font-bold text-zinc-900 dark:text-white">
                    {m.version_tag}
                  </td>
                  <td className="py-3 px-4 text-zinc-600 dark:text-zinc-300 font-medium">
                    {m.model_type}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        m.status === 'PRODUCTION'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : m.status === 'STAGING'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                          : 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400'
                      }`}
                    >
                      {m.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    {m.status !== 'PRODUCTION' ? (
                      <button
                        onClick={() => handleStatusChange(m.id, 'PRODUCTION')}
                        disabled={updatingModelId === m.id}
                        className="px-2.5 py-1 rounded border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-xs font-semibold text-zinc-800 dark:text-zinc-200 transition-colors"
                      >
                        Promote to Production
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStatusChange(m.id, 'STAGING')}
                        disabled={updatingModelId === m.id}
                        className="px-2.5 py-1 rounded border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-xs font-semibold text-zinc-800 dark:text-zinc-200 transition-colors"
                      >
                        Demote to Staging
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Security Audit Trail */}
      <section className="space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-900 dark:text-white flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-zinc-500" />
          Security Audit Trail (Last 25 Events)
        </h3>

        <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-zinc-200 dark:border-zinc-800 text-zinc-400 font-semibold uppercase">
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Action</th>
                <th className="py-2.5 px-4">Target Type</th>
                <th className="py-2.5 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/40">
                  <td className="py-2.5 px-4 text-zinc-400">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-2.5 px-4 font-bold text-zinc-900 dark:text-white">
                    {log.action}
                  </td>
                  <td className="py-2.5 px-4 text-zinc-500">
                    {log.target_type}
                  </td>
                  <td className="py-2.5 px-4 text-zinc-600 dark:text-zinc-300 truncate max-w-xs">
                    {JSON.stringify(log.details)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

    </div>
  );
};
