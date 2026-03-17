import { useApi } from '@/hooks/useApi';
import { fetchDashboard } from '@/api/client';
import Header from '@/components/layout/Header';
import MetricCard from '@/components/cards/MetricCard';
import ThreatPieChart from '@/components/charts/ThreatPieChart';
import AttackBarChart from '@/components/charts/AttackBarChart';
import TimelineChart from '@/components/charts/TimelineChart';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, ShieldAlert, Target, Crosshair, Eye } from 'lucide-react';
import CountUp from 'react-countup';

export default function Dashboard() {
  const { data, loading, error } = useApi(fetchDashboard);

  if (loading) return <LoadingSkeleton />;
  if (error) return <div className="text-red-400 p-8">Error loading dashboard: {error}</div>;
  if (!data) return null;

  const agreementData = [
    { name: 'Both Agree (Anomaly)', value: data.model_agreement.both_anomaly },
    { name: 'Both Agree (Normal)', value: data.model_agreement.both_normal },
    { name: 'Models Disagree', value: data.model_agreement.disagree },
  ];

  return (
    <div>
      <Header
        title="Identity Anomaly Detection System"
        subtitle="Ensemble ML-powered security monitoring with Isolation Forest + Autoencoder"
      />

      {/* Key Metrics */}
      <div className="grid grid-cols-5 gap-4 mb-8">
        <MetricCard title="Total Events" value={data.total_events} icon={Activity} delay={0} />
        <MetricCard title="Threats Detected" value={data.threats_detected} delta={`${(data.threats_detected / data.total_events * 100).toFixed(1)}%`} icon={ShieldAlert} delay={100} />
        <MetricCard title="F1-Score" value={data.cv_metrics.f1 * 100} suffix="%" icon={Target} delay={200} decimals={1} delta={`\u00b1 ${(data.cv_metrics.std.f1_score * 100).toFixed(1)}%`} />
        <MetricCard title="Precision" value={data.cv_metrics.precision * 100} suffix="%" icon={Crosshair} delay={300} decimals={1} delta={`\u00b1 ${(data.cv_metrics.std.precision * 100).toFixed(1)}%`} />
        <MetricCard title="Recall" value={data.cv_metrics.recall * 100} suffix="%" icon={Eye} delay={400} decimals={1} delta={`\u00b1 ${(data.cv_metrics.std.recall * 100).toFixed(1)}%`} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <ThreatPieChart distribution={data.threat_distribution} />
        <AttackBarChart attackTypes={data.attack_types} />
      </div>

      {/* Model Agreement */}
      <div className="glass-card mb-8 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Model Agreement Analysis</h3>
        <div className="grid grid-cols-3 gap-6">
          <div className="space-y-3">
            {Object.entries(data.model_agreement).map(([key, val]) => {
              const labels = { both_anomaly: 'Both Agree (Anomaly)', both_normal: 'Both Agree (Normal)', disagree: 'Models Disagree' };
              return (
                <div key={key} className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/30">
                  <p className="text-xs text-slate-400 uppercase tracking-wider">{labels[key]}</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    <CountUp end={val} separator="," duration={1.5} />
                  </p>
                  <p className="text-sm text-cyan-400">{(val / data.total_events * 100).toFixed(1)}%</p>
                </div>
              );
            })}
          </div>
          <div className="col-span-2">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={agreementData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} paddingAngle={3} dataKey="value" stroke="#1a1a2e" strokeWidth={2}>
                  <Cell fill="#f43f5e" />
                  <Cell fill="#22d3ee" />
                  <Cell fill="#fbbf24" />
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }} />
                <Legend formatter={(v) => <span style={{ color: '#e2e8f0' }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <TimelineChart timeline={data.timeline} />

      {/* Recent Threats Table */}
      <div className="glass-card mt-8 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Recent Threat Detections</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Time</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">User</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Department</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Threat Type</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Location</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Risk Score</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_threats.map((threat, i) => (
                <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 text-slate-300">{threat.timestamp.slice(0, 16)}</td>
                  <td className="py-3 px-4 text-white font-medium">{threat.user_name}</td>
                  <td className="py-3 px-4 text-slate-300">{threat.department}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 rounded-md text-xs font-medium bg-rose-500/20 text-rose-300 border border-rose-500/30">
                      {threat.anomaly_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{threat.location}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-700/50 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${threat.risk_score >= 75 ? 'bg-red-500' : threat.risk_score >= 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                          style={{ width: `${threat.risk_score}%` }}
                        />
                      </div>
                      <span className="text-white font-medium">{threat.risk_score}</span>
                    </div>
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

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-12 bg-slate-800/50 rounded-xl w-96" />
      <div className="grid grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => <div key={i} className="h-28 bg-slate-800/50 rounded-xl" />)}
      </div>
      <div className="grid grid-cols-2 gap-6">
        {[...Array(2)].map((_, i) => <div key={i} className="h-72 bg-slate-800/50 rounded-xl" />)}
      </div>
      <div className="h-80 bg-slate-800/50 rounded-xl" />
    </div>
  );
}
