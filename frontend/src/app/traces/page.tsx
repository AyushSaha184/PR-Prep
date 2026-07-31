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
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="glass-card rounded-3xl p-8 border border-white/10 relative overflow-hidden shadow-2xl space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-mono font-medium text-indigo-300 bg-indigo-500/10 border border-indigo-500/30">
          <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse-glow"></span>
          <span>OpenTelemetry & TimescaleDB Event Spine</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight font-display">
          Trace & Audit Event Timeline
        </h1>
        <p className="text-xs text-slate-300 max-w-2xl font-normal leading-relaxed">
          Reconstruct exact review execution history, span latencies, tool calls, and model cost attributions from immutable <code className="text-indigo-300 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">agent_events</code> hypertables.
        </p>

        {/* Ambient glow */}
        <div className="absolute -top-20 -right-20 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Trace Selector Bar */}
      <div className="glass-card rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4 border border-white/10 shadow-lg">
        <div className="flex items-center space-x-3">
          <span className="text-xs text-slate-400 font-mono font-bold">Active Trace Workflow:</span>
          <span className="text-xs font-bold font-mono text-indigo-300 bg-[#05070a] px-3.5 py-1.5 rounded-lg border border-indigo-500/30 shadow-inner">
            rev-001 (acme/pr-prep-service#PR-104)
          </span>
        </div>
        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="text-slate-400">Recorded Spans:</span>
          <span className="font-extrabold text-emerald-300 bg-emerald-950/60 px-3 py-1 rounded-md border border-emerald-800 tabular-nums">
            {spans.length} Spans
          </span>
        </div>
      </div>

      {/* Connected Trace Timeline */}
      <TraceTimeline spans={spans} />
    </div>
  );
}

