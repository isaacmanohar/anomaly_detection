import Header from '@/components/layout/Header';

export default function About() {
  return (
    <div>
      <Header
        title="About This System"
        subtitle="Identity Anomaly Detection System - Architecture & Documentation"
      />

      <div className="space-y-8">
        {/* Overview */}
        <div className="glass-card animate-fade-in-up">
          <h2 className="text-xl font-bold text-white mb-3">Identity Anomaly Detection System</h2>
          <p className="text-slate-300 leading-relaxed">
            A machine learning-powered security solution using an <span className="text-indigo-300 font-medium">ensemble of two unsupervised models</span> for
            detecting anomalous user access patterns in enterprise authentication logs.
          </p>
        </div>

        {/* Ensemble Architecture */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <h3 className="text-lg font-semibold text-white mb-4">Ensemble Architecture</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Model</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Type</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Approach</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-800/50">
                  <td className="py-3 px-4 text-indigo-300 font-medium">Isolation Forest</td>
                  <td className="py-3 px-4 text-slate-300">Tree-based</td>
                  <td className="py-3 px-4 text-slate-300">Isolates outliers via random partitioning</td>
                </tr>
                <tr className="border-b border-slate-800/50">
                  <td className="py-3 px-4 text-purple-300 font-medium">Autoencoder</td>
                  <td className="py-3 px-4 text-slate-300">Neural Network</td>
                  <td className="py-3 px-4 text-slate-300">Detects via reconstruction error</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Why Ensemble */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: '150ms' }}>
          <h3 className="text-lg font-semibold text-white mb-3">Why Ensemble?</h3>
          <ul className="space-y-2 text-slate-300">
            <li className="flex items-start gap-2"><span className="text-indigo-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Robustness:</span> Different algorithms catch different anomaly patterns</span></li>
            <li className="flex items-start gap-2"><span className="text-indigo-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Confidence:</span> When both models agree, prediction confidence is higher</span></li>
            <li className="flex items-start gap-2"><span className="text-indigo-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Coverage:</span> Reduces blind spots of individual models</span></li>
          </ul>
        </div>

        {/* Voting Strategies */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <h3 className="text-lg font-semibold text-white mb-4">Voting Strategies</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Strategy</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Description</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Use Case</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-800/50">
                  <td className="py-3 px-4 text-cyan-300 font-medium">Weighted Average</td>
                  <td className="py-3 px-4 text-slate-300">Combines scores by model F1-score</td>
                  <td className="py-3 px-4 text-slate-300">Balanced detection (recommended)</td>
                </tr>
                <tr className="border-b border-slate-800/50">
                  <td className="py-3 px-4 text-cyan-300 font-medium">Majority</td>
                  <td className="py-3 px-4 text-slate-300">Both models must agree</td>
                  <td className="py-3 px-4 text-slate-300">High precision needed</td>
                </tr>
                <tr className="border-b border-slate-800/50">
                  <td className="py-3 px-4 text-cyan-300 font-medium">Any</td>
                  <td className="py-3 px-4 text-slate-300">Either model flags</td>
                  <td className="py-3 px-4 text-slate-300">High recall needed</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Key Features */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: '250ms' }}>
          <h3 className="text-lg font-semibold text-white mb-3">Key Features</h3>
          <ul className="space-y-2 text-slate-300">
            <li className="flex items-start gap-2"><span className="text-cyan-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Dual ML Models:</span> Isolation Forest + Autoencoder ensemble</span></li>
            <li className="flex items-start gap-2"><span className="text-cyan-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Real-Time Processing:</span> Sub-millisecond inference latency</span></li>
            <li className="flex items-start gap-2"><span className="text-cyan-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Explainable AI:</span> SHAP-based explanations for flagged anomalies</span></li>
            <li className="flex items-start gap-2"><span className="text-cyan-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Multi-Attack Detection:</span> Identifies 5 types of security threats</span></li>
            <li className="flex items-start gap-2"><span className="text-cyan-400 font-bold mt-0.5">-</span><span><span className="text-white font-medium">Risk Scoring:</span> 0-100 risk scores for prioritization</span></li>
          </ul>
        </div>

        {/* Attack Types */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <h3 className="text-lg font-semibold text-white mb-4">Attack Types Detected</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Attack Type</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Description</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Credential Stuffing', 'Multiple failed login attempts from unusual sources'],
                  ['Impossible Travel', 'Login from geographically impossible locations'],
                  ['Privilege Escalation', 'Unauthorized access to elevated resources'],
                  ['After Hours Exfiltration', 'Large data transfers outside business hours'],
                  ['Lateral Movement', 'Unusual cross-system access patterns'],
                ].map(([type, desc], i) => (
                  <tr key={i} className="border-b border-slate-800/50">
                    <td className="py-3 px-4 text-rose-300 font-medium">{type}</td>
                    <td className="py-3 px-4 text-slate-300">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Architecture Diagram */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: '350ms' }}>
          <h3 className="text-lg font-semibold text-white mb-4">Technical Architecture</h3>
          <pre className="text-sm text-indigo-300 font-mono bg-slate-900/50 rounded-lg p-6 overflow-x-auto border border-slate-700/30">
{`  ┌─────────────────┐     ┌──────────────────┐
  │  Auth Logs       │────▶│  Data Pipeline   │
  │  (CSV/Stream)    │     │  (Feature Eng.)  │
  └─────────────────┘     └────────┬─────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  │                                 │
                  ▼                                 ▼
         ┌────────────────┐               ┌────────────────┐
         │ Isolation      │               │  Autoencoder   │
         │ Forest         │               │  (Deep Learning)│
         └───────┬────────┘               └───────┬────────┘
                 │                                 │
                 └────────────┬────────────────────┘
                              │
                  ┌───────────▼───────────┐
                  │  Ensemble Voting      │
                  │  (Weighted/Majority)  │
                  └───────────┬───────────┘
                              │
                  ┌───────────▼───────────┐
                  │  Alert System         │
                  │  (Risk Scoring)       │
                  └───────────────────────┘`}
          </pre>
        </div>

        {/* Performance Table */}
        <div className="glass-card animate-fade-in-up" style={{ animationDelay: '400ms' }}>
          <h3 className="text-lg font-semibold text-white mb-4">Model Performance (5-Fold Cross-Validation)</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Metric</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Target</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Achieved</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['F1-Score', '85-95%', '~90% \u00b1 1%'],
                  ['Precision', '>82%', '~86% \u00b1 3%'],
                  ['Recall', '>89%', '~94% \u00b1 3%'],
                  ['False Positive Rate', '<12%', '<1%'],
                  ['Latency', '<100ms', '<5ms'],
                ].map(([metric, target, achieved], i) => (
                  <tr key={i} className="border-b border-slate-800/50">
                    <td className="py-3 px-4 text-white font-medium">{metric}</td>
                    <td className="py-3 px-4 text-slate-300">{target}</td>
                    <td className="py-3 px-4 text-emerald-400 font-medium">{achieved}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="text-center text-slate-500 text-sm py-4">
          Built with Python, Scikit-learn, TensorFlow, React, and FastAPI
        </div>
      </div>
    </div>
  );
}
