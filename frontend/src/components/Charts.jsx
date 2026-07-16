import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

/**
 * Severity Distribution Chart
 */
export const SeverityChart = ({ incidents = [] }) => {
  // Count incidents by severity
  const severityCount = {
    Critical: 0,
    Major: 0,
    Warning: 0,
    Minor: 0,
  };

  incidents.forEach((incident) => {
    severityCount[incident.severity] = (severityCount[incident.severity] || 0) + 1;
  });

  const data = Object.entries(severityCount).map(([severity, count]) => ({
    name: severity,
    value: count,
  }));

  const COLORS = {
    Critical: '#ef4444',
    Major: '#f97316',
    Warning: '#eab308',
    Minor: '#22c55e',
  };

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Incidents by Severity</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value} incidents`} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Average Impact Score by Region
 */
export const RegionalImpactChart = ({ incidents = [] }) => {
  // Group incidents by region and calculate average score
  const regionScores = {};

  incidents.forEach((incident) => {
    const region = incident.region || 'Unknown';
    if (!regionScores[region]) {
      regionScores[region] = { scores: [], count: 0 };
    }
    regionScores[region].scores.push(incident.overall_score);
    regionScores[region].count += 1;
  });

  const data = Object.entries(regionScores)
    .map(([region, data]) => ({
      region,
      avgScore: (data.scores.reduce((a, b) => a + b, 0) / data.count).toFixed(1),
      incidents: data.count,
    }))
    .sort((a, b) => parseFloat(b.avgScore) - parseFloat(a.avgScore));

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Avg Impact Score by Region</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="region" tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} domain={[0, 100]} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
            formatter={(value) => [value, 'Avg Score']}
          />
          <Bar dataKey="avgScore" fill="#3b82f6" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Impact Score Distribution
 */
export const ScoreDistributionChart = ({ incidents = [] }) => {
  // Bucket incidents by score ranges
  const buckets = {
    'Critical (80-100)': 0,
    'High (60-79)': 0,
    'Medium (40-59)': 0,
    'Low (0-39)': 0,
  };

  incidents.forEach((incident) => {
    const score = incident.overall_score;
    if (score >= 80) buckets['Critical (80-100)'] += 1;
    else if (score >= 60) buckets['High (60-79)'] += 1;
    else if (score >= 40) buckets['Medium (40-59)'] += 1;
    else buckets['Low (0-39)'] += 1;
  });

  const data = Object.entries(buckets).map(([range, count]) => ({
    range,
    count,
  }));

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Impact Score Distribution</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="range" tick={{ fill: '#9ca3af', fontSize: 12 }} angle={-15} textAnchor="end" height={80} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
            formatter={(value) => [value, 'Incidents']}
          />
          <Bar dataKey="count" fill="#10b981" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Complaints vs Impact Score Scatter
 */
export const ComplaintImpactChart = ({ incidents = [] }) => {
  const data = incidents.map((incident) => ({
    complaints: incident.complaint_count,
    score: incident.overall_score,
    id: incident.outage_id,
  }));

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Complaints vs Impact Score</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="complaints" tick={{ fill: '#9ca3af', fontSize: 12 }} label={{ value: 'Complaints', position: 'insideBottom', offset: -5 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} label={{ value: 'Impact Score', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
            formatter={(value, name) => [
              name === 'score' ? value.toFixed(1) : value,
              name === 'score' ? 'Score' : 'Complaints',
            ]}
          />
          <Line type="monotone" dataKey="score" stroke="#f59e0b" dot={{ fill: '#f59e0b', r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
