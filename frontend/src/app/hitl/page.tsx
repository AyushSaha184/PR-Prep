'use client';
import { useEffect, useState } from 'react';
import { fetchHITLQueue } from '../../lib/api';
import { ReviewState } from '../../lib/types';
import { FindingCard } from '../../components/FindingCard';
import { ApprovalActions } from '../../components/ApprovalActions';

export default function HITLQueuePage() {
  const [items, setItems] = useState<ReviewState[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHITLQueue().then((data) => {
      setItems(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="glass-card rounded-3xl p-8 border border-amber-500/30 relative overflow-hidden shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
            <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse-glow"></span>
            <span>Human-in-the-Loop Policy Gate Active</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight font-display">
            Human Approval & Governance Queue
          </h1>
          <p className="text-xs text-slate-300 max-w-2xl font-normal leading-relaxed">
            Escalated pull request reviews requiring mandatory Lead Engineer authorization before posting to GitHub.
          </p>
        </div>

        <div className="flex items-center space-x-3 relative z-10">
          <div className="px-4 py-2 bg-[#05070a] text-amber-300 rounded-xl text-xs font-mono font-bold border border-amber-500/40 shadow-lg flex items-center space-x-2">
            <span>⚠️</span>
            <span>Pending Review: {items.length} PRs</span>
          </div>
        </div>

        {/* Ambient background warning glow */}
        <div className="absolute -top-20 -right-20 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {loading ? (
        <div className="glass-card rounded-2xl p-16 text-center text-slate-400 text-xs font-mono border border-white/10 shimmer-effect">
          Fetching pending HITL escalation queue items...
        </div>
      ) : items.length === 0 ? (
        <div className="glass-card rounded-2xl p-16 text-center text-emerald-300 text-sm font-mono border border-emerald-500/30 shadow-xl space-y-2">
          <div className="text-2xl">🎉</div>
          <div className="font-bold">HITL Governance Queue Empty</div>
          <div className="text-xs text-slate-400">All recent automated reviews passed confidence and severity policy gates cleanly.</div>
        </div>
      ) : (
        <div className="space-y-8">
          {items.map((rev) => (
            <div
              key={rev.review_id}
              className="glass-card rounded-3xl p-8 space-y-6 border border-amber-500/30 shadow-2xl relative overflow-hidden"
            >
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
                <div>
                  <div className="flex items-center space-x-3">
                    <h3 className="text-xl font-extrabold text-white font-mono tracking-tight">
                      {rev.repository} #PR-{rev.pr_number}
                    </h3>
                    <span className="text-xs font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
                      SHA: {rev.commit_sha.slice(0, 7)}
                    </span>
                  </div>
                  <p className="text-xs text-amber-300 font-mono mt-1 font-semibold flex items-center space-x-1.5">
                    <span>🛡️</span>
                    <span>{rev.routing_decision}</span>
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="px-3.5 py-1.5 rounded-full bg-amber-500/10 text-amber-300 text-xs font-mono font-bold border border-amber-500/40 shadow-sm flex items-center space-x-1.5">
                    <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse"></span>
                    <span>Priority Escalation • SLA: 1h 45m</span>
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-400 font-mono flex items-center space-x-2">
                  <span>Escalated Findings ({rev.findings.length})</span>
                </h4>
                <div className="grid grid-cols-1 gap-4">
                  {rev.findings.map((f, idx) => (
                    <FindingCard
                      key={f.id}
                      finding={f}
                      reviewId={rev.review_id}
                      findingIndex={idx}
                    />
                  ))}
                </div>
              </div>

              <div className="pt-6 border-t border-white/10 space-y-4">
                <div className="flex items-center space-x-2 text-xs font-extrabold uppercase tracking-wider text-amber-400 font-mono">
                  <span>⚖️</span>
                  <span>Lead Reviewer Authorization Action</span>
                </div>
                <ApprovalActions reviewId={rev.review_id} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

