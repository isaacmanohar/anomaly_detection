import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#f43f5e'];

export default function AttackBarChart({ attackTypes }) {
  return (
    <div className="glass-card animate-fade-in-up" style={{ animationDelay: '100ms' }}>
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Attack Types</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={attackTypes} layout="vertical" margin={{ left: 20 }}>
          <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} />
          <YAxis
            type="category"
            dataKey="type"
            tick={{ fill: '#e2e8f0', fontSize: 12 }}
            width={150}
            axisLine={{ stroke: 'rgba(99,102,241,0.2)' }}
          />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }}
          />
          <Bar dataKey="count" radius={[0, 6, 6, 0]}>
            {attackTypes.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
