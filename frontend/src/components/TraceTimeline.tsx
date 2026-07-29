import React from 'react';
import { TraceSpan } from '../lib/types';
import { AgentStatusBadge } from './AgentStatusBadge';

export const TraceTimeline: React.FC<{ spans: TraceSpan[] }> = ({ spans }) => {
  return (
    <div className="space-y-4">
      {spans.map((span) => (
        <div key={span.span_id} className="flex items-start space-x-3 bg-slate-900 border border-slate-800 rounded-lg p-3">
          <div className="pt-0.5">
            <AgentStatusBadge agent={span.agent} />
          </div>
          <div className="flex-1 space-y-1 text-xs">
            <div className="flex items-center justify-between text-slate-300">
              <span className="font-mono font-medium">{span.event_type}</span>
              <span className="text-slate-500 font-mono">{new Date(span.timestamp).toLocaleTimeString()}</span>
            </div>
            {span.model && (
              <div className="text-slate-400 font-mono">
                Model: <span className="text-slate-200">{span.model}</span> | Latency: <span className="text-slate-200">{span.latency_ms}ms</span> | Cost: <span className="text-emerald-400">${span.cost_usd}</span>
              </div>
            )}
            {span.outcome && (
              <div className="text-slate-400">
                Outcome: <span className="text-indigo-300 font-semibold">{span.outcome}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
