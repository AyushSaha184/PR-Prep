import React from 'react';
import { Severity } from '../lib/types';

const SEVERITY_STYLES: Record<Severity, string> = {
  CRITICAL: 'bg-red-900/80 text-red-200 border-red-500 font-bold animate-pulse',
  HIGH: 'bg-orange-900/60 text-orange-200 border-orange-500 font-semibold',
  MEDIUM: 'bg-amber-900/50 text-amber-200 border-amber-500',
  LOW: 'bg-blue-900/40 text-blue-200 border-blue-500',
  INFO: 'bg-slate-800 text-slate-300 border-slate-600',
};

export const SeverityBadge: React.FC<{ severity: Severity }> = ({ severity }) => {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${
        SEVERITY_STYLES[severity] || SEVERITY_STYLES.INFO
      }`}
      aria-label={`Severity: ${severity}`}
    >
      {severity}
    </span>
  );
};
