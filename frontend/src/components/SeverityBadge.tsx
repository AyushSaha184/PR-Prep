import React from 'react';
import { Severity } from '../lib/types';

const SEVERITY_STYLES: Record<Severity, { bg: string; text: string; border: string; dot: string }> = {
  CRITICAL: {
    bg: 'bg-rose-500/10',
    text: 'text-rose-400',
    border: 'border-rose-500/30',
    dot: 'bg-rose-500 shadow-rose-500/50',
  },
  HIGH: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    dot: 'bg-amber-500 shadow-amber-500/50',
  },
  MEDIUM: {
    bg: 'bg-yellow-500/10',
    text: 'text-yellow-300',
    border: 'border-yellow-500/30',
    dot: 'bg-yellow-400 shadow-yellow-400/50',
  },
  LOW: {
    bg: 'bg-sky-500/10',
    text: 'text-sky-300',
    border: 'border-sky-500/30',
    dot: 'bg-sky-400 shadow-sky-400/50',
  },
  INFO: {
    bg: 'bg-slate-500/10',
    text: 'text-slate-400',
    border: 'border-slate-500/30',
    dot: 'bg-slate-400 shadow-slate-400/50',
  },
};

export const SeverityBadge: React.FC<{ severity: Severity }> = ({ severity }) => {
  const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.INFO;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-mono border font-semibold tracking-wider transition-all duration-200 ${style.bg} ${style.text} ${style.border}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot} mr-1.5 shadow-sm`}></span>
      {severity}
    </span>
  );
};

