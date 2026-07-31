'use client';
import { useEffect, useState } from 'react';
import { fetchReviews, fetchHealth, fetchHITLQueue, fetchPRCosts } from '../lib/api';
import { ReviewState, PRCost } from '../lib/types';
import Link from 'next/link';
import { SeverityBadge } from '../components/SeverityBadge';
import { ConfidenceMeter } from '../components/ConfidenceMeter';
import { MetricsCard } from '../components/MetricsCard';

export default function Home() {
  const [reviews, setReviews] = useState<ReviewState[]>([]);
  const [hitlQueue, setHitlQueue] = useState<ReviewState[]>([]);
  const [prCosts, setPrCosts] = useState<PRCost[]>([]);
  const [healthStatus, setHealthStatus] = useState<string>('Checking...');
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'POSTED_AUTOMATICALLY' | 'ROUTED_TO_HITL'>('ALL');

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [reviewsData, healthData, hitlData, costsData] = await Promise.all([
          fetchReviews(),
          fetchHealth(),
          fetchHITLQueue(),
          fetchPRCosts(),
        ]);
        setReviews(reviewsData);
        setHealthStatus(healthData.status);
        setHitlQueue(hitlData);
        setPrCosts(costsData);
      } catch (err) {
        console.error('Failed to load live dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const totalCost = prCosts.reduce((acc, c) => acc + (c.total_cost_usd || 0), 0);

  const filteredReviews = reviews.filter((rev) => {
    const matchesSearch =
      rev.repository.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rev.pr_number.toString().includes(searchQuery) ||
      rev.commit_sha.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || rev.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Header Command Banner */}
      <div className="glass-card rounded-3xl p-8 border border-white/10 relative overflow-hidden shadow-2xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-mono font-medium text-indigo-300 bg-indigo-500/10 border border-indigo-500/30">
              <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse-glow"></span>
              <span>4 Grounded Specialist AI Agents Active</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight font-display">
              Automated PR Review Command Center
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl font-normal leading-relaxed">
              Repository-grounded review engine with automated confidence gating, security audits, and human-in-the-loop governance.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <Link
              href="/hitl"
              className="px-5 py-3 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-amber-500/20 transition duration-200 flex items-center space-x-2 border border-amber-400/30"
            >
              <span>HITL Queue ({hitlQueue.length})</span>
              <span>→</span>
            </Link>
          </div>
        </div>

        {/* Ambient background glow points */}
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          icon="⚡"
          title="System Engine"
          value={healthStatus}
          subtitle="All components operational"
        />
        <MetricsCard
          icon="📦"
          title="Total PR Reviews"
          value={reviews.length}
          subtitle="Processed through pipeline"
          trend="+100%"
        />
        <MetricsCard
          icon="⚖️"
          title="HITL Escalations"
          value={hitlQueue.length}
          subtitle="Pending human decision"
        />
        <MetricsCard
          icon="💎"
          title="Total Spend"
          value={`$${totalCost.toFixed(3)}`}
          subtitle="OpenAI & Gemini API usage"
        />
      </div>

      {/* Live Reviews Filter & Search Toolbar */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-4 rounded-2xl border border-white/10">
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center space-x-2">
              <span>Recent Review Activity</span>
            </h2>
            <span className="text-xs font-mono font-semibold text-emerald-300 bg-emerald-950/60 px-2.5 py-0.5 rounded-full border border-emerald-800/80">
              Live Stream
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Search Input */}
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search PR, repo, SHA..."
                className="bg-[#05070a] border border-white/10 rounded-xl px-3.5 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition font-mono w-48 sm:w-56"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1.5 text-xs text-slate-400 hover:text-white"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center bg-[#05070a] p-1 rounded-xl border border-white/10 text-xs font-mono">
              <button
                onClick={() => setStatusFilter('ALL')}
                className={`px-3 py-1 rounded-lg font-semibold transition ${
                  statusFilter === 'ALL'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                All ({reviews.length})
              </button>
              <button
                onClick={() => setStatusFilter('POSTED_AUTOMATICALLY')}
                className={`px-3 py-1 rounded-lg font-semibold transition ${
                  statusFilter === 'POSTED_AUTOMATICALLY'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Auto-Posted
              </button>
              <button
                onClick={() => setStatusFilter('ROUTED_TO_HITL')}
                className={`px-3 py-1 rounded-lg font-semibold transition ${
                  statusFilter === 'ROUTED_TO_HITL'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                HITL Queue
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="glass-card rounded-2xl p-16 text-center text-slate-400 text-xs font-mono border border-white/10 shimmer-effect">
            Connecting to FastAPI review execution stream...
          </div>
        ) : filteredReviews.length === 0 ? (
          <div className="glass-card rounded-2xl p-12 text-center text-slate-400 text-xs font-mono border border-white/10">
            No pull request reviews matched your search or status filter.
          </div>
        ) : (
          <div className="space-y-4">
            {filteredReviews.map((rev) => (
              <div
                key={rev.review_id}
                className="glass-card glass-card-hover rounded-2xl p-6 space-y-4 border border-white/10"
              >
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/5 pb-4">
                  <div className="flex items-center space-x-3">
                    <Link
                      href={`/reviews/${rev.review_id}`}
                      className="text-base font-extrabold text-white hover:text-indigo-400 font-mono tracking-tight transition"
                    >
                      {rev.repository}#PR-{rev.pr_number}
                    </Link>
                    <span className="text-xs text-slate-400 font-mono bg-[#05070a] px-2.5 py-1 rounded-md border border-white/10">
                      SHA: <strong className="text-slate-200">{rev.commit_sha.slice(0, 7)}</strong>
                    </span>
                  </div>

                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold font-mono border shadow-sm ${
                      rev.status === 'POSTED_AUTOMATICALLY'
                        ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                        : rev.status === 'ROUTED_TO_HITL'
                        ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                        : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30'
                    }`}
                  >
                    {rev.status === 'POSTED_AUTOMATICALLY' ? '✓ POSTED_AUTOMATICALLY' : rev.status}
                  </span>
                </div>

                <div className="flex flex-wrap items-center justify-between text-xs text-slate-300 gap-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-slate-400 font-semibold font-mono text-xs">Findings:</span>
                    <span className="font-extrabold text-white font-mono text-sm bg-white/5 px-2 py-0.5 rounded border border-white/10">
                      {rev.findings.length}
                    </span>
                    <div className="flex items-center space-x-1.5 ml-2">
                      {rev.findings.map((f) => (
                        <SeverityBadge key={f.id} severity={f.severity} />
                      ))}
                    </div>
                  </div>
                  <ConfidenceMeter score={rev.overall_confidence} />
                </div>

                <div className="text-xs text-slate-300 bg-[#05070a]/90 p-3.5 rounded-xl border border-white/5 font-mono flex items-center space-x-2">
                  <span className="text-indigo-400 font-bold">POLICY GATE:</span>
                  <span className="text-slate-300">{rev.routing_decision}</span>
                </div>

                <div className="pt-2 flex justify-end">
                  <Link
                    href={`/reviews/${rev.review_id}`}
                    className="px-4 py-2 bg-white/5 hover:bg-white/10 text-slate-200 hover:text-white rounded-xl text-xs font-bold border border-white/10 transition flex items-center space-x-1.5 shadow-sm"
                  >
                    <span>Inspect Review Details</span>
                    <span>→</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

