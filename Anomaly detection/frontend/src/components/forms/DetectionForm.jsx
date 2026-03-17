import { useState } from 'react';
import { Search, Zap, Shield, FileWarning, Globe, UserMinus, Calendar } from 'lucide-react';

const LOCATIONS = ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'New York', 'London', 'Moscow', 'Beijing'];

const presets = {
  normal: { failed_attempts: 0, resources_accessed: 10, download_mb: 50, privilege_level: 1, hour: 14, is_weekend: false, location: 'Mumbai', ip_type: 'internal', sensitive_data: false },
  credential: { failed_attempts: 87, resources_accessed: 0, download_mb: 0, privilege_level: 1, hour: 15, is_weekend: false, location: 'Moscow', ip_type: 'external', sensitive_data: false },
  exfiltration: { failed_attempts: 0, resources_accessed: 432, download_mb: 6330, privilege_level: 2, hour: 2, is_weekend: false, location: 'Mumbai', ip_type: 'internal', sensitive_data: true },
  impossible_travel: { failed_attempts: 2, resources_accessed: 5, download_mb: 20, privilege_level: 1, hour: 10, is_weekend: false, location: 'New York', ip_type: 'external', sensitive_data: false },
  insider_threat: { failed_attempts: 0, resources_accessed: 150, download_mb: 2500, privilege_level: 3, hour: 23, is_weekend: true, location: 'Mumbai', ip_type: 'internal', sensitive_data: true },
  weekend_access: { failed_attempts: 1, resources_accessed: 20, download_mb: 100, privilege_level: 1, hour: 14, is_weekend: true, location: 'Delhi', ip_type: 'internal', sensitive_data: true },
};

export default function DetectionForm({ onSubmit, loading }) {
  const [form, setForm] = useState(presets.normal);
  const [strategy, setStrategy] = useState('weighted');

  const update = (key, value) => setForm(prev => ({ ...prev, [key]: value }));
  const applyPreset = (preset) => setForm(presets[preset]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...form, strategy });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* ... (inputs remain the same) ... */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column */}
        <div className="glass-card space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Event Parameters</h3>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Failed Login Attempts: {form.failed_attempts}</label>
            <input
              type="range" min="0" max="200" value={form.failed_attempts}
              onChange={(e) => update('failed_attempts', parseInt(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Resources Accessed: {form.resources_accessed}</label>
            <input
              type="range" min="1" max="500" value={form.resources_accessed}
              onChange={(e) => update('resources_accessed', parseInt(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Data Downloaded (MB): {form.download_mb}</label>
            <input
              type="range" min="0" max="5000" value={form.download_mb}
              onChange={(e) => update('download_mb', parseInt(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Privilege Level</label>
            <select
              value={form.privilege_level}
              onChange={(e) => update('privilege_level', parseInt(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
            >
              <option value={1}>Normal (1)</option>
              <option value={2}>Elevated (2)</option>
              <option value={3}>Admin (3)</option>
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Hour of Day: {form.hour}:00</label>
            <input
              type="range" min="0" max="23" value={form.hour}
              onChange={(e) => update('hour', parseInt(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
          </div>

          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox" checked={form.is_weekend}
              onChange={(e) => update('is_weekend', e.target.checked)}
              className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-indigo-500 focus:ring-indigo-500"
            />
            Weekend
          </label>
        </div>

        {/* Right column */}
        <div className="glass-card space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Location & Network</h3>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Location</label>
            <select
              value={form.location}
              onChange={(e) => update('location', e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
            >
              {LOCATIONS.map(loc => <option key={loc} value={loc}>{loc}</option>)}
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-2 block">IP Type</label>
            <div className="flex gap-4">
              {['internal', 'external'].map(type => (
                <label key={type} className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                  <input
                    type="radio" name="ip_type" value={type}
                    checked={form.ip_type === type}
                    onChange={(e) => update('ip_type', e.target.value)}
                    className="text-indigo-500 focus:ring-indigo-500 bg-slate-800 border-slate-600"
                  />
                  {type === 'internal' ? 'Internal (192.168.x.x)' : 'External'}
                </label>
              ))}
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox" checked={form.sensitive_data}
              onChange={(e) => update('sensitive_data', e.target.checked)}
              className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-indigo-500 focus:ring-indigo-500"
            />
            Accessing Sensitive Data
          </label>

          <div className="pt-4 border-t border-slate-700/50">
            <label className="text-sm text-slate-400 mb-1 block">Voting Strategy</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
            >
              <option value="weighted">Weighted Average (Recommended)</option>
              <option value="majority">Majority (Both Agree)</option>
              <option value="any">Any (Either Flags)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <Search className="w-5 h-5" />
        {loading ? 'Analyzing...' : 'Analyze Event'}
      </button>

      {/* Quick test scenarios */}
      <div>
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Quick Test Scenarios</h3>
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
          <button type="button" onClick={() => applyPreset('normal')}
            className="glass-card text-center py-3 hover:border-emerald-500/40 transition-all cursor-pointer group">
            <Shield className="w-5 h-5 mx-auto mb-1 text-emerald-400 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-semibold text-slate-300">Normal</span>
          </button>
          <button type="button" onClick={() => applyPreset('credential')}
            className="glass-card text-center py-3 hover:border-yellow-500/40 transition-all cursor-pointer group">
            <Zap className="w-5 h-5 mx-auto mb-1 text-yellow-400 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-semibold text-slate-300">Brute Force</span>
          </button>
          <button type="button" onClick={() => applyPreset('exfiltration')}
            className="glass-card text-center py-3 hover:border-red-500/40 transition-all cursor-pointer group">
            <FileWarning className="w-5 h-5 mx-auto mb-1 text-red-400 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-semibold text-slate-300">Exfiltration</span>
          </button>
          <button type="button" onClick={() => applyPreset('impossible_travel')}
            className="glass-card text-center py-3 hover:border-orange-500/40 transition-all cursor-pointer group">
            <Globe className="w-5 h-5 mx-auto mb-1 text-orange-400 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-semibold text-slate-300">Impossible Travel</span>
          </button>
          <button type="button" onClick={() => applyPreset('insider_threat')}
            className="glass-card text-center py-3 hover:border-purple-500/40 transition-all cursor-pointer group">
            <UserMinus className="w-5 h-5 mx-auto mb-1 text-purple-400 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-semibold text-slate-300">Insider Threat</span>
          </button>
          <button type="button" onClick={() => applyPreset('weekend_access')}
            className="glass-card text-center py-3 hover:border-blue-500/40 transition-all cursor-pointer group">
            <Calendar className="w-5 h-5 mx-auto mb-1 text-blue-400 group-hover:scale-110 transition-transform" />
            <span className="text-xs font-semibold text-slate-300">Weekend Access</span>
          </button>
        </div>
      </div>
    </form>
  );
}
