import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#22d3ee', '#f43f5e'];

export default function ThreatPieChart({ distribution }) {
  const data = [
    { name: 'Normal', value: distribution.normal },
    { name: 'Anomaly', value: distribution.anomaly },
  ];

  return (
    <div className="glass-card animate-fade-in-up">
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Threat Distribution</h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={3}
            dataKey="value"
            stroke="#1a1a2e"
            strokeWidth={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }}
            formatter={(value) => [value.toLocaleString(), '']}
          />
          <Legend
            verticalAlign="bottom"
            formatter={(value) => <span style={{ color: '#e2e8f0' }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
