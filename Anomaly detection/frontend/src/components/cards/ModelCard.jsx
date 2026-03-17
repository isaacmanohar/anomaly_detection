import CountUp from 'react-countup';

const gradients = {
  if: 'from-indigo-600 to-indigo-800',
  ae: 'from-purple-600 to-purple-800',
  ensemble: 'from-cyan-600 to-cyan-800',
};

const shadows = {
  if: 'shadow-indigo-500/30',
  ae: 'shadow-purple-500/30',
  ensemble: 'shadow-cyan-500/30',
};

export default function ModelCard({ type, title, subtitle, metrics, weight, strengths }) {
  return (
    <div className={`bg-gradient-to-br ${gradients[type]} rounded-2xl p-6 shadow-xl ${shadows[type]} animate-fade-in-up`}>
      <h3 className="text-xl font-bold text-white mb-1">{title}</h3>
      <p className="text-white/70 text-sm mb-4">{subtitle}</p>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-white/80 text-sm">F1-Score</span>
          <span className="text-white font-bold text-lg">
            <CountUp end={metrics.f1_score * 100} decimals={1} suffix="%" duration={1.5} />
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-white/80 text-sm">Precision</span>
          <span className="text-white font-bold text-lg">
            <CountUp end={metrics.precision * 100} decimals={1} suffix="%" duration={1.5} />
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-white/80 text-sm">Recall</span>
          <span className="text-white font-bold text-lg">
            <CountUp end={metrics.recall * 100} decimals={1} suffix="%" duration={1.5} />
          </span>
        </div>
        {weight !== undefined && (
          <div className="flex justify-between items-center pt-2 border-t border-white/20">
            <span className="text-white/80 text-sm">Ensemble Weight</span>
            <span className="text-white font-bold text-lg">{weight.toFixed(2)}</span>
          </div>
        )}
      </div>

      {strengths && (
        <div className="mt-4 pt-4 border-t border-white/20">
          <p className="text-white/80 text-sm font-medium mb-2">Strengths:</p>
          <ul className="space-y-1">
            {strengths.map((s, i) => (
              <li key={i} className="text-white/70 text-sm flex items-start gap-2">
                <span className="text-white/50 mt-0.5">-</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
