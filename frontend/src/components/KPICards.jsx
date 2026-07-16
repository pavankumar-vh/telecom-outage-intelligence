import React from 'react';
import { AlertTriangle, Users, Globe, TrendingUp } from 'react-icons/fa';

/**
 * KPI Card Component
 * 
 * Displays a single key performance indicator with icon and value
 */
export const KPICard = ({ title, value, icon: Icon, color = 'blue', trend = null }) => {
  const colorClasses = {
    red: 'bg-red-900/20 border-red-500/20 text-red-400',
    yellow: 'bg-yellow-900/20 border-yellow-500/20 text-yellow-400',
    green: 'bg-green-900/20 border-green-500/20 text-green-400',
    blue: 'bg-blue-900/20 border-blue-500/20 text-blue-400',
  };

  return (
    <div className={`${colorClasses[color]} border border-opacity-30 rounded-lg p-6 backdrop-blur-sm`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium mb-2">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 ${trend > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% from last hour
            </p>
          )}
        </div>
        <Icon className={`text-2xl opacity-20`} />
      </div>
    </div>
  );
};

/**
 * KPI Cards Container
 * 
 * Displays all dashboard KPIs
 */
export const KPIContainer = ({ metrics }) => {
  const kpis = [
    {
      title: 'Active Outages',
      value: metrics?.activeOutages || 0,
      icon: AlertTriangle,
      color: metrics?.activeOutages > 3 ? 'red' : 'yellow',
    },
    {
      title: 'Avg Impact Score',
      value: metrics?.avgScore ? metrics.avgScore.toFixed(1) : '0.0',
      icon: TrendingUp,
      color: 'blue',
    },
    {
      title: 'Affected Customers',
      value: metrics?.affectedCustomers ? `${(metrics.affectedCustomers / 1000).toFixed(1)}K` : '0',
      icon: Users,
      color: 'red',
    },
    {
      title: 'Regions Impacted',
      value: metrics?.regions || 0,
      icon: Globe,
      color: 'yellow',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {kpis.map((kpi, index) => (
        <KPICard key={index} {...kpi} />
      ))}
    </div>
  );
};
