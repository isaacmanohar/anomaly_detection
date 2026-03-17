import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#a855f7', '#f59e0b', '#ef4444'];

export default function DetectionRateChart({ attackDetection }) {
  return (
    <div className="glass-card animate-fade-in-up">
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Attack-Specific Detection Rates</h3>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={attackDetection} margin={{ top: 20 }}>
          <XAxis
            dataKey="attack_type"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={{ stroke: 'rgba(99,102,241,0.2)' }}
            interval={0}
            angle={-15}
            textAnchor="end"
            height={60}
          />
          <YAxis domain={[0, 105]} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }}
            formatter={(val) => [`${val}%`, 'Detection Rate']}
          />
          <Bar dataKey="detection_rate" radius={[6, 6, 0, 0]}>
            {attackDetection.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
            <LabelList dataKey="detection_rate" position="top" fill="#e2e8f0" fontSize={12} formatter={(v) => `${v}%`} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
