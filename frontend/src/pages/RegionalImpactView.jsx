import React, { useState } from 'react';
import { FaArrowLeft, FaMapMarkerAlt, FaExclamationCircle, FaChartLine, FaUsers } from 'react-icons/fa';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const RegionalImpactView = ({ incidents = [], region = null, onBack = () => {} }) => {
  const [selectedMetric, setSelectedMetric] = useState('score');

  // Filter incidents by region if specified
  const regionIncidents = region 
    ? incidents.filter(inc => inc.region === region)
    : incidents;

  // Get all regions
  const regions = [...new Set(incidents.map(inc => inc.region))].sort();
  const [activeRegion, setActiveRegion] = useState(region || regions[0]);

  const filtered = incidents.filter(inc => inc.region === activeRegion);

  // Calculate regional metrics
  const metrics = {
    totalIncidents: filtered.length,
    avgScore: filtered.length > 0 ? (filtered.reduce((sum, inc) => sum + (inc.overall_score || 0), 0) / filtered.length).toFixed(1) : 0,
    totalAffected: filtered.reduce((sum, inc) => sum + (inc.affected_customers || 0), 0),
    totalComplaints: filtered.reduce((sum, inc) => sum + (inc.complaint_count || 0), 0),
    avgTraffic: filtered.length > 0 ? (filtered.reduce((sum, inc) => sum + (inc.avg_traffic_gbps || 0), 0) / filtered.length).toFixed(2) : 0,
    peakUsers: Math.max(...filtered.map(inc => inc.peak_active_users || 0)),
  };

  // Severity distribution
  const severityData = [
    { name: 'Critical', value: filtered.filter(inc => inc.severity === 'Critical').length, color: '#dc2626' },
    { name: 'Major', value: filtered.filter(inc => inc.severity === 'Major').length, color: '#ea580c' },
    { name: 'Warning', value: filtered.filter(inc => inc.severity === 'Warning').length, color: '#eab308' },
    { name: 'Minor', value: filtered.filter(inc => inc.severity === 'Minor').length, color: '#16a34a' },
  ].filter(s => s.value > 0);

  // Component breakdown
  const componentData = Object.entries(
    filtered.reduce((acc, inc) => {
      acc[inc.component] = (acc[inc.component] || 0) + 1;
      return acc;
    }, {})
  ).map(([component, count]) => ({ component, count }));

  // Impact scores by component
  const componentScores = Object.entries(
    filtered.reduce((acc, inc) => {
      if (!acc[inc.component]) acc[inc.component] = [];
      acc[inc.component].push(inc.overall_score || 0);
      return acc;
    }, {})
  ).map(([component, scores]) => ({
    component,
    avgScore: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1),
    maxScore: Math.max(...scores).toFixed(1),
  }));

  // Traffic trend
  const trafficData = filtered.map((inc, idx) => ({
    incident: inc.outage_id,
    traffic: inc.avg_traffic_gbps || 0,
    complaints: inc.complaint_count || 0,
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6">
      {/* Header */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 mb-8 text-blue-400 hover:text-blue-300 transition font-semibold"
      >
        <FaArrowLeft size={20} /> Back
      </button>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <FaMapMarkerAlt className="text-blue-400" size={28} />
          <h1 className="text-4xl font-bold text-gray-100">Regional Impact Analysis</h1>
        </div>
        <p className="text-gray-400">Detailed view of incidents and impact metrics by region</p>
      </div>

      {/* Region Selector */}
      <div className="mb-8 border border-gray-700 rounded-lg p-4 bg-gray-900 backdrop-blur-lg">
        <p className="text-gray-400 text-sm mb-3">Select Region</p>
        <div className="flex flex-wrap gap-2">
          {regions.map(reg => (
            <button
              key={reg}
              onClick={() => setActiveRegion(reg)}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                activeRegion === reg
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
              }`}
            >
              {reg}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 backdrop-blur-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm font-semibold">Total Incidents</span>
            <FaExclamationCircle className="text-red-400" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-100">{metrics.totalIncidents}</p>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 backdrop-blur-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm font-semibold">Average Impact Score</span>
            <FaChartLine className="text-blue-400" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-100">{metrics.avgScore}</p>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 backdrop-blur-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm font-semibold">Affected Customers</span>
            <FaUsers className="text-orange-400" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-100">{metrics.totalAffected}</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Severity Distribution */}
        <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg">
          <h3 className="text-xl font-bold text-gray-100 mb-4">Severity Distribution</h3>
          {severityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '8px' }}
                  labelStyle={{ color: '#f3f4f6' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-12">No incidents in this region</p>
          )}
        </div>

        {/* Component Impact */}
        <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg">
          <h3 className="text-xl font-bold text-gray-100 mb-4">Incidents by Component</h3>
          {componentData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={componentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="component" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '8px' }}
                  labelStyle={{ color: '#f3f4f6' }}
                />
                <Bar dataKey="count" fill="#3b82f6" name="Incidents" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-12">No components affected</p>
          )}
        </div>

        {/* Component Score Analysis */}
        <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg lg:col-span-2">
          <h3 className="text-xl font-bold text-gray-100 mb-4">Component Impact Scores</h3>
          {componentScores.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={componentScores}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="component" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '8px' }}
                  labelStyle={{ color: '#f3f4f6' }}
                />
                <Legend />
                <Bar dataKey="avgScore" fill="#10b981" name="Average Score" />
                <Bar dataKey="maxScore" fill="#ef4444" name="Maximum Score" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-center py-12">No data available</p>
          )}
        </div>
      </div>

      {/* Regional Statistics */}
      <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg">
        <h3 className="text-xl font-bold text-gray-100 mb-6">Regional Statistics</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Traffic Statistics */}
          <div>
            <h4 className="text-lg font-semibold text-gray-100 mb-4">Network Traffic</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center bg-gray-800 p-3 rounded border border-gray-700">
                <span className="text-gray-400">Average Traffic</span>
                <span className="text-gray-100 font-semibold">{metrics.avgTraffic} Gbps</span>
              </div>
              <div className="flex justify-between items-center bg-gray-800 p-3 rounded border border-gray-700">
                <span className="text-gray-400">Peak Active Users</span>
                <span className="text-gray-100 font-semibold">{metrics.peakUsers.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Complaint Statistics */}
          <div>
            <h4 className="text-lg font-semibold text-gray-100 mb-4">Customer Impact</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center bg-gray-800 p-3 rounded border border-gray-700">
                <span className="text-gray-400">Total Complaints</span>
                <span className="text-gray-100 font-semibold">{metrics.totalComplaints}</span>
              </div>
              <div className="flex justify-between items-center bg-gray-800 p-3 rounded border border-gray-700">
                <span className="text-gray-400">Total Affected Customers</span>
                <span className="text-gray-100 font-semibold">{metrics.totalAffected.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegionalImpactView;
