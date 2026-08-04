import React from 'react';
import { FaBoxOpen, FaExclamationTriangle, FaSearch } from 'react-icons/fa';

/**
 * Empty State - No Incidents
 */
export const EmptyIncidents = ({ onRefresh }) => (
  <div className="rounded-lg border border-gray-700 p-12 text-center bg-gray-900/30">
    <FaBoxOpen className="text-gray-500 mx-auto mb-4" size={48} />
    <h3 className="text-lg font-semibold text-gray-300 mb-2">No Incidents Found</h3>
    <p className="text-gray-400 mb-6">
      There are currently no incidents matching your filters. Try adjusting your search criteria.
    </p>
    {onRefresh && (
      <button
        onClick={onRefresh}
        className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-semibold transition"
      >
        Refresh Data
      </button>
    )}
  </div>
);

/**
 * Empty State - No Search Results
 */
export const EmptySearchResults = ({ query, onClear }) => (
  <div className="rounded-lg border border-gray-700 p-12 text-center bg-gray-900/30">
    <FaSearch className="text-gray-500 mx-auto mb-4" size={48} />
    <h3 className="text-lg font-semibold text-gray-300 mb-2">No Results for "{query}"</h3>
    <p className="text-gray-400 mb-6">
      No incidents match your search. Try a different search term or clear filters.
    </p>
    <button
      onClick={onClear}
      className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-semibold transition"
    >
      Clear Search
    </button>
  </div>
);

/**
 * Empty State - No Data Available
 */
export const EmptyState = ({ title, description, icon: Icon = BoxOpen, action, actionLabel }) => (
  <div className="rounded-lg border border-gray-700 p-12 text-center bg-gray-900/30">
    <Icon className="text-gray-500 mx-auto mb-4" size={48} />
    <h3 className="text-lg font-semibold text-gray-300 mb-2">{title}</h3>
    <p className="text-gray-400 mb-6">{description}</p>
    {action && actionLabel && (
      <button
        onClick={action}
        className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-semibold transition"
      >
        {actionLabel}
      </button>
    )}
  </div>
);

/**
 * Inline Empty State for Sections
 */
export const InlineEmptyState = ({ message }) => (
  <div className="text-center py-8 text-gray-400">
    <FaExclamationTriangle className="mx-auto mb-2" size={24} />
    <p className="text-sm">{message}</p>
  </div>
);
