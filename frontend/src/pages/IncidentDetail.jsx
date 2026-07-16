import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertCircle, CheckCircle, Clock, Users, TrendingUp, MapPin } from 'react-icons/fa';
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
        // Fetch ranked incidents
        const incidentsResponse = await apiService.getRankedIncidents();
        if (incidentsResponse.status === 'success' && incidentsResponse.incidents) {
          const allIncidents = incidentsResponse.incidents;
          const found = allIncidents.find(inc => inc.outage_id === incidentId);
          if (found) {
            setIncident(found);
            // Find related incidents in same region
            const related = allIncidents.filter(
              inc => inc.region === found.region && inc.outage_id !== incidentId
            );
            setRelatedIncidents(related);
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
      Critical: <AlertCircle className="text-red-400" />,
      Major: <AlertCircle className="text-orange-400" />,
      Warning: <AlertCircle className="text-yellow-400" />,
      Minor: <CheckCircle className="text-green-400" />,
    };
    return icons[severity] || <AlertCircle />;
  };



  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6">
      {/* Header with back button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 mb-8 text-blue-400 hover:text-blue-300 transition font-semibold"
      >
        <ArrowLeft size={20} /> Back to Dashboard
      </button>

      {loading && (
        <div className="text-center text-gray-400 py-12">Loading incident details...</div>
      )}

      {!loading && !incident && (
        <div className="text-center text-gray-400 py-12">Incident not found</div>
      )}

      {!loading && incident && (
        <>
      <div className="mb-8 border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-3">
              {getSeverityIcon(incident.severity)}
              <h1 className="text-3xl font-bold text-gray-100">{incident.outage_id}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getSeverityColor(incident.severity)}`}>
                {incident.severity}
              </span>
            </div>
            <p className="text-gray-400">{incident.component} • {new Date(incident.timestamp).toLocaleString()}</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-blue-400">{incident.overall_score?.toFixed(1) || 'N/A'}</div>
            <p className="text-gray-400">Impact Score</p>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Region</p>
            <p className="text-lg font-semibold text-gray-100">{incident.region}</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Duration</p>
            <p className="text-lg font-semibold text-gray-100">{incident.duration_minutes} min</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Status</p>
            <p className="text-lg font-semibold text-green-400">{incident.status}</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Component</p>
            <p className="text-lg font-semibold text-gray-100">{incident.component}</p>
          </div>
        </div>
      </div>

      {/* Scoring Breakdown */}
      <div className="mb-8 border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
        <h2 className="text-2xl font-bold text-gray-100 mb-4">Impact Score Breakdown</h2>
        
        <div className="space-y-4">
          {/* Severity Score */}
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <div className="flex justify-between mb-2">
              <span className="text-gray-300 font-semibold">Severity Score (40%)</span>
              <span className="text-red-400 font-bold">{(incident.severity_score || 0).toFixed(1)}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-red-600 to-red-400 h-2 rounded-full"
                style={{ width: `${Math.min((incident.severity_score || 0) * 10, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-400 mt-2">{incident.severity} severity incident</p>
          </div>

          {/* Complaint Score */}
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <div className="flex justify-between mb-2">
              <span className="text-gray-300 font-semibold">Complaint Score (35%)</span>
              <span className="text-orange-400 font-bold">{(incident.complaint_score || 0).toFixed(1)}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-orange-600 to-orange-400 h-2 rounded-full"
                style={{ width: `${Math.min((incident.complaint_score || 0) * 10, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-400 mt-2">{incident.complaint_count} complaints, {incident.max_escalation} escalations</p>
          </div>

          {/* Usage Score */}
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <div className="flex justify-between mb-2">
              <span className="text-gray-300 font-semibold">Usage Score (25%)</span>
              <span className="text-yellow-400 font-bold">{(incident.usage_score || 0).toFixed(1)}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-yellow-600 to-yellow-400 h-2 rounded-full"
                style={{ width: `${Math.min((incident.usage_score || 0) * 10, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-400 mt-2">{incident.avg_traffic_gbps} Gbps traffic, {incident.peak_active_users} peak users</p>
          </div>
        </div>

        {/* Explanation */}
        {incident.explanation && (
          <div className="mt-4 bg-blue-900 bg-opacity-20 border border-blue-700 rounded p-4">
            <p className="text-blue-300 text-sm">{incident.explanation}</p>
          </div>
        )}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Complaint Progression */}
        <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
          <h3 className="text-xl font-bold text-gray-100 mb-4">Complaint Progression</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={[
              { time: '0h', complaints: 0 },
              { time: '2h', complaints: Math.floor(incident.complaint_count * 0.3) },
              { time: '4h', complaints: Math.floor(incident.complaint_count * 0.7) },
              { time: '6h', complaints: incident.complaint_count },
              { time: `${Math.ceil(incident.duration_minutes / 60)}h`, complaints: 0 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Line type="monotone" dataKey="complaints" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Impact Metrics Over Time */}
        <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
          <h3 className="text-xl font-bold text-gray-100 mb-4">Impact Metrics Over Time</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={[
              { time: '0h', traffic: incident.avg_traffic_gbps * 0.5, users: incident.peak_active_users * 0.4 },
              { time: '2h', traffic: incident.avg_traffic_gbps * 0.8, users: incident.peak_active_users * 0.7 },
              { time: '4h', traffic: incident.avg_traffic_gbps, users: incident.peak_active_users },
              { time: `${Math.ceil(incident.duration_minutes / 60)}h`, traffic: incident.avg_traffic_gbps * 0.5, users: incident.peak_active_users * 0.5 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Legend />
              <Bar dataKey="traffic" fill="#3b82f6" name="Traffic (Gbps)" />
              <Bar dataKey="users" fill="#10b981" name="Active Users" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Timeline */}
      <div className="mb-8 border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
        <h2 className="text-2xl font-bold text-gray-100 mb-6">Incident Timeline</h2>
        
        <div className="relative">
          {[
            {
              time: '00:00',
              title: 'Incident Detected',
              description: `${incident.component} component failure detected`,
              severity: 'critical',
            },
            {
              time: '05:30',
              title: 'Complaints Received',
              description: `Initial customer complaints: ${incident.complaint_count} reports`,
              severity: 'warning',
            },
            {
              time: '12:00',
              title: 'Peak Impact',
              description: `Maximum affected customers: ${incident.affected_customers}`,
              severity: 'critical',
            },
            {
              time: `${incident.duration_minutes}:00`,
              title: 'Incident Resolved',
              description: `${incident.component} restored to normal operation`,
              severity: 'success',
            },
          ].map((event, idx, arr) => (
            <div key={idx} className="flex gap-4 mb-6 last:mb-0">
              {/* Timeline dot */}
              <div className="flex flex-col items-center">
                <div
                  className={`w-4 h-4 rounded-full border-2 ${
                    event.severity === 'critical'
                      ? 'bg-red-600 border-red-400'
                      : event.severity === 'warning'
                      ? 'bg-yellow-600 border-yellow-400'
                      : 'bg-green-600 border-green-400'
                  }`}
                ></div>
                {idx !== arr.length - 1 && (
                  <div className="w-0.5 h-12 bg-gray-700 mt-2"></div>
                )}
              </div>
              
              {/* Event content */}
              <div className="pb-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-sm text-gray-400">{event.time}</span>
                  <span className="font-semibold text-gray-100">{event.title}</span>
                </div>
                <p className="text-gray-400 text-sm">{event.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>



      {/* Customer Impact Summary */}
      <div className="mb-8 border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
        <h2 className="text-2xl font-bold text-gray-100 mb-4">Customer Impact Summary</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-800 rounded p-4 border border-gray-700 flex items-center gap-3">
            <Users className="text-red-400" size={24} />
            <div>
              <p className="text-gray-400 text-sm">Affected Customers</p>
              <p className="text-2xl font-bold text-gray-100">{incident.affected_customers}</p>
            </div>
          </div>
          
          <div className="bg-gray-800 rounded p-4 border border-gray-700 flex items-center gap-3">
            <TrendingUp className="text-orange-400" size={24} />
            <div>
              <p className="text-gray-400 text-sm">Peak Traffic</p>
              <p className="text-2xl font-bold text-gray-100">{incident.avg_traffic_gbps} Gbps</p>
            </div>
          </div>
          
          <div className="bg-gray-800 rounded p-4 border border-gray-700 flex items-center gap-3">
            <Clock className="text-yellow-400" size={24} />
            <div>
              <p className="text-gray-400 text-sm">Total Duration</p>
              <p className="text-2xl font-bold text-gray-100">{incident.duration_minutes} min</p>
            </div>
          </div>
        </div>
      </div>

      {/* Related Incidents in Region */}
      {relatedIncidents.length > 0 && (
        <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg shadow-xl">
          <h2 className="text-2xl font-bold text-gray-100 mb-4">Other Incidents in {incident.region}</h2>
          
          <div className="space-y-3">
            {relatedIncidents.slice(0, 5).map((rel) => (
              <button
                key={rel.outage_id}
                onClick={() => navigate(`/incident/${rel.outage_id}`)}
                className="w-full text-left bg-gray-800 hover:bg-gray-750 rounded p-4 border border-gray-700 hover:border-gray-600 transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-100">{rel.outage_id}</p>
                    <p className="text-sm text-gray-400">{rel.component} • Score: {rel.overall_score?.toFixed(1) || 'N/A'}</p>
                  </div>
                  <span className={`px-3 py-1 rounded text-sm font-semibold ${getSeverityColor(rel.severity)}`}>
                    {rel.severity}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentDetail;
