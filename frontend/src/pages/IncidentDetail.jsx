import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FaArrowLeft, FaExclamationCircle, FaCheckCircle, FaClock, FaUsers, FaChartLine } from 'react-icons/fa';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiService } from '../services/apiService';

const IncidentDetail = () => {
  const { incidentId } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [relatedIncidents, setRelatedIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const incidentsResponse = await apiService.getRankedIncidents();
        if (incidentsResponse.status === 'success' && incidentsResponse.incidents) {
          const allIncidents = incidentsResponse.incidents;
          const found = allIncidents.find((inc) => inc.outage_id === incidentId);

          if (found) {
            setIncident(found);
            setRelatedIncidents(
              allIncidents.filter((inc) => inc.region === found.region && inc.outage_id !== incidentId)
            );
          }
        }
      } catch (err) {
        console.error('Error fetching incident data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [incidentId]);

  const getSeverityColor = (severity) => {
    const colors = {
      Critical: 'bg-red-900 text-red-100 border-red-700',
      Major: 'bg-orange-900 text-orange-100 border-orange-700',
      Warning: 'bg-yellow-900 text-yellow-100 border-yellow-700',
      Minor: 'bg-green-900 text-green-100 border-green-700',
    };

    return colors[severity] || 'bg-gray-800 text-gray-200 border-gray-700';
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      Critical: <FaExclamationCircle className="text-red-400" />,
      Major: <FaExclamationCircle className="text-orange-400" />,
      Warning: <FaExclamationCircle className="text-yellow-400" />,
      Minor: <FaCheckCircle className="text-green-400" />,
    };

    return icons[severity] || <FaExclamationCircle />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6 flex items-center justify-center text-gray-400">
        Loading incident details...
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6 flex items-center justify-center text-gray-400">
        Incident not found
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6 text-gray-100">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 mb-8 text-blue-400 hover:text-blue-300 transition font-semibold"
      >
        <FaArrowLeft size={20} /> Back to Dashboard
      </button>

      <div className="space-y-6">
        <section className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
          <div className="flex items-start justify-between gap-6 flex-wrap">
            <div>
              <div className="flex items-center gap-3 mb-3 flex-wrap">
                {getSeverityIcon(incident.severity)}
                <h1 className="text-3xl font-bold">{incident.outage_id}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getSeverityColor(incident.severity)}`}>
                  {incident.severity}
                </span>
              </div>
              <p className="text-gray-400">
                {incident.component} • {new Date(incident.timestamp).toLocaleString()}
              </p>
            </div>

            <div className="text-right">
              <div className="text-4xl font-bold text-blue-400">{incident.overall_score?.toFixed(1) || 'N/A'}</div>
              <p className="text-gray-400">Impact Score</p>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Region</p>
            <p className="text-lg font-semibold">{incident.region}</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Duration</p>
            <p className="text-lg font-semibold">{incident.duration_minutes} min</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Status</p>
            <p className="text-lg font-semibold text-green-400">{incident.status}</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Component</p>
            <p className="text-lg font-semibold">{incident.component}</p>
          </div>
        </section>

        <section className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
          <h2 className="text-2xl font-bold mb-4">Impact Score Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800 rounded p-4 border border-gray-700">
              <p className="text-gray-300 font-semibold mb-2">Severity Score</p>
              <p className="text-red-400 font-bold">{(incident.severity_score || 0).toFixed(1)}</p>
              <p className="text-xs text-gray-400 mt-2">{incident.severity} severity incident</p>
            </div>
            <div className="bg-gray-800 rounded p-4 border border-gray-700">
              <p className="text-gray-300 font-semibold mb-2">Complaint Score</p>
              <p className="text-orange-400 font-bold">{(incident.complaint_score || 0).toFixed(1)}</p>
              <p className="text-xs text-gray-400 mt-2">{incident.complaint_count} complaints</p>
            </div>
            <div className="bg-gray-800 rounded p-4 border border-gray-700">
              <p className="text-gray-300 font-semibold mb-2">Usage Score</p>
              <p className="text-yellow-400 font-bold">{(incident.usage_score || 0).toFixed(1)}</p>
              <p className="text-xs text-gray-400 mt-2">{incident.avg_traffic_gbps} Gbps traffic</p>
            </div>
          </div>

          {incident.explanation && (
            <div className="mt-4 bg-blue-900 bg-opacity-20 border border-blue-700 rounded p-4">
              <p className="text-blue-300 text-sm">{incident.explanation}</p>
            </div>
          )}
        </section>

        <section className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
          <h2 className="text-2xl font-bold mb-4">Customer Impact Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800 rounded p-4 border border-gray-700 flex items-center gap-3">
              <FaUsers className="text-red-400" size={24} />
              <div>
                <p className="text-gray-400 text-sm">Affected Customers</p>
                <p className="text-2xl font-bold">{incident.affected_customers}</p>
              </div>
            </div>
            <div className="bg-gray-800 rounded p-4 border border-gray-700 flex items-center gap-3">
              <FaChartLine className="text-orange-400" size={24} />
              <div>
                <p className="text-gray-400 text-sm">Peak Traffic</p>
                <p className="text-2xl font-bold">{incident.avg_traffic_gbps} Gbps</p>
              </div>
            </div>
            <div className="bg-gray-800 rounded p-4 border border-gray-700 flex items-center gap-3">
              <FaClock className="text-yellow-400" size={24} />
              <div>
                <p className="text-gray-400 text-sm">Total Duration</p>
                <p className="text-2xl font-bold">{incident.duration_minutes} min</p>
              </div>
            </div>
          </div>
        </section>

        {relatedIncidents.length > 0 && (
          <section className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
            <h2 className="text-2xl font-bold mb-4">Other Incidents in {incident.region}</h2>
            <div className="space-y-3">
              {relatedIncidents.slice(0, 5).map((rel) => (
                <button
                  key={rel.outage_id}
                  onClick={() => navigate(`/incident/${rel.outage_id}`)}
                  className="w-full text-left bg-gray-800 hover:bg-gray-750 rounded p-4 border border-gray-700 hover:border-gray-600 transition"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{rel.outage_id}</p>
                      <p className="text-sm text-gray-400">
                        {rel.component} • Score: {rel.overall_score?.toFixed(1) || 'N/A'}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded text-sm font-semibold ${getSeverityColor(rel.severity)}`}>
                      {rel.severity}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default IncidentDetail;
