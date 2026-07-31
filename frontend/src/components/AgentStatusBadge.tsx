import React from 'react';
import { AgentType } from '../lib/types';

const AGENT_CONFIG: Record<AgentType, { icon: string; style: string }> = {
  security: {
    icon: '🛡️',
    style: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
  },
  quality: {
    icon: '✨',
    style: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
  },
  tests: {
    icon: '🧪',
    style: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  },
  docs: {
    icon: '📚',
    style: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  },
  aggregator: {
    icon: '⚖️',
    style: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
  },
};

export const AgentStatusBadge: React.FC<{ agent: AgentType }> = ({ agent }) => {
  const config = AGENT_CONFIG[agent] || AGENT_CONFIG.aggregator;

  return (
    <span
      className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md text-[10px] font-mono border font-semibold uppercase tracking-wider ${config.style}`}
    >
      <span>{config.icon}</span>
      <span>{agent}</span>
    </span>
  );
};

