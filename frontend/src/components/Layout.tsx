import React from 'react';
import { Navbar } from './Navbar';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen text-slate-100 font-sans antialiased flex flex-col selection:bg-indigo-500 selection:text-white">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <footer className="border-t border-white/5 py-6 bg-[#07090e]/60 backdrop-blur-md mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 font-mono gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-200">PRism Engine</span>
            <span>— Repository-Grounded Selective Reviewer</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>FastAPI Ingress</span>
            <span>•</span>
            <span>LangGraph Orchestrator</span>
            <span>•</span>
            <span>Tiger Cloud Postgres</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

