import { useState } from 'react';
import Header from '@/components/layout/Header';
import DetectionForm from '@/components/forms/DetectionForm';
import { detectEvent } from '@/api/client';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';
import CountUp from 'react-countup';

const severityColors = {
  CRITICAL: 'bg-red-500/20 text-red-300 border-red-500/30',
  HIGH: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  MEDIUM: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  LOW: 'bg-green-500/20 text-green-300 border-green-500/30',
};

export default function RealTimeDetection() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (params) => {
    setLoading(true);
    try {
      const data = await detectEvent(params);
      setResult(data);
    } catch (err) {
      console.error('Detection failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Header
        title="Real-Time Threat Analysis"
        subtitle="Test the ensemble model with custom authentication events"
      />

      <DetectionForm onSubmit={handleSubmit} loading={loading} />

      {result && (
        <div className="mt-8 space-y-6 animate-fade-in-up">
          <h3 className="text-lg font-semibold text-white">Ensemble Analysis Results</h3>

          {/* Individual model results */}
          <div className="grid grid-cols-3 gap-4">
            <ModelResult
              title="Isolation Forest"
              prediction={result.isolation_forest.prediction}
              score={result.isolation_forest.score}
              gradient="from-indigo-600 to-indigo-800"
            />
            <ModelResult
              title="Autoencoder"
              prediction={result.autoencoder.prediction}
              score={result.autoencoder.score}
              gradient="from-purple-600 to-purple-800"
            />
            <ModelResult
              title="Ensemble Result"
              prediction={result.ensemble.prediction}
              score={result.ensemble.risk_score}
              gradient="from-cyan-600 to-cyan-800"
              isEnsemble
            />
          </div>

          {/* Ensemble metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="glass-card">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Ensemble Risk Score</p>
              <p className="text-3xl font-bold text-white">
                <CountUp end={result.ensemble.risk_score} decimals={1} duration={1} /><span className="text-lg text-slate-400">/100</span>
              </p>
            </div>
            <div className="glass-card">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Model Agreement</p>
              <p className="text-lg font-semibold text-white">
                {result.agreement === 'both_flag_anomaly' ? 'Both flag anomaly' :
                  result.agreement === 'both_say_normal' ? 'Both say normal' : 'Models disagree'}
              </p>
              <p className={`text-sm mt-1 ${result.agreement === 'models_disagree' ? 'text-yellow-400' : 'text-green-400'}`}>
                {result.agreement === 'models_disagree' ? 'LOW confidence' : 'HIGH confidence'}
              </p>
            </div>
            <div className="glass-card">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Severity</p>
              <span className={`inline-block px-3 py-1 rounded-lg text-sm font-semibold border ${severityColors[result.severity]}`}>
                {result.severity}
              </span>
            </div>
          </div>

          {/* Contributing factors */}
          <div className="glass-card">
            <h4 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-3">Analysis Details</h4>
            {result.contributing_factors.length > 0 ? (
              <div>
                <p className="text-sm text-slate-300 mb-2 font-medium">Contributing Factors:</p>
                <ul className="space-y-1">
                  {result.contributing_factors.map((factor, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5 shrink-0" />
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-sm text-emerald-400">All parameters within normal range.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ModelResult({ title, prediction, score, gradient, isEnsemble }) {
  const isAnomaly = prediction === 1;
  return (
    <div className={`bg-gradient-to-br ${gradient} rounded-2xl p-5 shadow-xl`}>
      <p className="text-white/80 text-sm font-medium mb-3">{title}</p>
      <div className="flex items-center gap-3">
        {isAnomaly ? (
          <ShieldAlert className="w-8 h-8 text-red-300" />
        ) : (
          <ShieldCheck className="w-8 h-8 text-emerald-300" />
        )}
        <div>
          <p className={`text-lg font-bold ${isAnomaly ? 'text-red-200' : 'text-emerald-200'}`}>
            {isAnomaly ? 'ANOMALY' : 'NORMAL'}
          </p>
          <p className="text-white/70 text-sm">
            Score: {typeof score === 'number' ? score.toFixed(1) : score}
          </p>
        </div>
      </div>
    </div>
  );
}
