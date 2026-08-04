import React from 'react';
import { FaFilter, FaTimes } from 'react-icons/fa';

/**
 * Filter Component
 * 
 * Provides filtering options for incidents
 */
export const FilterBar = ({
  regions = [],
  selectedRegion = null,
  onRegionChange,
  severityFilter = null,
  onSeverityChange,
  scoreRange = [0, 100],
  onScoreRangeChange,
}) => {
  const severityOptions = ['Critical', 'Major', 'Warning', 'Minor'];

  const handleClearFilters = () => {
    onRegionChange(null);
    onSeverityChange(null);
    onScoreRangeChange([0, 100]);
  };

  const hasActiveFilters = selectedRegion || severityFilter || scoreRange[0] > 0 || scoreRange[1] < 100;

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 mb-6 backdrop-blur-sm">
      <div className="flex items-center gap-3 mb-4">
        <FaFilter size={18} className="text-gray-400" />
        <h3 className="text-sm font-semibold text-gray-300">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="ml-auto text-xs text-gray-400 hover:text-gray-200 flex items-center gap-1"
          >
            <FaTimes size={14} /> Clear all
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Region Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-2">Region</label>
          <select
            value={selectedRegion || ''}
            onChange={(e) => onRegionChange(e.target.value || null)}
            className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-sm text-gray-200 hover:border-gray-500 focus:border-blue-500 focus:outline-none transition-colors"
          >
            <option value="">All Regions</option>
            {regions.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </div>

        {/* Severity Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-2">Severity</label>
          <select
            value={severityFilter || ''}
            onChange={(e) => onSeverityChange(e.target.value || null)}
            className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-sm text-gray-200 hover:border-gray-500 focus:border-blue-500 focus:outline-none transition-colors"
          >
            <option value="">All Severities</option>
            {severityOptions.map((severity) => (
              <option key={severity} value={severity}>
                {severity}
              </option>
            ))}
          </select>
        </div>

        {/* Impact Score Range */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-2">
            Impact Score: {scoreRange[0]} - {scoreRange[1]}
          </label>
          <div className="flex items-center gap-2">
            <input
              type="range"
              min="0"
              max="100"
              value={scoreRange[0]}
              onChange={(e) => {
                const newMin = Math.min(parseInt(e.target.value), scoreRange[1]);
                onScoreRangeChange([newMin, scoreRange[1]]);
              }}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <input
              type="range"
              min="0"
              max="100"
              value={scoreRange[1]}
              onChange={(e) => {
                const newMax = Math.max(parseInt(e.target.value), scoreRange[0]);
                onScoreRangeChange([scoreRange[0], newMax]);
              }}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
