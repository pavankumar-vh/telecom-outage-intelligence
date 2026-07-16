import React, { useState, useMemo } from 'react';
import { ChevronDown, AlertTriangle, Search, ArrowUp, ArrowDown, Download } from 'react-icons/fa';
import { EmptyIncidents } from './EmptyStates';
import { TableRowSkeleton } from './LoadingStates';

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
 * Sort Header Component
 */
const SortHeader = ({ label, sortKey, currentSort, onSort }) => {
  const isActive = currentSort.key === sortKey;
  
  return (
    <button
      onClick={() => onSort(sortKey)}
      className="flex items-center gap-2 hover:text-gray-200 transition text-gray-300 font-semibold"
    >
      {label}
      {isActive && (
        currentSort.direction === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
      )}
    </button>
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
          <ChevronDown
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
            <AlertTriangle size={16} className="text-red-400 inline" title="Anomalies detected" />
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
                    <span>Severity (40%)</span>
                    <span className="text-gray-200">{(incident.severity_score?.contribution || 0).toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Complaints (35%)</span>
                    <span className="text-gray-200">{(incident.complaint_score?.contribution || 0).toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Usage Impact (25%)</span>
                    <span className="text-gray-200">{(incident.usage_score?.contribution || 0).toFixed(1)}</span>
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
 * Enhanced Incident Table with Search, Sort, and Pagination
 */
export const IncidentTable = ({ 
  incidents = [], 
  anomalies = {}, 
  isLoading = false, 
  onIncidentClick,
  searchQuery = '',
  onSearchChange = () => {},
}) => {
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: 'overall_score', direction: 'desc' });
  const itemsPerPage = 10;

  const toggleRow = (outageId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(outageId)) {
      newExpanded.delete(outageId);
    } else {
      newExpanded.add(outageId);
    }
    setExpandedRows(newExpanded);
  };

  // Map anomalies by outage_id
  const anomaliesByOutage = {};
  if (anomalies.incidents) {
    anomalies.incidents.forEach(inc => {
      anomaliesByOutage[inc.outage_id] = inc.anomaly_flags || [];
    });
  }

  // Search filtering
  const filteredIncidents = useMemo(() => {
    let result = incidents.filter(incident => {
      const query = searchQuery.toLowerCase();
      return (
        incident.outage_id.toLowerCase().includes(query) ||
        incident.region.toLowerCase().includes(query) ||
        incident.component.toLowerCase().includes(query) ||
        incident.severity.toLowerCase().includes(query)
      );
    });
    return result;
  }, [incidents, searchQuery]);

  // Sorting
  const sortedIncidents = useMemo(() => {
    let sorted = [...filteredIncidents];
    sorted.sort((a, b) => {
      const key = sortConfig.key;
      let aVal = a[key];
      let bVal = b[key];

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [filteredIncidents, sortConfig]);

  // Pagination
  const paginatedIncidents = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedIncidents.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedIncidents, currentPage]);

  const totalPages = Math.ceil(sortedIncidents.length / itemsPerPage);

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc',
    }));
    setCurrentPage(1);
  };

  const handleExportCSV = () => {
    const headers = ['Incident ID', 'Region', 'Severity', 'Impact Score', 'Duration (min)', 'Complaints', 'Affected Customers', 'Component'];
    const rows = sortedIncidents.map(inc => [
      inc.outage_id,
      inc.region,
      inc.severity,
      inc.overall_score.toFixed(1),
      inc.duration_minutes,
      inc.complaint_count,
      inc.affected_customers,
      inc.component,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `incidents-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (isLoading) {
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
            {[...Array(5)].map((_, i) => (
              <TableRowSkeleton key={i} />
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (!incidents || incidents.length === 0) {
    return <EmptyIncidents />;
  }

  return (
    <div>
      {/* Search and Export Bar */}
      <div className="flex flex-col md:flex-row gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 text-gray-500" size={18} />
          <input
            type="text"
            placeholder="Search incidents..."
            value={searchQuery}
            onChange={(e) => {
              onSearchChange(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-gray-800 border border-gray-700 rounded px-10 py-2 text-gray-200 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <button
          onClick={handleExportCSV}
          disabled={sortedIncidents.length === 0}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 px-4 py-2 rounded transition-colors font-semibold"
        >
          <Download size={16} /> Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-gray-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800 border-b border-gray-700">
            <tr>
              <th className="px-4 py-3 text-left"></th>
              <th className="px-4 py-3 text-left">
                <SortHeader label="Incident ID" sortKey="outage_id" currentSort={sortConfig} onSort={handleSort} />
              </th>
              <th className="px-4 py-3 text-left">
                <SortHeader label="Region" sortKey="region" currentSort={sortConfig} onSort={handleSort} />
              </th>
              <th className="px-4 py-3 text-left">
                <SortHeader label="Severity" sortKey="severity" currentSort={sortConfig} onSort={handleSort} />
              </th>
              <th className="px-4 py-3 text-left">
                <SortHeader label="Impact Score" sortKey="overall_score" currentSort={sortConfig} onSort={handleSort} />
              </th>
              <th className="px-4 py-3 text-left">
                <SortHeader label="Duration" sortKey="duration_minutes" currentSort={sortConfig} onSort={handleSort} />
              </th>
              <th className="px-4 py-3 text-left">
                <SortHeader label="Complaints" sortKey="complaint_count" currentSort={sortConfig} onSort={handleSort} />
              </th>
              <th className="px-4 py-3 text-center font-semibold text-gray-300">Flags</th>
            </tr>
          </thead>
          <tbody>
            {paginatedIncidents.length > 0 ? (
              paginatedIncidents.map((incident) => (
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
              ))
            ) : (
              <tr>
                <td colSpan="8" className="px-4 py-12 text-center text-gray-400">
                  No incidents match your search
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 px-2">
          <div className="text-sm text-gray-400">
            Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, sortedIncidents.length)} of {sortedIncidents.length} incidents
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="bg-gray-800 hover:bg-gray-700 disabled:opacity-50 px-3 py-2 rounded text-sm font-semibold transition"
            >
              Previous
            </button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = i + 1;
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3 py-2 rounded text-sm font-semibold transition ${
                      currentPage === pageNum
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
              {totalPages > 5 && <span className="text-gray-400">...</span>}
            </div>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="bg-gray-800 hover:bg-gray-700 disabled:opacity-50 px-3 py-2 rounded text-sm font-semibold transition"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
