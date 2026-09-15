'use client';

import React from 'react';
import { ShieldCheck, History, Cpu, FileText, Settings, User, LogOut } from 'lucide-react';
import { UserProfile } from '../types';

interface NavbarProps {
  activeTab: 'analyze' | 'history' | 'models' | 'methodology' | 'admin';
  setActiveTab: (tab: 'analyze' | 'history' | 'models' | 'methodology' | 'admin') => void;
  user: UserProfile | null;
  onOpenAuth: () => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenAuth,
  onLogout,
}) => {
  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white/95 dark:bg-zinc-950/95 sticky top-0 z-40 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div 
          onClick={() => setActiveTab('analyze')}
          className="flex items-center gap-3 cursor-pointer group select-none"
        >
          <div className="w-9 h-9 rounded-lg bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center text-white dark:text-zinc-900 shadow-sm transition-transform group-hover:scale-105">
            <ShieldCheck className="w-5 h-5 stroke-[2.2]" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-zinc-900 dark:text-white">
              Truth<span className="text-zinc-500 dark:text-zinc-400 font-normal">Lens</span>
            </span>
            <span className="hidden md:inline-block ml-2.5 px-2 py-0.5 text-[11px] font-medium tracking-wide uppercase rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700">
              Research v1.0
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1">
          <button
            onClick={() => setActiveTab('analyze')}
            className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'analyze'
                ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white font-semibold'
                : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-900'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            Analyze
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'history'
                ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white font-semibold'
                : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-900'
            }`}
          >
            <History className="w-4 h-4" />
            History
          </button>

          <button
            onClick={() => setActiveTab('models')}
            className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'models'
                ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white font-semibold'
                : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-900'
            }`}
          >
            <Cpu className="w-4 h-4" />
            Models
          </button>

          <button
            onClick={() => setActiveTab('methodology')}
            className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'methodology'
                ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white font-semibold'
                : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-900'
            }`}
          >
            <FileText className="w-4 h-4" />
            Methodology
          </button>

          {user?.role === 'ADMIN' && (
            <button
              onClick={() => setActiveTab('admin')}
              className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                activeTab === 'admin'
                  ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 font-semibold border border-amber-200 dark:border-amber-800/50'
                  : 'text-amber-700 dark:text-amber-400 hover:bg-amber-50/60 dark:hover:bg-amber-950/20'
              }`}
            >
              <Settings className="w-4 h-4" />
              Admin
            </button>
          )}
        </nav>

        {/* User / Authentication Actions */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-2.5">
              <div className="hidden sm:flex flex-col items-end">
                <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-200">
                  {user.email}
                </span>
                <span className="text-[10px] text-zinc-500 dark:text-zinc-400 uppercase tracking-wider font-mono">
                  {user.role}
                </span>
              </div>
              <button
                onClick={onLogout}
                title="Log Out"
                className="p-2 rounded-lg border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-4 py-2 rounded-lg text-sm font-medium bg-zinc-900 hover:bg-zinc-800 text-white dark:bg-zinc-100 dark:hover:bg-zinc-200 dark:text-zinc-900 transition-colors shadow-sm flex items-center gap-2"
            >
              <User className="w-4 h-4" />
              Sign In
            </button>
          )}
        </div>

      </div>
    </header>
  );
};
