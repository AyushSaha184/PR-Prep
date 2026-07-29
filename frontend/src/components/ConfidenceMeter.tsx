import React from 'react';

export const ConfidenceMeter: React.FC<{ score: number }> = ({ score }) => {
  const percentage = Math.round(score * 100);
  let color = 'bg-emerald-500';
  if (score < 0.7) color = 'bg-rose-500';
  else if (score < 0.85) color = 'bg-amber-500';

  return (
    <div className="flex items-center space-x-2" title={`Confidence score: ${percentage}%`}>
      <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
        <div className={`h-full ${color} transition-all duration-500`} style={{ width: `${percentage}%` }} />
      </div>
      <span className="text-xs font-mono font-medium text-slate-300">{percentage}%</span>
    </div>
  );
};
