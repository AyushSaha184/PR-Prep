import React, { useState } from 'react';
import { Finding } from '../lib/types';
import { SeverityBadge } from './SeverityBadge';
import { ConfidenceMeter } from './ConfidenceMeter';
import { submitDispute } from '../lib/api';

interface FindingCardProps {
  finding: Finding;
  reviewId?: string;
  findingIndex?: number;
}

export const FindingCard: React.FC<FindingCardProps> = ({ finding, reviewId = 'rev-001', findingIndex = 0 }) => {
  const [showDisputeForm, setShowDisputeForm] = useState(false);
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [disputeResult, setDisputeResult] = useState<string | null>(null);

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
      setDisputeResult(`Dispute #${res.dispute_id} submitted for review!`);
      setShowDisputeForm(false);
      setReason('');
    } catch (err: any) {
      setDisputeResult('Dispute recorded.');
      setShowDisputeForm(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 space-y-3 shadow-md hover:border-slate-700 transition">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <SeverityBadge severity={finding.severity} />
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
            {finding.agent_type}
          </span>
          <span className="text-xs text-slate-500 font-mono">{finding.category}</span>
        </div>
        <ConfidenceMeter score={finding.confidence} />
      </div>

      <h4 className="text-sm font-medium text-slate-100">{finding.summary}</h4>

      <div className="text-xs text-indigo-400 font-mono bg-slate-950 px-2.5 py-1 rounded border border-slate-800/80 inline-block">
        {finding.file_path}:L{finding.line_start}-L{finding.line_end}
      </div>

      <div className="text-xs text-slate-300 bg-slate-950/60 p-2.5 rounded border border-slate-800 space-y-1">
        <span className="text-slate-400 font-semibold block">Rationale:</span>
        <p className="leading-relaxed">{finding.rationale}</p>
      </div>

      {finding.suggestion && (
        <div className="text-xs font-mono bg-slate-950 p-2.5 rounded border border-emerald-900/40 text-emerald-300 overflow-x-auto">
          <span className="text-emerald-500 font-semibold block font-sans mb-1">Suggested Fix:</span>
          <pre>{finding.suggestion}</pre>
        </div>
      )}

      {/* Developer Dispute Action */}
      <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
        <button
          onClick={() => setShowDisputeForm(!showDisputeForm)}
          className="text-xs text-amber-400 hover:text-amber-300 font-medium flex items-center space-x-1"
        >
          <span>⚖️ {showDisputeForm ? 'Cancel Dispute' : 'Dispute this Finding'}</span>
        </button>

        {disputeResult && <span className="text-xs font-mono text-emerald-400">{disputeResult}</span>}
      </div>

      {showDisputeForm && (
        <form onSubmit={handleDisputeSubmit} className="bg-slate-950 p-3 rounded-lg border border-amber-900/40 space-y-2 mt-2">
          <label className="text-xs font-semibold text-slate-300 block">
            Reason for disputing finding:
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g. False positive: input is sanitized upstream in validator middleware"
            className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            required
          />
          <div className="flex justify-end space-x-2">
            <button
              type="submit"
              disabled={submitting}
              className="px-3 py-1 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded text-xs font-semibold shadow"
            >
              Submit Dispute
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
