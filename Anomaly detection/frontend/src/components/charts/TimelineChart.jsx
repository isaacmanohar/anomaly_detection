import { AreaChart, Area, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function TimelineChart({ timeline }) {
  return (
    <div className="glass-card animate-fade-in-up" style={{ animationDelay: '200ms' }}>
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Threat Activity Timeline</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={timeline}>
          <defs>
            <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={{ stroke: 'rgba(99,102,241,0.2)' }}
            tickFormatter={(d) => d.slice(5)}
          />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }}
          />
          <Area type="monotone" dataKey="total" stroke="#6366f1" fill="url(#colorTotal)" strokeWidth={2} name="Total Events" />
          <Line type="monotone" dataKey="anomalies" stroke="#f43f5e" strokeWidth={2.5} dot={{ r: 3, fill: '#f43f5e' }} name="Threats" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
