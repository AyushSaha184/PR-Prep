import React from 'react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: string;
  icon?: string;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon,
}) => {
  return (
    <div className="glass-card glass-card-hover rounded-2xl p-5 relative space-y-3 overflow-hidden group">
      <div className="flex items-center justify-between text-xs font-semibold text-slate-400 tracking-wider uppercase font-mono">
        <div className="flex items-center space-x-2">
          {icon && <span className="text-base">{icon}</span>}
          <span>{title}</span>
        </div>
        {trend && (
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 shadow-sm">
            {trend}
          </span>
        )}
      </div>

      <div className="text-3xl font-extrabold text-white font-mono tracking-tight tabular-nums group-hover:text-indigo-200 transition-colors">
        {value}
      </div>

      {subtitle && (
        <p className="text-xs text-slate-400 font-medium tracking-tight flex items-center space-x-1.5">
          <span className="w-1 h-1 rounded-full bg-indigo-400 inline-block"></span>
          <span>{subtitle}</span>
        </p>
      )}

      {/* Subtle top glow line */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
    </div>
  );
};

