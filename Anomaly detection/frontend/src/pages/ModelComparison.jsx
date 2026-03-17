import { useApi } from '@/hooks/useApi';
import { fetchModelComparison } from '@/api/client';
import Header from '@/components/layout/Header';
import ModelCard from '@/components/cards/ModelCard';
import ConfusionMatrix from '@/components/charts/ConfusionMatrix';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ModelComparison() {
  const { data, loading, error } = useApi(fetchModelComparison);

  if (loading) return <div className="animate-pulse space-y-4">{[...Array(4)].map((_, i) => <div key={i} className="h-48 bg-slate-800/50 rounded-xl" />)}</div>;
  if (error) return <div className="text-red-400 p-8">Error: {error}</div>;
  if (!data) return null;

  return (
    <div>
      <Header title="Model Comparison" subtitle="Compare Isolation Forest vs Autoencoder performance" />

      {/* Model Cards */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <ModelCard
          type="if"
          title="Isolation Forest"
          subtitle="Tree-based anomaly isolation"
          metrics={data.isolation_forest}
          weight={data.model_weights.isolation_forest}
          strengths={[
            'Fast training and inference',
            'No assumptions about data distribution',
            'Works well with high-dimensional data',
          ]}
        />
        <ModelCard
          type="ae"
          title="Autoencoder"
          subtitle="Neural network reconstruction error"
          metrics={data.autoencoder}
          weight={data.model_weights.autoencoder}
          strengths={[
            'Learns complex patterns',
            'Captures non-linear relationships',
            'Adapts to data characteristics',
          ]}
        />
      </div>

      {/* Comparison Bar Chart */}
      <div className="glass-card mb-8 animate-fade-in-up">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Performance Comparison</h3>
        <ResponsiveContainer width="100%" height={380}>
          <BarChart data={data.comparison} barGap={8}>
            <XAxis dataKey="metric" tick={{ fill: '#e2e8f0', fontSize: 13 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} unit="%" />
            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v) => [`${v}%`, '']} />
            <Legend formatter={(v) => <span style={{ color: '#e2e8f0' }}>{v}</span>} />
            <Bar dataKey="isolation_forest" name="Isolation Forest" fill="#6366f1" radius={[6, 6, 0, 0]} />
            <Bar dataKey="autoencoder" name="Autoencoder" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
            <Bar dataKey="ensemble" name="Ensemble" fill="#22c55e" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Strategy Comparison Table */}
      <div className="glass-card mb-8 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Voting Strategy Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Strategy</th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">Precision</th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">Recall</th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">F1-Score</th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">FPR</th>
              </tr>
            </thead>
            <tbody>
              {data.strategies.map((s, i) => (
                <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="py-3 px-4 text-white font-medium">{s.strategy}</td>
                  <td className="py-3 px-4 text-right text-slate-300">{s.precision}%</td>
                  <td className="py-3 px-4 text-right text-slate-300">{s.recall}%</td>
                  <td className="py-3 px-4 text-right">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${s.f1_score >= 90 ? 'bg-green-500/20 text-green-300' : 'bg-blue-500/20 text-blue-300'}`}>
                      {s.f1_score}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-slate-300">{s.fpr}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 p-4 bg-slate-800/30 rounded-lg text-sm text-slate-400 space-y-1">
          <p><span className="text-slate-300 font-medium">Majority/Unanimous:</span> Both models must agree - Higher precision, lower recall</p>
          <p><span className="text-slate-300 font-medium">Any:</span> Either model flags anomaly - Higher recall, lower precision</p>
          <p><span className="text-slate-300 font-medium">Weighted:</span> Combines scores based on model performance - Balanced approach</p>
        </div>
      </div>

      {/* Confusion Matrices */}
      <div className="grid grid-cols-2 gap-6">
        <ConfusionMatrix matrix={data.confusion_matrices.isolation_forest} title="Isolation Forest Confusion Matrix" colorScheme="blue" />
        <ConfusionMatrix matrix={data.confusion_matrices.autoencoder} title="Autoencoder Confusion Matrix" colorScheme="purple" />
      </div>
    </div>
  );
}
