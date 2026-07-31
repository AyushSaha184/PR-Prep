'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const Navbar: React.FC = () => {
  const pathname = usePathname();

  const navLinks = [
    { href: '/', label: 'Dashboard' },
    { href: '/reviews', label: 'Reviews' },
    { href: '/hitl', label: 'HITL Queue', badge: '1', alert: true },
    { href: '/traces', label: 'Trace Viewer' },
    { href: '/economics', label: 'Economics' },
    { href: '/health', label: 'Health' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#07090e]/80 backdrop-blur-xl border-b border-white/10 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand Identity */}
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-[1px] shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition duration-300">
                <div className="w-full h-full bg-[#0b0f19] rounded-[7px] flex items-center justify-center">
                  <span className="font-mono font-extrabold text-xs bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
                    Δ
                  </span>
                </div>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center space-x-2">
                  <span className="font-extrabold text-sm tracking-tight text-white font-mono">
                    PRism
                  </span>
                  <span className="px-1.5 py-0.5 text-[9px] font-mono font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 rounded">
                    v0.1
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono hidden md:inline-block tracking-tight">
                  Selective AI Code Review Engine
                </span>
              </div>
            </Link>

            {/* Nav links */}
            <nav className="flex items-center space-x-1">
              {navLinks.map((link) => {
                const isActive = pathname === link.href || (link.href !== '/' && pathname?.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center space-x-1.5 ${
                      isActive
                        ? 'bg-indigo-600/20 text-white border border-indigo-500/40 shadow-sm shadow-indigo-500/20'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
                    }`}
                  >
                    <span>{link.label}</span>
                    {link.badge && (
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold border ${
                          link.alert
                            ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse-glow'
                            : 'bg-slate-800 text-slate-300 border-slate-700'
                        }`}
                      >
                        {link.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Specialist & Live Status Badge */}
          <div className="hidden sm:flex items-center space-x-4">
            <div className="flex items-center space-x-1.5 text-[11px] font-mono text-slate-400 bg-white/[0.03] px-2.5 py-1 rounded-full border border-white/10">
              <div className="flex -space-x-1">
                <span className="w-2 h-2 rounded-full bg-purple-500 inline-block shadow-sm shadow-purple-500" title="Security Agent"></span>
                <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block shadow-sm shadow-cyan-400" title="Quality Agent"></span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block shadow-sm shadow-emerald-400" title="Tests Agent"></span>
                <span className="w-2 h-2 rounded-full bg-amber-400 inline-block shadow-sm shadow-amber-400" title="Docs Agent"></span>
              </div>
              <span className="ml-1 text-slate-300 font-medium">4 Agents Active</span>
            </div>

            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-mono text-emerald-300 bg-emerald-950/40 border border-emerald-800/60 shadow-sm shadow-emerald-950">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mr-2 animate-pulse-glow"></span>
              Engine Live
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

