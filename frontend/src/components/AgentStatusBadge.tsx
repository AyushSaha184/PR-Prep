import React from 'react';
import { AgentType } from '../lib/types';

const AGENT_COLORS: Record<AgentType, string> = {
  security: 'bg-red-950 text-red-300 border-red-800',
  quality: 'bg-blue-950 text-blue-300 border-blue-800',
  tests: 'bg-purple-950 text-purple-300 border-purple-800',
  docs: 'bg-emerald-950 text-emerald-300 border-emerald-800',
  aggregator: 'bg-amber-950 text-amber-300 border-amber-800',
};

export const AgentStatusBadge: React.FC<{ agent: AgentType }> = ({ agent }) => {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs border font-medium uppercase ${AGENT_COLORS[agent]}`}>
      {agent}
    </span>
  );
};
