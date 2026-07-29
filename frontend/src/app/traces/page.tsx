'use client';
import { useEffect, useState } from 'react';
import { fetchTraceSpans } from '../../lib/api';
import { TraceSpan } from '../../lib/types';
import { TraceTimeline } from '../../components/TraceTimeline';

export default function TracesPage() {
  const [spans, setSpans] = useState<TraceSpan[]>([]);

  useEffect(() => {
    fetchTraceSpans('rev-001').then(setSpans);
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-slate-100">Trace & Audit Event Viewer</h1>
        <p className="text-xs text-slate-400">
          Reconstruct exact review execution history from the immutable TimescaleDB agent_events hypertable
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
        <div>
          <span className="text-xs text-slate-400 font-mono">Trace ID:</span>{' '}
          <span className="text-xs font-bold text-indigo-300 font-mono">rev-001 (acme/pr-prep-service#PR-104)</span>
        </div>
        <span className="text-xs text-slate-400 font-mono">Spans Recorded: {spans.length}</span>
      </div>

      <TraceTimeline spans={spans} />
    </div>
  );
}
