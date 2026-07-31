import React from 'react';
import { TraceSpan } from '../lib/types';
import { AgentStatusBadge } from './AgentStatusBadge';

export const TraceTimeline: React.FC<{ spans: TraceSpan[] }> = ({ spans }) => {
  return (
    <div className="relative space-y-6 pl-4 before:absolute before:inset-0 before:left-7 before:w-0.5 before:bg-gradient-to-b before:from-indigo-500/40 before:via-purple-500/40 before:to-emerald-500/20">
      {spans.map((span, idx) => (
        <div
          key={span.span_id || idx}
          className="relative flex items-start space-x-4 glass-card glass-card-hover rounded-2xl p-5 ml-4 animate-slide-up group"
        >
          {/* Connected timeline node icon */}
          <div className="relative z-10 -ml-10 p-1.5 bg-[#07090e] border border-white/10 rounded-xl shadow-xl">
            <AgentStatusBadge agent={span.agent} />
          </div>

          {/* Span metadata body */}
          <div className="flex-1 space-y-3 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-3">
              <div className="flex items-center space-x-2">
                <span className="font-mono font-bold text-white text-sm tracking-tight">
                  {span.event_type}
                </span>
                <span className="text-[10px] text-slate-400 font-mono bg-white/5 px-2 py-0.5 rounded border border-white/10">
                  ID: {span.span_id}
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-mono bg-[#05070a] px-2.5 py-1 rounded-md border border-white/10 tabular-nums">
                🕒 {new Date(span.timestamp).toLocaleTimeString()}
              </span>
            </div>

            {span.model && (
              <div className="flex flex-wrap items-center gap-3 text-slate-300 font-mono bg-[#05070a]/90 p-3 rounded-xl border border-white/5 shadow-inner">
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-500">Model:</span>
                  <strong className="text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/30">
                    {span.model}
                  </strong>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-500">Latency:</span>
                  <strong className="text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30 tabular-nums">
                    {span.latency_ms}ms
                  </strong>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-500">Cost:</span>
                  <strong className="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30 tabular-nums">
                    ${span.cost_usd}
                  </strong>
                </div>
              </div>
            )}

            {span.outcome && (
              <div className="flex items-center space-x-2 text-slate-400 font-mono">
                <span>Execution Outcome:</span>
                <span className="text-emerald-300 font-bold bg-emerald-950/60 px-2.5 py-0.5 rounded-md border border-emerald-800">
                  {span.outcome}
                </span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

