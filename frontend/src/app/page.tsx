'use client';
import { useEffect, useState } from 'react';
import { fetchReviews, fetchHealth, fetchHITLQueue, fetchPRCosts } from '../lib/api';
import { ReviewState, PRCost } from '../lib/types';
import Link from 'next/link';
import { SeverityBadge } from '../components/SeverityBadge';
import { ConfidenceMeter } from '../components/ConfidenceMeter';

export default function Home() {
  const [reviews, setReviews] = useState<ReviewState[]>([]);
  const [hitlQueue, setHitlQueue] = useState<ReviewState[]>([]);
  const [prCosts, setPrCosts] = useState<PRCost[]>([]);
  const [healthStatus, setHealthStatus] = useState<string>('Checking...');
  const [loading, setLoading] = useState(true);

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

  return (
    <div className="space-y-6">
      {/* Top Bar Header & Live Metrics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4 gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Automated Pull Request Reviews</h1>
          <p className="text-xs text-slate-400">Ground-checked specialist findings & human approval queue</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
            <span className="text-slate-400">System Status:</span>
            <span className="font-semibold text-emerald-400 flex items-center space-x-1">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>{healthStatus}</span>
            </span>
          </div>
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
            <span className="text-slate-400">Total Reviews:</span>
            <span className="font-mono font-bold text-indigo-300">{reviews.length}</span>
          </div>
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
            <span className="text-slate-400">HITL Queue:</span>
            <span className="font-mono font-bold text-amber-400">{hitlQueue.length}</span>
          </div>
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
            <span className="text-slate-400">Total Spend:</span>
            <span className="font-mono font-bold text-emerald-300">${totalCost.toFixed(3)}</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-xs font-mono">Loading live backend review stream...</div>
      ) : (
        <div className="space-y-4">
          {reviews.map((rev) => (
            <div
              key={rev.review_id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Link
                    href={`/reviews/${rev.review_id}`}
                    className="text-sm font-bold text-indigo-400 hover:text-indigo-300 font-mono"
                  >
                    {rev.repository}#PR-{rev.pr_number}
                  </Link>
                  <span className="text-xs text-slate-500 font-mono">Commit: {rev.commit_sha.slice(0, 7)}</span>
                </div>
                <span
                  className={`px-2.5 py-0.5 rounded text-xs font-semibold font-mono border ${
                    rev.status === 'POSTED_AUTOMATICALLY'
                      ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                      : rev.status === 'ROUTED_TO_HITL'
                      ? 'bg-amber-950 text-amber-300 border-amber-800'
                      : 'bg-indigo-950 text-indigo-300 border-indigo-800'
                  }`}
                >
                  {rev.status}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                <div>
                  Findings: <span className="font-bold text-slate-200">{rev.findings.length}</span> (
                  {rev.findings.map((f) => (
                    <span key={f.id} className="mr-1.5 inline-block">
                      <SeverityBadge severity={f.severity} />
                    </span>
                  ))}
                  )
                </div>
                <ConfidenceMeter score={rev.overall_confidence} />
              </div>

              <div className="text-xs text-slate-500 bg-slate-950 p-2.5 rounded border border-slate-800/80 font-mono">
                {rev.routing_decision}
              </div>

              <div className="pt-2 flex justify-end">
                <Link
                  href={`/reviews/${rev.review_id}`}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center space-x-1"
                >
                  <span>View Review Details →</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
