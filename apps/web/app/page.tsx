'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { AuthModal } from '../components/AuthModal';
import { AnalysisWorkspace } from '../features/AnalysisWorkspace';
import { HistoryView } from '../features/HistoryView';
import { ModelsView } from '../features/ModelsView';
import { MethodologyView } from '../features/MethodologyView';
import { AdminView } from '../features/AdminView';
import { ResultView } from '../features/ResultView';
import { UserProfile, AnalysisResponse } from '../types';
import { api } from '../lib/api';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState<'analyze' | 'history' | 'models' | 'methodology' | 'admin'>('analyze');
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResponse | null>(null);

  // Load user profile on mount if token exists
  useEffect(() => {
    setMounted(true);
    const token = typeof window !== 'undefined' ? localStorage.getItem('truthlens_token') : null;
    if (token) {
      api.getMe()
        .then(setUser)
        .catch(() => {
          api.logout();
          setUser(null);
        });
    }
  }, []);

  const handleLogout = () => {
    api.logout();
    setUser(null);
    if (activeTab === 'admin') {
      setActiveTab('analyze');
    }
  };

  const handleSelectHistoryAnalysis = (analysis: AnalysisResponse) => {
    setSelectedAnalysis(analysis);
  };

  if (!mounted) {
    return (
      <div className="min-h-screen flex flex-col bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100" suppressHydrationWarning>
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 selection:bg-zinc-200 dark:selection:bg-zinc-800" suppressHydrationWarning>
      
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setSelectedAnalysis(null);
          setActiveTab(tab);
        }}
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {selectedAnalysis ? (
          <ResultView
            analysis={selectedAnalysis}
            onBack={() => setSelectedAnalysis(null)}
          />
        ) : (
          <>
            {activeTab === 'analyze' && (
              <AnalysisWorkspace onNavigateToMethodology={() => setActiveTab('methodology')} />
            )}

            {activeTab === 'history' && (
              <HistoryView
                onSelectAnalysis={handleSelectHistoryAnalysis}
                onOpenAuth={() => setIsAuthOpen(true)}
                isAuthenticated={!!user}
              />
            )}

            {activeTab === 'models' && <ModelsView />}

            {activeTab === 'methodology' && <MethodologyView />}

            {activeTab === 'admin' && <AdminView />}
          </>
        )}
      </main>

      <Footer onNavigate={(tab) => {
        setSelectedAnalysis(null);
        setActiveTab(tab);
      }} />

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(loggedUser) => setUser(loggedUser)}
      />

    </div>
  );
}
