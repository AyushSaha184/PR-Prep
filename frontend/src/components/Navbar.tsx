import React from 'react';
import Link from 'next/link';

export const Navbar: React.FC = () => {
  return (
    <nav className="bg-slate-900 border-b border-slate-800 text-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/reviews" className="flex items-center space-x-2">
              <span className="bg-indigo-600 text-white px-2.5 py-1 rounded font-mono font-bold text-sm">PR PREP</span>
              <span className="text-xs text-slate-400 font-mono hidden sm:inline">Selective AI Reviewer</span>
            </Link>
            <div className="flex space-x-4 text-xs font-medium">
              <Link href="/reviews" className="hover:text-white px-3 py-2 rounded-md transition text-slate-300">
                Reviews
              </Link>
              <Link href="/hitl" className="hover:text-white px-3 py-2 rounded-md transition text-slate-300 flex items-center space-x-1">
                <span>HITL Queue</span>
                <span className="bg-red-500/20 text-red-400 text-[10px] px-1.5 py-0.5 rounded-full border border-red-500/30">1</span>
              </Link>
              <Link href="/traces" className="hover:text-white px-3 py-2 rounded-md transition text-slate-300">
                Trace Viewer
              </Link>
              <Link href="/economics" className="hover:text-white px-3 py-2 rounded-md transition text-slate-300">
                Economics
              </Link>
              <Link href="/health" className="hover:text-white px-3 py-2 rounded-md transition text-slate-300">
                Health
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
              ● Engine Online
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};
