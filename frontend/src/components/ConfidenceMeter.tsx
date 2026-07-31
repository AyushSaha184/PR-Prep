import React from 'react';

export const ConfidenceMeter: React.FC<{ score: number }> = ({ score }) => {
  const percentage = Math.round(score * 100);

  const getGradient = (pct: number) => {
    if (pct >= 90) return 'from-emerald-500 to-teal-400 shadow-emerald-500/40 text-emerald-400';
    if (pct >= 80) return 'from-cyan-500 to-blue-400 shadow-cyan-500/40 text-cyan-400';
    return 'from-amber-500 to-orange-400 shadow-amber-500/40 text-amber-400';
  };

  const styleClass = getGradient(percentage);

  return (
    <div
      className="flex items-center space-x-2.5 bg-black/30 px-3 py-1 rounded-full border border-white/5"
      title={`Confidence Score: ${percentage}% (Gating Threshold: 85%)`}
    >
      <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider font-mono">
        Confidence
      </span>
      <div className="w-20 bg-slate-900 rounded-full h-2 p-0.5 border border-white/10 overflow-hidden shadow-inner">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${styleClass} transition-all duration-500 shadow-sm`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className={`text-xs font-mono font-bold ${styleClass.split(' ').pop()} tabular-nums`}>
        {percentage}%
      </span>
    </div>
  );
};

