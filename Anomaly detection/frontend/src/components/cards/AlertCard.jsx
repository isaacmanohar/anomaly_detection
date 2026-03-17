import { useState } from 'react';
import { ChevronDown, ChevronUp, MapPin, Globe, User, Building2 } from 'lucide-react';

const severityStyles = {
  CRITICAL: 'border-l-4 border-l-red-500 bg-gradient-to-r from-red-500/10 to-red-900/5',
  HIGH: 'border-l-4 border-l-orange-500 bg-gradient-to-r from-orange-500/10 to-orange-900/5',
  MEDIUM: 'border-l-4 border-l-yellow-500 bg-gradient-to-r from-yellow-500/10 to-yellow-900/5',
  LOW: 'border-l-4 border-l-green-500 bg-gradient-to-r from-green-500/10 to-green-900/5',
};

const severityBadge = {
  CRITICAL: 'bg-red-500/20 text-red-300 border border-red-500/30',
  HIGH: 'bg-orange-500/20 text-orange-300 border border-orange-500/30',
  MEDIUM: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30',
  LOW: 'bg-green-500/20 text-green-300 border border-green-500/30',
};

export default function AlertCard({ alert, index }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`rounded-xl p-4 mb-3 ${severityStyles[alert.severity]} border border-slate-700/50 animate-fade-in-up cursor-pointer transition-all hover:border-slate-600/50`}
      style={{ animationDelay: `${index * 50}ms` }}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          <span className={`text-xs font-semibold px-2 py-1 rounded-md ${severityBadge[alert.severity]}`}>
            {alert.severity}
          </span>
          <span className="text-white font-medium">{alert.user_name}</span>
          <span className="text-slate-400">-</span>
          <span className="text-slate-300">{alert.anomaly_type}</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-400">Risk: <span className="text-white font-semibold">{alert.risk_score}</span></span>
          {expanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>
      </div>

      {expanded && (
        <div className="mt-4 pt-4 border-t border-slate-700/50 grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <User className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-slate-400">User:</span>
              <span className="text-slate-200">{alert.user_name}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Building2 className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-slate-400">Department:</span>
              <span className="text-slate-200">{alert.department}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-slate-400">Timestamp:</span>
              <span className="text-slate-200">{alert.timestamp}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-slate-400">Location:</span>
              <span className="text-slate-200">{alert.location}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <Globe className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-slate-400">Source IP:</span>
              <span className="text-slate-200">{alert.source_ip}</span>
            </div>
            <div className="text-sm">
              <span className="text-slate-400">Resources:</span>
              <span className="text-slate-200 ml-2">{alert.resources_accessed}</span>
            </div>
            <div className="text-sm">
              <span className="text-slate-400">Download:</span>
              <span className="text-slate-200 ml-2">{alert.download_mb} MB</span>
            </div>
            <div className="text-sm">
              <span className="text-slate-400">Failed Attempts:</span>
              <span className="text-slate-200 ml-2">{alert.failed_attempts}</span>
            </div>
          </div>
          <div className="col-span-2 mt-2">
            <div className="text-sm mb-2">
              <span className="text-slate-400">Model Predictions:</span>
              <span className="text-slate-200 ml-2">IF: {alert.if_prediction}, AE: {alert.ae_prediction}</span>
            </div>
            <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-3 text-sm text-indigo-200">
              <span className="font-medium">Recommended Action: </span>{alert.recommended_action}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
