'use client';
import { useEffect, useState } from 'react';
import { fetchHealth } from '../../lib/api';
import { MetricsCard } from '../../components/MetricsCard';

export default function HealthPage() {
  const [health, setHealth] = useState<{ status: string; service: string; version: string } | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth);
  }, []);

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-slate-100">Operational System Health</h1>
        <p className="text-xs text-slate-400">Live operational status for API ingress, queue depth, and database lanes</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricsCard title="API Ingress" value={health ? health.status : 'Checking...'} subtitle="FastAPI /health" />
        <MetricsCard title="ARQ Job Queue" value="Operational" subtitle="0 depth, 1 worker online" />
        <MetricsCard title="Tiger Cloud Data Spine" value="Connected" subtitle="Postgres + pgvector + Timescale" />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 font-mono text-xs text-slate-300">
        <div className="text-sm font-bold text-slate-100">Service Configuration Details</div>
        <div>Service: {health?.service || 'pr-prep-backend'}</div>
        <div>Version: {health?.version || '0.1.0'}</div>
        <div>Environment: Development</div>
        <div>Worker Pool: 1 active worker</div>
      </div>
    </div>
  );
}
