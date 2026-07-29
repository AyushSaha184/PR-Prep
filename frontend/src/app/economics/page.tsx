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

  const totalSpend = health.reduce((acc, h) => acc + h.cost_usd, 0).toFixed(2);
  const totalCalls = health.reduce((acc, h) => acc + h.llm_calls, 0);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-slate-100">Economics & Continuous Aggregates</h1>
        <p className="text-xs text-slate-400">
          Real-time metrics precomputed from TimescaleDB continuous aggregates (agent_health_1m & pr_cost_hourly)
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricsCard title="Total Spend Today" value={`$${totalSpend}`} subtitle="Budget Cap: $50.00 / day" />
        <MetricsCard title="Total LLM Calls" value={totalCalls} subtitle="Across 4 specialists" />
        <MetricsCard title="BudgetGuard Status" value="Active" subtitle="Hard preflight protection enabled" />
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-200">Per-Agent Cost & Health Rollup (agent_health_1m)</h3>
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 font-mono border-b border-slate-800">
              <tr>
                <th className="p-3">Agent</th>
                <th className="p-3">LLM Calls</th>
                <th className="p-3">Total Cost ($)</th>
                <th className="p-3">p95 Latency (ms)</th>
                <th className="p-3">Rejection Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {health.map((row) => (
                <tr key={row.agent} className="hover:bg-slate-850">
                  <td className="p-3 font-mono font-bold uppercase text-indigo-300">{row.agent}</td>
                  <td className="p-3 font-mono">{row.llm_calls}</td>
                  <td className="p-3 font-mono text-emerald-400">${row.cost_usd.toFixed(2)}</td>
                  <td className="p-3 font-mono">{row.p95_ms}ms</td>
                  <td className="p-3 font-mono">{(row.rejection_rate * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-200">Per-PR Cost Rollup (pr_cost_hourly)</h3>
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 font-mono border-b border-slate-800">
              <tr>
                <th className="p-3">Repository / PR</th>
                <th className="p-3">Agents Used</th>
                <th className="p-3">Max Confidence</th>
                <th className="p-3">Total PR Cost ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {prCosts.map((row) => (
                <tr key={row.review_id} className="hover:bg-slate-850">
                  <td className="p-3 font-mono font-bold text-slate-200">
                    {row.repository}#PR-{row.pr_number}
                  </td>
                  <td className="p-3 font-mono">{row.agents_used}</td>
                  <td className="p-3 font-mono">{(row.max_confidence * 100).toFixed(0)}%</td>
                  <td className="p-3 font-mono text-emerald-400">${row.total_cost_usd.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
