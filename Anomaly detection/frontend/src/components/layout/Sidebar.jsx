import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Search, GitCompare, BarChart3, AlertTriangle, Info, Shield
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/detection', icon: Search, label: 'Real-Time Detection' },
  { to: '/models', icon: GitCompare, label: 'Model Comparison' },
  { to: '/performance', icon: BarChart3, label: 'Performance' },
  { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
  { to: '/about', icon: Info, label: 'About' },
];

export default function Sidebar({ systemInfo }) {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-gradient-to-b from-[#1a1a2e]/90 to-[#0f0f23]/90 backdrop-blur-xl border-r border-indigo-500/20 flex flex-col z-50">
      {/* Logo */}
      <div className="p-6 border-b border-indigo-500/20">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-indigo-400" />
          <div>
            <h1 className="text-lg font-bold text-white">Anomaly Detection</h1>
            <p className="text-xs text-slate-400">Identity Security</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 px-3">Navigation</p>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 shadow-lg shadow-indigo-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`
            }
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* System Overview */}
      {systemInfo && (
        <div className="p-4 border-t border-indigo-500/20 space-y-3">
          <p className="text-xs text-slate-500 uppercase tracking-wider px-1">System Overview</p>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Total Events</span>
              <span className="text-white font-semibold">{systemInfo.total_events?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Anomaly Rate</span>
              <span className="text-white font-semibold">{systemInfo.anomaly_rate}%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">F1-Score (CV)</span>
              <span className="text-white font-semibold">{(systemInfo.cv_metrics?.f1 * 100).toFixed(1)}%</span>
            </div>
          </div>

          {systemInfo.model_weights && (
            <div className="space-y-2 mt-3">
              <p className="text-xs text-slate-500 uppercase tracking-wider px-1">Model Weights</p>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Isolation Forest</span>
                  <span className="text-indigo-300">{(systemInfo.model_weights.isolation_forest * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-1.5">
                  <div
                    className="bg-indigo-500 h-1.5 rounded-full transition-all"
                    style={{ width: `${systemInfo.model_weights.isolation_forest * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Autoencoder</span>
                  <span className="text-purple-300">{(systemInfo.model_weights.autoencoder * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-1.5">
                  <div
                    className="bg-purple-500 h-1.5 rounded-full transition-all"
                    style={{ width: `${systemInfo.model_weights.autoencoder * 100}%` }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
