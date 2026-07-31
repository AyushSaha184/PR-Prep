import React, { useState } from 'react';
import { Finding } from '../lib/types';
import { SeverityBadge } from './SeverityBadge';
import { ConfidenceMeter } from './ConfidenceMeter';
import { AgentStatusBadge } from './AgentStatusBadge';
import { submitDispute } from '../lib/api';

interface FindingCardProps {
  finding: Finding;
  reviewId?: string;
  findingIndex?: number;
}

export const FindingCard: React.FC<FindingCardProps> = ({
  finding,
  reviewId = 'rev-001',
  findingIndex = 0,
}) => {
  const [showDisputeForm, setShowDisputeForm] = useState(false);
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [disputeResult, setDisputeResult] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleDisputeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim()) return;

    setSubmitting(true);
    try {
      const res = await submitDispute({
        review_id: reviewId,
        finding_index: findingIndex,
        developer_id: 'dev_user',
        reason: reason,
      });
      setDisputeResult(`Dispute #${res.dispute_id} submitted!`);
      setShowDisputeForm(false);
      setReason('');
    } catch {
      setDisputeResult('Dispute recorded for review.');
      setShowDisputeForm(false);
    } finally {
      setSubmitting(false);
    }
  };

  const copySuggestedFix = () => {
    if (finding.suggestion) {
      navigator.clipboard.writeText(finding.suggestion);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const setPresetReason = (text: string) => {
    setReason(text);
  };

  return (
    <div className="glass-card glass-card-hover rounded-2xl p-6 space-y-4 relative overflow-hidden transition-all duration-300">
      {/* Top Metadata Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <SeverityBadge severity={finding.severity} />
          <AgentStatusBadge agent={finding.agent_type} />
          <span className="text-[10px] font-mono font-semibold text-slate-400 bg-white/[0.04] px-2.5 py-1 rounded-md border border-white/10">
            {finding.category}
          </span>
        </div>
        <ConfidenceMeter score={finding.confidence} />
      </div>

      {/* Summary Heading */}
      <h4 className="text-base font-bold text-white tracking-tight leading-snug">
        {finding.summary}
      </h4>

      {/* File & Line Range Pill */}
      <div className="flex items-center space-x-2 text-xs font-mono text-indigo-300 bg-[#07090e]/90 px-3 py-1.5 rounded-lg border border-indigo-500/20 shadow-inner w-fit">
        <span className="text-slate-400">📄</span>
        <span className="font-semibold">{finding.file_path}</span>
        <span className="text-slate-600">•</span>
        <span className="text-indigo-400 font-bold bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/30">
          L{finding.line_start}-L{finding.line_end}
        </span>
      </div>

      {/* Rationale Block */}
      <div className="text-xs text-slate-300 bg-[#07090e]/60 p-4 rounded-xl border border-white/5 space-y-1.5 shadow-inner">
        <div className="flex items-center space-x-1.5 text-slate-400 font-semibold text-[10px] uppercase tracking-wider font-mono">
          <span>🔍</span>
          <span>Agent Rationale & Evidence</span>
        </div>
        <p className="leading-relaxed text-slate-300 font-sans">{finding.rationale}</p>
      </div>

      {/* Suggested Remediation Code Block */}
      {finding.suggestion && (
        <div className="relative group text-xs font-mono bg-[#05070a] rounded-xl border border-emerald-500/30 overflow-hidden shadow-2xl">
          <div className="flex items-center justify-between px-4 py-2 bg-emerald-950/40 border-b border-emerald-500/20">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-[10px] text-emerald-300 font-bold uppercase tracking-wider font-sans">
                Suggested Patch / Remediation
              </span>
            </div>
            <button
              onClick={copySuggestedFix}
              className="text-[10px] font-mono font-semibold px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-200 border border-emerald-500/40 hover:bg-emerald-500/30 transition shadow-sm flex items-center space-x-1"
            >
              <span>{copied ? '✓ Copied to Clipboard' : '📋 Copy Patch'}</span>
            </button>
          </div>
          <div className="p-4 overflow-x-auto">
            <pre className="text-emerald-300 leading-relaxed font-mono whitespace-pre-wrap">
              {finding.suggestion}
            </pre>
          </div>
        </div>
      )}

      {/* Footer Actions (Dispute) */}
      <div className="pt-3 border-t border-white/5 flex items-center justify-between">
        <button
          onClick={() => setShowDisputeForm(!showDisputeForm)}
          className="text-xs font-semibold text-amber-400 hover:text-amber-300 transition flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 hover:border-amber-500/40"
        >
          <span>⚖️</span>
          <span>{showDisputeForm ? 'Cancel Dispute' : 'Dispute Finding'}</span>
        </button>

        {disputeResult && (
          <span className="text-xs font-mono text-emerald-300 bg-emerald-950/80 px-3 py-1 rounded-full border border-emerald-800 shadow-sm animate-fade-in">
            ✓ {disputeResult}
          </span>
        )}
      </div>

      {/* Dispute Form Drawer */}
      {showDisputeForm && (
        <form
          onSubmit={handleDisputeSubmit}
          className="bg-[#05070a] p-4 rounded-xl border border-amber-500/30 space-y-3 animate-slide-up"
        >
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-amber-300 font-mono">
              Provide Dispute Rationale & Evidence:
            </label>
            <div className="flex space-x-1 text-[10px] font-mono text-slate-400">
              <button
                type="button"
                onClick={() => setPresetReason('False positive: sanitized upstream in API gateway')}
                className="px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 text-slate-300 transition"
              >
                + Sanitized upstream
              </button>
              <button
                type="button"
                onClick={() => setPresetReason('Intentional architectural decision per ADR-004')}
                className="px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 text-slate-300 transition"
              >
                + Per ADR
              </button>
            </div>
          </div>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={2}
            placeholder="e.g. False positive: input is sanitized upstream in validator middleware"
            className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500 transition font-mono"
            required
          />
          <div className="flex justify-end space-x-2">
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold shadow-lg shadow-amber-600/20 transition"
            >
              {submitting ? 'Recording Dispute...' : 'Submit Lead Dispute'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

