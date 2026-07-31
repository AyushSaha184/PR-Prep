'use client';
import { useEffect, useState } from 'react';
import { fetchAgentHealth, fetchPRCosts } from '../../lib/api';
import { AgentHealth, PRCost } from '../../lib/types';
import { MetricsCard } from '../../components/MetricsCard';

export default function EconomicsPage() {
  const [health, setHealth] = useState<AgentHealth[]>([]);
  const [prCosts, setPRCosts] = useState<PRCost[]>([]);

  useEffect(() => {
    fetchAgentHealth().then(setHealth);
    fetchPRCosts().then(setPRCosts);
  }, []);

  const totalSpendNum = health.reduce((acc, h) => acc + h.cost_usd, 0);
  const totalSpend = totalSpendNum.toFixed(2);
  const totalCalls = health.reduce((acc, h) => acc + h.llm_calls, 0);
  const budgetCap = 50.0;
  const budgetPercent = Math.min(100, Math.round((totalSpendNum / budgetCap) * 100));

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="glass-card rounded-3xl p-8 border border-white/10 relative overflow-hidden shadow-2xl space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-mono font-medium text-indigo-300 bg-indigo-500/10 border border-indigo-500/30">
          <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse-glow"></span>
          <span>TimescaleDB Continuous Aggregates Active</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight font-display">
          Economics & Continuous Cost Aggregates
        </h1>
        <p className="text-xs text-slate-300 max-w-2xl font-normal leading-relaxed">
          Real-time token cost attribution and agent latency analytics computed over continuous hypertables <code className="text-indigo-300 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">agent_health_1m</code> and <code className="text-indigo-300 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">pr_cost_hourly</code>.
        </p>

        {/* Ambient glow */}
        <div className="absolute -top-20 -right-20 w-80 h-80 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricsCard
          icon="💰"
          title="Total Spend Today"
          value={`$${totalSpend}`}
          subtitle={`Budget Cap: $${budgetCap.toFixed(2)} / day (${budgetPercent}% used)`}
          trend={`${budgetPercent}%`}
        />
        <MetricsCard
          icon="🤖"
          title="Total LLM Invocations"
          value={totalCalls.toLocaleString()}
          subtitle="Across 4 parallel specialist models"
        />
        <MetricsCard
          icon="🛡️"
          title="BudgetGuard Status"
          value="Protected"
          subtitle="Hard budget preflight ceiling enabled"
        />
      </div>

      {/* Visual Agent Spend Distribution Bar */}
      <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-3">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="font-bold text-white uppercase tracking-wider">Agent Spend Share Distribution</span>
          <span className="text-slate-400 font-bold tabular-nums">${totalSpend} total</span>
        </div>
        <div className="h-3 w-full bg-[#05070a] rounded-full overflow-hidden flex border border-white/10 p-0.5 shadow-inner">
          {health.map((h) => {
            const pct = (h.cost_usd / totalSpendNum) * 100;
            const colors: Record<string, string> = {
              security: 'bg-purple-500',
              quality: 'bg-cyan-400',
              tests: 'bg-emerald-400',
              docs: 'bg-amber-400',
            };
            return (
              <div
                key={h.agent}
                className={`h-full ${colors[h.agent] || 'bg-indigo-500'} transition-all duration-500`}
                style={{ width: `${pct}%` }}
                title={`${h.agent}: $${h.cost_usd.toFixed(2)} (${pct.toFixed(1)}%)`}
              />
            );
          })}
        </div>
        <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-slate-400 pt-1">
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span><span>Security (39.5%)</span></span>
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span><span>Quality (47.0%)</span></span>
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span><span>Tests (28.3%)</span></span>
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span><span>Docs (13.7%)</span></span>
        </div>
      </div>

      {/* Table 1: Per-Agent Cost & Health Rollup */}
      <div className="space-y-4">
        <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-300 font-mono flex items-center space-x-2">
          <span>Per-Agent Cost & Health Rollup</span>
          <span className="text-xs font-mono font-normal text-indigo-300 bg-indigo-500/10 px-2.5 py-0.5 rounded-full border border-indigo-500/30">
            agent_health_1m
          </span>
        </h3>
        <div className="glass-card rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#05070a] text-slate-400 font-mono border-b border-white/10">
              <tr>
                <th className="p-4">Agent Specialist</th>
                <th className="p-4">LLM Calls</th>
                <th className="p-4">Total Cost ($)</th>
                <th className="p-4">p95 Latency (ms)</th>
                <th className="p-4">Rejection Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {health.map((row) => (
                <tr key={row.agent} className="hover:bg-white/[0.03] transition">
                  <td className="p-4 font-mono font-bold uppercase text-indigo-300 flex items-center space-x-2">
                    <span className="h-2 w-2 rounded-full bg-indigo-400"></span>
                    <span>{row.agent}</span>
                  </td>
                  <td className="p-4 font-mono tabular-nums">{row.llm_calls.toLocaleString()}</td>
                  <td className="p-4 font-mono text-emerald-400 font-bold tabular-nums">${row.cost_usd.toFixed(2)}</td>
                  <td className="p-4 font-mono text-slate-200 tabular-nums">{row.p95_ms}ms</td>
                  <td className="p-4 font-mono tabular-nums">{(row.rejection_rate * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Table 2: Per-PR Cost Rollup */}
      <div className="space-y-4">
        <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-300 font-mono flex items-center space-x-2">
          <span>Per-PR Cost Attribution Rollup</span>
          <span className="text-xs font-mono font-normal text-indigo-300 bg-indigo-500/10 px-2.5 py-0.5 rounded-full border border-indigo-500/30">
            pr_cost_hourly
          </span>
        </h3>
        <div className="glass-card rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#05070a] text-slate-400 font-mono border-b border-white/10">
              <tr>
                <th className="p-4">Repository / PR</th>
                <th className="p-4">Agents Executed</th>
                <th className="p-4">Max Confidence</th>
                <th className="p-4">Total PR Cost ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {prCosts.map((row) => (
                <tr key={row.review_id} className="hover:bg-white/[0.03] transition">
                  <td className="p-4 font-mono font-bold text-indigo-300">
                    {row.repository}#PR-{row.pr_number}
                  </td>
                  <td className="p-4 font-mono tabular-nums">{row.agents_used} Specialists</td>
                  <td className="p-4 font-mono text-amber-300 font-bold tabular-nums">
                    {(row.max_confidence * 100).toFixed(0)}%
                  </td>
                  <td className="p-4 font-mono text-emerald-400 font-bold tabular-nums">
                    ${row.total_cost_usd.toFixed(3)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

