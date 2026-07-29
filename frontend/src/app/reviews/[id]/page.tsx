'use client';
import { useEffect, useState } from 'react';
import { fetchReviewById } from '../../../lib/api';
import { ReviewState } from '../../../lib/types';
import { FindingCard } from '../../../components/FindingCard';
import { ConfidenceMeter } from '../../../components/ConfidenceMeter';
import { ApprovalActions } from '../../../components/ApprovalActions';
import Link from 'next/link';

export default function ReviewDetailPage({ params }: { params: { id: string } }) {
  const [review, setReview] = useState<ReviewState | null>(null);

  useEffect(() => {
    fetchReviewById(params.id).then((res) => {
      if (res) setReview(res);
    });
  }, [params.id]);

  if (!review) {
    return <div className="py-12 text-center text-slate-500 text-xs font-mono">Loading review {params.id}...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <Link href="/reviews" className="text-xs text-indigo-400 hover:text-indigo-300 mb-1 inline-block">
            ← Back to Reviews
          </Link>
          <h1 className="text-xl font-bold text-slate-100 font-mono">
            {review.repository} #PR-{review.pr_number}
          </h1>
          <p className="text-xs text-slate-400 font-mono">Commit SHA: {review.commit_sha}</p>
        </div>
        <ConfidenceMeter score={review.overall_confidence} />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
        <div className="text-xs font-semibold text-slate-300">Routing Decision & Autonomy State</div>
        <div className="text-xs text-indigo-300 font-mono bg-slate-950 p-3 rounded border border-slate-800">
          {review.routing_decision}
        </div>
      </div>

      {review.status === 'ROUTED_TO_HITL' && (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Human Action Required</div>
          <ApprovalActions reviewId={review.review_id} />
        </div>
      )}

      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-200">Discovered Specialist Findings ({review.findings.length})</h3>
        {review.findings.map((finding) => (
          <FindingCard key={finding.id} finding={finding} />
        ))}
      </div>
    </div>
  );
}
