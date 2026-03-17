import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function FoldBarChart({ foldScores, meanScore }) {
  const data = foldScores.map((score, i) => ({
    name: `Fold ${i + 1}`,
    f1: (score * 100).toFixed(1),
  }));

  return (
    <div className="glass-card animate-fade-in-up">
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">F1-Score by Fold</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} />
          <YAxis domain={[80, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }}
            formatter={(val) => [`${val}%`, 'F1-Score']}
          />
          <ReferenceLine y={meanScore * 100} stroke="#f43f5e" strokeDasharray="5 5" label={{ value: `Mean: ${(meanScore * 100).toFixed(1)}%`, fill: '#f43f5e', fontSize: 12 }} />
          <Bar dataKey="f1" fill="#6366f1" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
