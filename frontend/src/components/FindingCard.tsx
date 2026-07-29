import React from 'react';
import { Finding } from '../lib/types';
import { SeverityBadge } from './SeverityBadge';
import { ConfidenceMeter } from './ConfidenceMeter';

export const FindingCard: React.FC<{ finding: Finding }> = ({ finding }) => {
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
    </div>
  );
};
