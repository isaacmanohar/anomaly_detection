import { useState, useEffect } from 'react';
import { fetchAlerts } from '@/api/client';
import Header from '@/components/layout/Header';
import MetricCard from '@/components/cards/MetricCard';
import AlertCard from '@/components/cards/AlertCard';
import { AlertTriangle, ShieldAlert, AlertCircle, CheckCircle } from 'lucide-react';

const SEVERITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

export default function Alerts() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState(['CRITICAL', 'HIGH']);
  const [attackFilter, setAttackFilter] = useState([]);
  const [deptFilter, setDeptFilter] = useState([]);
  const [availableFilters, setAvailableFilters] = useState({ attack_types: [], departments: [] });

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const result = await fetchAlerts({
        severity: severityFilter.length > 0 ? severityFilter : undefined,
        attackType: attackFilter.length > 0 ? attackFilter : undefined,
        department: deptFilter.length > 0 ? deptFilter : undefined,
      });
      setData(result);
      if (result.available_filters) {
        setAvailableFilters(result.available_filters);
      }
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAlerts(); }, [severityFilter, attackFilter, deptFilter]);

  const toggleSeverity = (sev) => {
    setSeverityFilter(prev =>
      prev.includes(sev) ? prev.filter(s => s !== sev) : [...prev, sev]
    );
  };

  const toggleAttack = (type) => {
    setAttackFilter(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const toggleDept = (dept) => {
    setDeptFilter(prev =>
      prev.includes(dept) ? prev.filter(d => d !== dept) : [...prev, dept]
    );
  };

  const severityIcons = {
    CRITICAL: AlertTriangle,
    HIGH: ShieldAlert,
    MEDIUM: AlertCircle,
    LOW: CheckCircle,
  };

  return (
    <div>
      <Header title="Security Alerts" subtitle="Monitor and filter detected security threats" />

      {/* Filters */}
      <div className="glass-card mb-6 animate-fade-in-up">
        <div className="grid grid-cols-3 gap-6">
          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-2 block">Severity</label>
            <div className="flex flex-wrap gap-2">
              {SEVERITIES.map(sev => (
                <button
                  key={sev}
                  onClick={() => toggleSeverity(sev)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    severityFilter.includes(sev)
                      ? sev === 'CRITICAL' ? 'bg-red-500/20 border-red-500/40 text-red-300'
                        : sev === 'HIGH' ? 'bg-orange-500/20 border-orange-500/40 text-orange-300'
                        : sev === 'MEDIUM' ? 'bg-yellow-500/20 border-yellow-500/40 text-yellow-300'
                        : 'bg-green-500/20 border-green-500/40 text-green-300'
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-2 block">Attack Type</label>
            <div className="flex flex-wrap gap-2">
              {availableFilters.attack_types.map(type => (
                <button
                  key={type}
                  onClick={() => toggleAttack(type)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    attackFilter.includes(type)
                      ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-2 block">Department</label>
            <div className="flex flex-wrap gap-2">
              {availableFilters.departments.map(dept => (
                <button
                  key={dept}
                  onClick={() => toggleDept(dept)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    deptFilter.includes(dept)
                      ? 'bg-purple-500/20 border-purple-500/40 text-purple-300'
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {dept}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Severity Counts */}
      {data && (
        <>
          <div className="grid grid-cols-4 gap-4 mb-6">
            <MetricCard title="Critical" value={data.severity_counts.CRITICAL} icon={AlertTriangle} delay={0} />
            <MetricCard title="High" value={data.severity_counts.HIGH} icon={ShieldAlert} delay={100} />
            <MetricCard title="Medium" value={data.severity_counts.MEDIUM} icon={AlertCircle} delay={200} />
            <MetricCard title="Low" value={data.severity_counts.LOW} icon={CheckCircle} delay={300} />
          </div>

          {/* Alerts List */}
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
              Alerts ({data.total} total)
            </h3>
          </div>

          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-slate-800/50 rounded-xl" />)}
            </div>
          ) : (
            <div>
              {data.alerts.map((alert, i) => (
                <AlertCard key={i} alert={alert} index={i} />
              ))}
              {data.alerts.length === 0 && (
                <div className="glass-card text-center py-12">
                  <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                  <p className="text-slate-300">No alerts matching the current filters</p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
