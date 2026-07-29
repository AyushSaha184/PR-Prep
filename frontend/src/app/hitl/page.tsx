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
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-slate-100">Human-in-the-Loop Approval Queue</h1>
        <p className="text-xs text-slate-400">
          Reviews held for manual verification due to CRITICAL findings, low confidence, or policy constraints.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500 text-xs font-mono">Loading live HITL approval queue...</div>
      ) : items.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-xs text-slate-400 font-mono">
          Queue empty. All automated reviews met auto-post confidence criteria!
        </div>
      ) : (
        <div className="space-y-6">
          {items.map((rev) => (
            <div key={rev.review_id} className="bg-slate-900 border border-amber-900/60 rounded-xl p-5 space-y-4 shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-100 font-mono">
                    {rev.repository} #PR-{rev.pr_number}
                  </h3>
                  <span className="text-xs text-amber-400 font-mono">
                    Reason: CRITICAL Finding Detected or Budget Limit
                  </span>
                </div>
                <span className="px-2.5 py-1 rounded bg-amber-950 text-amber-300 text-xs font-bold border border-amber-800">
                  Priority 1 — SLA: 2h
                </span>
              </div>

              <div className="space-y-3">
                <div className="text-xs font-semibold text-slate-300">Findings to Review ({rev.findings.length})</div>
                {rev.findings.map((f) => (
                  <FindingCard key={f.id} finding={f} />
                ))}
              </div>

              <div className="pt-2 border-t border-slate-800">
                <div className="text-xs font-semibold text-slate-300 mb-2">Reviewer Decision</div>
                <ApprovalActions reviewId={rev.review_id} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
