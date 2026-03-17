import CountUp from 'react-countup';

export default function MetricCard({ title, value, suffix = '', delta, icon: Icon, delay = 0, decimals = 0 }) {
  const numericValue = typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value;

  return (
    <div
      className="glass-card animate-fade-in-up hover:border-indigo-500/40 transition-all duration-300"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-2">{title}</p>
          <p className="text-2xl font-bold text-white">
            {!isNaN(numericValue) ? (
              <CountUp end={numericValue} duration={1.5} separator="," decimals={decimals} suffix={suffix} delay={delay / 1000} />
            ) : (
              <span>{value}{suffix}</span>
            )}
          </p>
          {delta && (
            <p className="text-sm text-cyan-400 mt-1">{delta}</p>
          )}
        </div>
        {Icon && (
          <div className="p-2 bg-indigo-500/10 rounded-lg">
            <Icon className="w-5 h-5 text-indigo-400" />
          </div>
        )}
      </div>
    </div>
  );
}
