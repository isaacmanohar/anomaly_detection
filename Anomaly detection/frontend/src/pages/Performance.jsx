import { useApi } from '@/hooks/useApi';
import { fetchPerformance } from '@/api/client';
import Header from '@/components/layout/Header';
import MetricCard from '@/components/cards/MetricCard';
import ConfusionMatrix from '@/components/charts/ConfusionMatrix';
import FoldBarChart from '@/components/charts/FoldBarChart';
import DetectionRateChart from '@/components/charts/DetectionRateChart';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Crosshair, Eye, Target, AlertTriangle } from 'lucide-react';

export default function Performance() {
  const { data, loading, error } = useApi(fetchPerformance);

  if (loading) return <div className="animate-pulse space-y-4">{[...Array(5)].map((_, i) => <div key={i} className="h-40 bg-slate-800/50 rounded-xl" />)}</div>;
  if (error) return <div className="text-red-400 p-8">Error: {error}</div>;
  if (!data) return null;

  const cv = data.cv_results;

  const cvVsTargets = [
    { metric: 'Precision', achieved: data.achieved.precision, target: data.targets.precision },
    { metric: 'Recall', achieved: data.achieved.recall, target: data.targets.recall },
    { metric: 'F1-Score', achieved: data.achieved.f1_score, target: data.targets.f1_score },
  ];

  return (
    <div>
      <Header title="Ensemble Performance" subtitle="5-Fold Cross-Validation Results (Honest Evaluation)" />

      {/* CV Metric Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Precision" value={cv.mean.precision * 100} suffix="%" decimals={1}
          delta={`\u00b1 ${(cv.std.precision * 100).toFixed(1)}% | Target: 82%+`}
          icon={Crosshair} delay={0}
        />
        <MetricCard
          title="Recall" value={cv.mean.recall * 100} suffix="%" decimals={1}
          delta={`\u00b1 ${(cv.std.recall * 100).toFixed(1)}% | Target: 89%+`}
          icon={Eye} delay={100}
        />
        <MetricCard
          title="F1-Score" value={cv.mean.f1_score * 100} suffix="%" decimals={1}
          delta={`\u00b1 ${(cv.std.f1_score * 100).toFixed(1)}% | Target: 85-95%`}
          icon={Target} delay={200}
        />
        <MetricCard
          title="False Positive Rate" value={cv.mean.false_positive_rate * 100} suffix="%" decimals={2}
          delta={`\u00b1 ${(cv.std.false_positive_rate * 100).toFixed(2)}% | Target: <12%`}
          icon={AlertTriangle} delay={300}
        />
      </div>

      {/* Fold Results */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Fold Table */}
        <div className="glass-card animate-fade-in-up">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Cross-Validation Fold Results</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left py-2 px-3 text-slate-400 font-medium">Fold</th>
                  <th className="text-right py-2 px-3 text-slate-400 font-medium">Precision</th>
                  <th className="text-right py-2 px-3 text-slate-400 font-medium">Recall</th>
                  <th className="text-right py-2 px-3 text-slate-400 font-medium">F1-Score</th>
                  <th className="text-right py-2 px-3 text-slate-400 font-medium">FPR</th>
                </tr>
              </thead>
              <tbody>
                {cv.fold_metrics.precision.map((_, i) => (
                  <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                    <td className="py-2 px-3 text-white font-medium">Fold {i + 1}</td>
                    <td className="py-2 px-3 text-right text-slate-300">{(cv.fold_metrics.precision[i] * 100).toFixed(1)}%</td>
                    <td className="py-2 px-3 text-right text-slate-300">{(cv.fold_metrics.recall[i] * 100).toFixed(1)}%</td>
                    <td className="py-2 px-3 text-right text-slate-300">{(cv.fold_metrics.f1_score[i] * 100).toFixed(1)}%</td>
                    <td className="py-2 px-3 text-right text-slate-300">{(cv.fold_metrics.false_positive_rate[i] * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Fold Bar Chart */}
        <FoldBarChart foldScores={cv.fold_metrics.f1_score} meanScore={cv.mean.f1_score} />
      </div>

      {/* Confusion Matrix + CV vs Targets */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <ConfusionMatrix matrix={data.confusion_matrix} title="Confusion Matrix (Full Dataset)" colorScheme="green" />

        <div className="glass-card animate-fade-in-up">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">CV Performance vs Targets</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cvVsTargets} barGap={8}>
              <XAxis dataKey="metric" tick={{ fill: '#e2e8f0', fontSize: 13 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(99,102,241,0.2)' }} unit="%" />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v) => [`${v}%`, '']} />
              <Legend formatter={(v) => <span style={{ color: '#e2e8f0' }}>{v}</span>} />
              <Bar dataKey="achieved" name="Achieved (CV)" fill="#22c55e" radius={[6, 6, 0, 0]} />
              <Bar dataKey="target" name="Target" fill="#ef4444" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Attack Detection Rates */}
      <DetectionRateChart attackDetection={data.attack_detection} />

      {/* Detailed Stats */}
      <div className="glass-card mt-8 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Detailed Statistics</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Metric</th>
                <th className="text-right py-2 px-4 text-slate-400 font-medium">Value</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Total Events', data.detailed_stats.total_predictions.toLocaleString()],
                ['True Positives', data.detailed_stats.true_positives.toLocaleString()],
                ['True Negatives', data.detailed_stats.true_negatives.toLocaleString()],
                ['False Positives', data.detailed_stats.false_positives.toLocaleString()],
                ['False Negatives', data.detailed_stats.false_negatives.toLocaleString()],
                ['Inference Latency (ms)', data.detailed_stats.latency_ms],
                ['Throughput (events/sec)', data.detailed_stats.throughput.toLocaleString()],
              ].map(([metric, value], i) => (
                <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="py-2 px-4 text-slate-300">{metric}</td>
                  <td className="py-2 px-4 text-right text-white font-medium">{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
