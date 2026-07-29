import React from 'react';

interface ApprovalActionsProps {
  reviewId: string;
  onAction?: (action: string) => void;
}

export const ApprovalActions: React.FC<ApprovalActionsProps> = ({ reviewId, onAction }) => {
  const handle = (action: string) => {
    if (onAction) onAction(action);
    else alert(`Action "${action}" submitted for review ${reviewId}`);
  };

  return (
    <div className="flex items-center space-x-3 bg-slate-900 border border-slate-800 p-3 rounded-lg">
      <button
        onClick={() => handle('APPROVE')}
        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold shadow transition"
      >
        Approve & Post
      </button>
      <button
        onClick={() => handle('EDIT')}
        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold shadow transition"
      >
        Edit Findings
      </button>
      <button
        onClick={() => handle('REJECT')}
        className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold shadow transition"
      >
        Reject Review
      </button>
      <button
        onClick={() => handle('ESCALATE')}
        className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded text-xs font-semibold shadow transition"
      >
        Escalate to Lead
      </button>
    </div>
  );
};
