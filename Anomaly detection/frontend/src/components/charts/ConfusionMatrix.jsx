const colorScales = {
  blue: ['rgba(99,102,241,0.1)', 'rgba(99,102,241,0.3)', 'rgba(99,102,241,0.5)', 'rgba(99,102,241,0.8)'],
  purple: ['rgba(139,92,246,0.1)', 'rgba(139,92,246,0.3)', 'rgba(139,92,246,0.5)', 'rgba(139,92,246,0.8)'],
  green: ['rgba(34,197,94,0.1)', 'rgba(34,197,94,0.3)', 'rgba(34,197,94,0.5)', 'rgba(34,197,94,0.8)'],
};

export default function ConfusionMatrix({ matrix, title, colorScheme = 'blue' }) {
  const { true_negatives: tn, false_positives: fp, false_negatives: fn, true_positives: tp } = matrix;
  const maxVal = Math.max(tn, fp, fn, tp);
  const colors = colorScales[colorScheme];

  const getColor = (val) => {
    const ratio = val / maxVal;
    if (ratio > 0.7) return colors[3];
    if (ratio > 0.4) return colors[2];
    if (ratio > 0.1) return colors[1];
    return colors[0];
  };

  const cells = [
    [{ label: 'TN', value: tn }, { label: 'FP', value: fp }],
    [{ label: 'FN', value: fn }, { label: 'TP', value: tp }],
  ];

  return (
    <div className="glass-card animate-fade-in-up">
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">{title}</h3>
      <div className="flex">
        {/* Y-axis label */}
        <div className="flex flex-col justify-center mr-2">
          <span className="text-xs text-slate-400 transform -rotate-90 whitespace-nowrap">Actual</span>
        </div>
        <div className="flex-1">
          {/* X-axis labels */}
          <div className="grid grid-cols-2 gap-1 mb-1 ml-16">
            <span className="text-xs text-slate-400 text-center">Normal</span>
            <span className="text-xs text-slate-400 text-center">Anomaly</span>
          </div>
          <div className="flex">
            <div className="flex flex-col justify-around mr-1 w-14">
              <span className="text-xs text-slate-400 text-right">Normal</span>
              <span className="text-xs text-slate-400 text-right">Anomaly</span>
            </div>
            <div className="grid grid-cols-2 gap-1 flex-1">
              {cells.flat().map(({ label, value }, i) => (
                <div
                  key={i}
                  className="rounded-lg p-4 flex flex-col items-center justify-center border border-slate-700/30"
                  style={{ backgroundColor: getColor(value) }}
                >
                  <span className="text-lg font-bold text-white">{value.toLocaleString()}</span>
                  <span className="text-xs text-slate-400 mt-1">{label}</span>
                </div>
              ))}
            </div>
          </div>
          <p className="text-xs text-slate-400 text-center mt-1">Predicted</p>
        </div>
      </div>
    </div>
  );
}
