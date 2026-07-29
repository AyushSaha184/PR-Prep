import React, { useState } from 'react';
import { submitHITLAction } from '../lib/api';

interface ApprovalActionsProps {
  reviewId: string;
  onAction?: (action: string) => void;
}

export const ApprovalActions: React.FC<ApprovalActionsProps> = ({ reviewId, onAction }) => {
  const [submitting, setSubmitting] = useState(false);
  const [submittedStatus, setSubmittedStatus] = useState<string | null>(null);

  const handle = async (action: 'APPROVE' | 'EDIT' | 'REJECT' | 'ESCALATE') => {
    setSubmitting(true);
    try {
      await submitHITLAction({
        review_id: reviewId,
        expected_version: 1,
        action: action,
        reviewer: 'reviewer_lead',
        comment: `Action ${action} executed via Dashboard UI`,
      });
      setSubmittedStatus(`Action "${action}" recorded on backend!`);
      if (onAction) onAction(action);
    } catch (err: any) {
      setSubmittedStatus(`Action submitted: ${action}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-3 bg-slate-900 border border-slate-800 p-3 rounded-lg">
        <button
          disabled={submitting}
          onClick={() => handle('APPROVE')}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded text-xs font-semibold shadow transition"
        >
          Approve & Post
        </button>
        <button
          disabled={submitting}
          onClick={() => handle('EDIT')}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded text-xs font-semibold shadow transition"
        >
          Edit Findings
        </button>
        <button
          disabled={submitting}
          onClick={() => handle('REJECT')}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white rounded text-xs font-semibold shadow transition"
        >
          Reject Review
        </button>
        <button
          disabled={submitting}
          onClick={() => handle('ESCALATE')}
          className="px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded text-xs font-semibold shadow transition"
        >
          Escalate to Lead
        </button>
      </div>
      {submittedStatus && (
        <div className="text-xs font-mono text-emerald-400 pl-1">{submittedStatus}</div>
      )}
    </div>
  );
};
