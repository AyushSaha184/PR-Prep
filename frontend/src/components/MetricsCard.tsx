import React from 'react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({ title, value, subtitle, icon }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-2">
      <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
        <span>{title}</span>
        {icon && <span className="text-slate-500">{icon}</span>}
      </div>
      <div className="text-2xl font-bold text-slate-100 font-mono">{value}</div>
      {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
};
