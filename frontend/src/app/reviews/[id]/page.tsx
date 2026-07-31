'use client';
import { useEffect, useState } from 'react';
import { fetchReviewById, fetchGovernanceExplanation } from '../../../lib/api';
import { ReviewState, AgentType } from '../../../lib/types';
import { FindingCard } from '../../../components/FindingCard';
import { ConfidenceMeter } from '../../../components/ConfidenceMeter';
import { ApprovalActions } from '../../../components/ApprovalActions';
import Link from 'next/link';

export default function ReviewDetailPage({ params }: { params: { id: string } }) {
  const [review, setReview] = useState<ReviewState | null>(null);
  const [explanation, setExplanation] = useState<Record<string, any> | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<AgentType | 'ALL'>('ALL');
  const [activeTab, setActiveTab] = useState<'findings' | 'governance' | 'raw'>('findings');

  useEffect(() => {
    fetchReviewById(params.id).then((res) => {
      if (res) setReview(res);
    });
    fetchGovernanceExplanation(params.id).then((exp) => {
      setExplanation(exp);
    });
  }, [params.id]);

  if (!review) {
    return (
      <div className="glass-card rounded-2xl p-16 text-center text-slate-400 text-xs font-mono border border-white/10 shimmer-effect">
        Retrieving inspection details for review {params.id}...
      </div>
    );
  }

  const filteredFindings =
    selectedAgent === 'ALL'
      ? review.findings
      : review.findings.filter((f) => f.agent_type === selectedAgent);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Nav & PR Identifier Hero Card */}
      <div className="glass-card rounded-3xl p-8 border border-indigo-500/30 relative overflow-hidden shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <Link
              href="/"
              className="text-xs font-mono font-bold text-indigo-400 hover:text-indigo-300 transition inline-flex items-center space-x-1.5 bg-indigo-500/10 px-3 py-1 rounded-full border border-indigo-500/20"
            >
              <span>← Back to Command Center</span>
            </Link>
            <h1 className="text-3xl font-extrabold text-white font-mono tracking-tight pt-1">
              {review.repository} <span className="text-indigo-400">#PR-{review.pr_number}</span>
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-slate-400">
              <span>Commit SHA: <strong className="text-white bg-white/5 px-2 py-0.5 rounded border border-white/10">{review.commit_sha}</strong></span>
              <span>•</span>
              <span>Workflow ID: <strong className="text-indigo-300">{review.workflow_id}</strong></span>
            </div>
          </div>

          <div className="flex flex-col items-end space-y-3 relative z-10">
            <ConfidenceMeter score={review.overall_confidence} />
            <span
              className={`px-3.5 py-1 rounded-full text-xs font-mono font-extrabold border shadow-sm ${
                review.status === 'POSTED_AUTOMATICALLY'
                  ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                  : review.status === 'ROUTED_TO_HITL'
                  ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                  : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30'
              }`}
            >
              {review.status}
            </span>
          </div>
        </div>

        {/* Ambient top glow */}
        <div className="absolute -top-20 -right-20 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Navigation Tabs Bar */}
      <div className="flex items-center space-x-2 border-b border-white/10 pb-3 font-mono text-xs">
        <button
          onClick={() => setActiveTab('findings')}
          className={`px-4 py-2 rounded-xl font-bold transition flex items-center space-x-2 ${
            activeTab === 'findings'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20 border border-indigo-500/40'
              : 'text-slate-400 hover:text-white bg-white/5'
          }`}
        >
          <span>Findings Overview ({review.findings.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('governance')}
          className={`px-4 py-2 rounded-xl font-bold transition flex items-center space-x-2 ${
            activeTab === 'governance'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20 border border-indigo-500/40'
              : 'text-slate-400 hover:text-white bg-white/5'
          }`}
        >
          <span>🛡️ Governance Audit Record</span>
        </button>
        <button
          onClick={() => setActiveTab('raw')}
          className={`px-4 py-2 rounded-xl font-bold transition flex items-center space-x-2 ${
            activeTab === 'raw'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20 border border-indigo-500/40'
              : 'text-slate-400 hover:text-white bg-white/5'
          }`}
        >
          <span>JSON Payload</span>
        </button>
      </div>

      {/* Autonomy State & Policy Gate Banner */}
      <div className="glass-card rounded-2xl p-5 border border-indigo-500/20 space-y-2 shadow-xl">
        <div className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono flex items-center space-x-2">
          <span>⚡ Policy Gate Decision</span>
        </div>
        <div className="text-xs font-mono text-indigo-300 bg-[#05070a] p-4 rounded-xl border border-white/10">
          {review.routing_decision}
        </div>
      </div>

      {/* Lead Reviewer Action Banner if HITL */}
      {review.status === 'ROUTED_TO_HITL' && (
        <div className="glass-card rounded-3xl p-6 border border-amber-500/40 space-y-4 shadow-2xl bg-amber-500/[0.02]">
          <div className="text-xs font-extrabold text-amber-300 uppercase tracking-wider font-mono flex items-center space-x-2">
            <span>⚠️ Lead Reviewer Authorization Required</span>
          </div>
          <ApprovalActions reviewId={review.review_id} />
        </div>
      )}

      {/* Tab 1: Specialist Findings */}
      {activeTab === 'findings' && (
        <div className="space-y-6">
          {/* Agent Filter Buttons */}
          <div className="flex flex-wrap items-center justify-between gap-4 glass-card p-4 rounded-2xl border border-white/10">
            <span className="text-xs font-mono font-bold text-slate-300">Filter by Agent Specialist:</span>
            <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
              {(['ALL', 'security', 'quality', 'tests', 'docs'] as const).map((agent) => (
                <button
                  key={agent}
                  onClick={() => setSelectedAgent(agent)}
                  className={`px-3 py-1.5 rounded-lg font-bold capitalize transition border ${
                    selectedAgent === agent
                      ? 'bg-indigo-600/30 text-white border-indigo-500/50 shadow-sm'
                      : 'bg-white/5 text-slate-400 border-white/5 hover:text-white'
                  }`}
                >
                  {agent}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-5">
            {filteredFindings.map((finding) => (
              <FindingCard key={finding.id} finding={finding} reviewId={review.review_id} />
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Governance Audit Record */}
      {activeTab === 'governance' && (
        <div className="glass-card rounded-3xl p-8 border border-indigo-500/40 space-y-4 shadow-2xl">
          <div className="text-sm font-extrabold uppercase tracking-wider text-indigo-300 font-mono flex items-center space-x-2">
            <span>🛡️ Policy Gate & RAG Governance Audit</span>
          </div>
          {explanation ? (
            <div className="text-xs text-slate-200 space-y-4 font-mono bg-[#05070a] p-6 rounded-2xl border border-white/10">
              {explanation.why_raised && (
                <div>
                  <span className="text-slate-500 block mb-1">Reason Raised:</span>
                  <span className="text-slate-100 font-bold bg-white/5 p-2 rounded block">{explanation.why_raised}</span>
                </div>
              )}
              {explanation.why_routed && (
                <div>
                  <span className="text-slate-500 block mb-1">Routing Explanation:</span>
                  <span className="text-amber-300 font-bold bg-amber-500/10 p-2 rounded block border border-amber-500/30">{explanation.why_routed}</span>
                </div>
              )}
              {explanation.cited_context_chunk_ids && (
                <div>
                  <span className="text-slate-500 block mb-1">Cited Vector Chunks:</span>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {explanation.cited_context_chunk_ids.map((chunkId: string) => (
                      <span key={chunkId} className="text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1 rounded-md border border-emerald-500/30">
                        {chunkId}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs font-mono text-slate-400">Loading audit record...</div>
          )}
        </div>
      )}

      {/* Tab 3: Raw JSON Payload */}
      {activeTab === 'raw' && (
        <div className="glass-card rounded-3xl p-6 border border-white/10 space-y-3 font-mono text-xs">
          <div className="text-slate-400 font-bold">Review State Raw Payload:</div>
          <pre className="bg-[#05070a] p-6 rounded-2xl border border-white/10 text-emerald-400 overflow-x-auto leading-relaxed">
            {JSON.stringify(review, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

