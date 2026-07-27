import React, { useState } from 'react';
import { FaChevronDown, FaExclamationTriangle, FaCheckCircle, FaClock } from 'react-icons/fa';

/**
 * Severity Badge Component
 */
export const SeverityBadge = ({ severity }) => {
  const severityColors = {
    Critical: 'bg-red-900/30 text-red-300 border border-red-500/30',
    Major: 'bg-orange-900/30 text-orange-300 border border-orange-500/30',
    Warning: 'bg-yellow-900/30 text-yellow-300 border border-yellow-500/30',
    Minor: 'bg-green-900/30 text-green-300 border border-green-500/30',
  };

  return (
    <span className={`${severityColors[severity] || 'bg-gray-900/30 text-gray-300'} px-3 py-1 rounded text-xs font-semibold`}>
      {severity}
    </span>
  );
};

/**
 * Score Bar Component
 */
export const ScoreBar = ({ score }) => {
  let color = 'bg-green-500';
  if (score >= 80) color = 'bg-red-500';
  else if (score >= 60) color = 'bg-orange-500';
  else if (score >= 40) color = 'bg-yellow-500';

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-700 rounded-full h-2 overflow-hidden">
        <div className={`${color} h-full transition-all`} style={{ width: `${score}%` }}></div>
      </div>
      <span className="text-sm font-semibold text-gray-200 min-w-[40px] text-right">{score.toFixed(1)}</span>
    </div>
  );
};

/**
 * Incident Row Component (Expandable)
 */
export const IncidentRow = ({ incident, isExpanded, onToggle, onIncidentClick }) => {
  const durationHours = (incident.duration_minutes / 60).toFixed(1);
  const hasAnomalies = incident.anomalies && incident.anomalies.length > 0;

  return (
    <>
      <tr
        className="border-b border-gray-700 hover:bg-gray-900/50 cursor-pointer transition-colors"
        onClick={onToggle}
      >
        <td className="px-4 py-3">
          <FaChevronDown
            className={`inline transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            size={16}
          />
        </td>
        <td className="px-4 py-3 font-mono text-sm text-gray-300">{incident.outage_id}</td>
        <td className="px-4 py-3 text-sm text-gray-300">{incident.region}</td>
        <td className="px-4 py-3">
          <SeverityBadge severity={incident.severity} />
        </td>
        <td className="px-4 py-3">
          <ScoreBar score={incident.overall_score} />
        </td>
        <td className="px-4 py-3 text-sm text-gray-400">{durationHours}h</td>
        <td className="px-4 py-3 text-sm text-gray-400">{incident.complaint_count}</td>
        <td className="px-4 py-3 text-center">
          {hasAnomalies && (
            <FaExclamationTriangle size={16} className="text-red-400 inline" title="Anomalies detected" />
          )}
        </td>
      </tr>

      {isExpanded && (
        <tr className="bg-gray-900/30 border-b border-gray-700">
          <td colSpan="8" className="px-4 py-4">
            <div className="grid grid-cols-2 gap-6">
              {/* Scoring Breakdown */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-3">Impact Score Breakdown</h4>
                <div className="space-y-2 text-xs text-gray-400">
                  <div className="flex justify-between">
                    <span>Severity ({incident.severity_score?.weight * 100 || 0}%)</span>
                    <span className="text-gray-200">{incident.severity_score?.contribution?.toFixed(1) || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Complaints ({incident.complaint_score?.weight * 100 || 0}%)</span>
                    <span className="text-gray-200">{incident.complaint_score?.contribution?.toFixed(1) || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Usage Impact ({incident.usage_score?.weight * 100 || 0}%)</span>
                    <span className="text-gray-200">{incident.usage_score?.contribution?.toFixed(1) || 0}</span>
                  </div>
                </div>
              </div>

              {/* Metrics */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-3">Incident Metrics</h4>
                <div className="space-y-2 text-xs text-gray-400">
                  <div className="flex justify-between">
                    <span>Affected Customers</span>
                    <span className="text-gray-200">{incident.affected_customers?.toLocaleString() || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Peak Traffic</span>
                    <span className="text-gray-200">{incident.avg_traffic_gbps?.toFixed(1) || '—'} Gbps</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Active Users</span>
                    <span className="text-gray-200">{incident.peak_active_users?.toLocaleString() || '—'}</span>
                  </div>
                </div>
              </div>

              {/* Explanation */}
              {incident.explanation && (
                <div className="col-span-2">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Score Explanation</h4>
                  <p className="text-xs text-gray-400 italic">{incident.explanation}</p>
                </div>
              )}

              {/* Anomalies */}
              {hasAnomalies && (
                <div className="col-span-2">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">
                    <AlertTriangle size={14} className="inline mr-2 text-red-400" />
                    Detected Anomalies
                  </h4>
                  <ul className="space-y-1 text-xs text-gray-400">
                    {incident.anomalies.map((anomaly, idx) => (
                      <li key={idx} className="ml-6">
                        <span className={`font-semibold ${
                          anomaly.severity === 'high' ? 'text-red-400' :
                          anomaly.severity === 'medium' ? 'text-yellow-400' :
                          'text-blue-400'
                        }`}>
                          [{anomaly.severity.toUpperCase()}]
                        </span>
                        {' '}{anomaly.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Button */}
              {onIncidentClick && (
                <div className="col-span-2 flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onIncidentClick(incident.outage_id);
                    }}
                    className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-semibold transition"
                  >
                    View Full Details
                  </button>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

/**
 * Incident Table Component
 */
export const IncidentTable = ({ incidents = [], anomalies = {}, isLoading = false, onIncidentClick }) => {
  const [expandedRows, setExpandedRows] = useState(new Set());

  const toggleRow = (outageId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(outageId)) {
      newExpanded.delete(outageId);
    } else {
      newExpanded.add(outageId);
    }
    setExpandedRows(newExpanded);
  };

  // Map anomalies by outage_id for quick lookup
  const anomaliesByOutage = {};
  if (anomalies?.incidents) {
    anomalies.incidents.forEach(inc => {
      anomaliesByOutage[inc.outage_id] = inc.anomaly_flags || [];
    });
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border border-gray-700 p-8 text-center">
        <p className="text-gray-400">Loading incidents...</p>
      </div>
    );
  }

  if (!incidents || incidents.length === 0) {
    return (
      <div className="rounded-lg border border-gray-700 p-8 text-center">
        <p className="text-gray-400">No incidents to display</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-700 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-800 border-b border-gray-700">
          <tr>
            <th className="px-4 py-3 text-left"></th>
            <th className="px-4 py-3 text-left font-semibold text-gray-300">Incident ID</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-300">Region</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-300">Severity</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-300">Impact Score</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-300">Duration</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-300">Complaints</th>
            <th className="px-4 py-3 text-center font-semibold text-gray-300">Flags</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map((incident) => (
            <IncidentRow
              key={incident.outage_id}
              incident={{
                ...incident,
                anomalies: anomaliesByOutage[incident.outage_id] || [],
              }}
              isExpanded={expandedRows.has(incident.outage_id)}
              onToggle={() => toggleRow(incident.outage_id)}
              onIncidentClick={onIncidentClick}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};
