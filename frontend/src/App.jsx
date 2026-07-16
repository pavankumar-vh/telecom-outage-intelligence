import { useState, useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'react-icons/fa';
import './App.css';
import { KPIContainer } from './components/KPICards';
import { IncidentTable } from './components/IncidentTable';
import { FilterBar } from './components/FilterBar';
import {
  SeverityChart,
  RegionalImpactChart,
  ScoreDistributionChart,
  ComplaintImpactChart,
} from './components/Charts';
import { apiService } from './services/apiService';

function App() {
  // State management
  const [incidents, setIncidents] = useState([]);
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Filter state
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [selectedSeverity, setSelectedSeverity] = useState(null);
  const [scoreRange, setScoreRange] = useState([0, 100]);

  // Calculate metrics from incidents
  const calculateMetrics = (incidents) => {
    if (!incidents || incidents.length === 0) {
      return {
        activeOutages: 0,
        avgScore: 0,
        affectedCustomers: 0,
        regions: 0,
      };
    }

    const avgScore = incidents.reduce((sum, inc) => sum + inc.overall_score, 0) / incidents.length;
    const affectedCustomers = incidents.reduce((sum, inc) => sum + (inc.affected_customers || 0), 0);
    const regions = new Set(incidents.map((inc) => inc.region)).size;

    return {
      activeOutages: incidents.length,
      avgScore,
      affectedCustomers,
      regions,
    };
  };

  // Get unique regions from incidents
  const getAvailableRegions = (incidents) => {
    return [...new Set(incidents.map((inc) => inc.region))].sort();
  };

  // Filter incidents based on current filters
  const getFilteredIncidents = () => {
    return incidents.filter((incident) => {
      // Region filter
      if (selectedRegion && incident.region !== selectedRegion) {
        return false;
      }

      // Severity filter
      if (selectedSeverity && incident.severity !== selectedSeverity) {
        return false;
      }

      // Score range filter
      if (
        incident.overall_score < scoreRange[0] ||
        incident.overall_score > scoreRange[1]
      ) {
        return false;
      }

      return true;
    });
  };

  // Fetch data from backend
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch ranked incidents
      const incidentsResponse = await apiService.getRankedIncidents();
      if (incidentsResponse.status === 'success' && incidentsResponse.incidents) {
        setIncidents(incidentsResponse.incidents);
      } else {
        setError('Failed to fetch incidents');
      }

      // Fetch anomalies
      const anomaliesResponse = await apiService.getAnomalies();
      if (anomaliesResponse.status === 'success') {
        setAnomalies(anomaliesResponse);
      }

      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(`Error fetching data: ${err.message}`);
      console.error('Data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load and auto-refresh
  useEffect(() => {
    fetchData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredIncidents = getFilteredIncidents();
  const metrics = calculateMetrics(filteredIncidents);
  const availableRegions = getAvailableRegions(incidents);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Header */}
      <div className="border-b border-gray-700 sticky top-0 z-50 backdrop-blur-md bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">NOC Outage Impact Dashboard</h1>
              <p className="text-gray-400 text-sm mt-1">
                Telecom Outage Impact Prioritization System
              </p>
            </div>
            <div className="text-right">
              <button
                onClick={fetchData}
                disabled={loading}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded transition-colors"
              >
                <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                Refresh
              </button>
              {lastUpdated && (
                <p className="text-gray-400 text-xs mt-2">Last updated: {lastUpdated}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 flex items-start gap-4 bg-red-900/20 border border-red-500/30 rounded-lg p-4">
            <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <h3 className="text-red-300 font-semibold">Error</h3>
              <p className="text-red-200/70 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* KPI Cards */}
        {!loading && <KPIContainer metrics={metrics} />}

        {/* Filters */}
        <FilterBar
          regions={availableRegions}
          selectedRegion={selectedRegion}
          onRegionChange={setSelectedRegion}
          severityFilter={selectedSeverity}
          onSeverityChange={setSelectedSeverity}
          scoreRange={scoreRange}
          onScoreRangeChange={setScoreRange}
        />

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <SeverityChart incidents={filteredIncidents} />
          <RegionalImpactChart incidents={filteredIncidents} />
          <ScoreDistributionChart incidents={filteredIncidents} />
          <ComplaintImpactChart incidents={filteredIncidents} />
        </div>

        {/* Incident Table */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">
            Ranked Incidents ({filteredIncidents.length})
          </h2>
          <IncidentTable
            incidents={filteredIncidents}
            anomalies={anomalies}
            isLoading={loading}
          />
        </div>

        {/* Data Quality Info */}
        {filteredIncidents.length > 0 && (
          <div className="bg-gray-800/30 border border-gray-700 rounded-lg p-4 text-sm text-gray-400">
            <p>
              Showing {filteredIncidents.length} of {incidents.length} incidents
              {anomalies?.total_anomalies > 0 && ` • ${anomalies.total_anomalies} anomalies detected`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
