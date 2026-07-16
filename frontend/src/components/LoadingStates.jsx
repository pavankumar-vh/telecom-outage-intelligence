import React from 'react';

/**
 * Skeleton Loader for KPI Cards
 */
export const KPICardSkeleton = () => (
  <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 animate-pulse">
    <div className="mb-4 h-4 w-24 bg-gray-700 rounded"></div>
    <div className="h-8 w-16 bg-gray-700 rounded"></div>
  </div>
);

/**
 * Skeleton Loader for Table Rows
 */
export const TableRowSkeleton = () => (
  <tr className="border-b border-gray-700">
    <td className="px-4 py-3">
      <div className="h-4 w-4 bg-gray-700 rounded animate-pulse"></div>
    </td>
    <td className="px-4 py-3">
      <div className="h-4 w-24 bg-gray-700 rounded animate-pulse"></div>
    </td>
    <td className="px-4 py-3">
      <div className="h-4 w-20 bg-gray-700 rounded animate-pulse"></div>
    </td>
    <td className="px-4 py-3">
      <div className="h-4 w-16 bg-gray-700 rounded animate-pulse"></div>
    </td>
    <td className="px-4 py-3">
      <div className="h-4 w-32 bg-gray-700 rounded animate-pulse"></div>
    </td>
    <td className="px-4 py-3">
      <div className="h-4 w-12 bg-gray-700 rounded animate-pulse"></div>
    </td>
    <td className="px-4 py-3">
      <div className="h-4 w-12 bg-gray-700 rounded animate-pulse"></div>
    </td>
    <td className="px-4 py-3">
      <div className="h-4 w-8 bg-gray-700 rounded animate-pulse"></div>
    </td>
  </tr>
);

/**
 * Skeleton Loader for Chart
 */
export const ChartSkeleton = () => (
  <div className="border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg animate-pulse">
    <div className="h-6 w-40 bg-gray-700 rounded mb-4"></div>
    <div className="flex flex-col gap-2">
      <div className="h-32 w-full bg-gray-800 rounded"></div>
    </div>
  </div>
);

/**
 * Skeleton Loader for Detail Page Header
 */
export const DetailHeaderSkeleton = () => (
  <div className="mb-8 border border-gray-700 rounded-lg p-6 bg-gray-900 backdrop-blur-lg animate-pulse">
    <div className="flex items-start justify-between mb-4">
      <div className="flex-1">
        <div className="h-8 w-40 bg-gray-700 rounded mb-2"></div>
        <div className="h-4 w-56 bg-gray-700 rounded"></div>
      </div>
      <div className="text-right">
        <div className="h-10 w-20 bg-gray-700 rounded mb-2"></div>
        <div className="h-4 w-24 bg-gray-700 rounded"></div>
      </div>
    </div>
    
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="h-3 w-16 bg-gray-700 rounded mb-2"></div>
          <div className="h-6 w-20 bg-gray-700 rounded"></div>
        </div>
      ))}
    </div>
  </div>
);

/**
 * Full Page Loading Skeleton
 */
export const DashboardSkeleton = () => (
  <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6">
    <div className="max-w-7xl mx-auto">
      {/* Header Skeleton */}
      <div className="mb-8 border-b border-gray-700 pb-4">
        <div className="h-8 w-64 bg-gray-700 rounded mb-2 animate-pulse"></div>
        <div className="h-4 w-96 bg-gray-700 rounded animate-pulse"></div>
      </div>

      {/* KPI Cards Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[...Array(4)].map((_, i) => (
          <KPICardSkeleton key={i} />
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {[...Array(4)].map((_, i) => (
          <ChartSkeleton key={i} />
        ))}
      </div>

      {/* Table Skeleton */}
      <div className="rounded-lg border border-gray-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-800 border-b border-gray-700">
            <tr>
              <th className="px-4 py-3 text-left"></th>
              <th className="px-4 py-3 text-left">
                <div className="h-4 w-24 bg-gray-700 rounded animate-pulse"></div>
              </th>
              <th className="px-4 py-3 text-left">
                <div className="h-4 w-16 bg-gray-700 rounded animate-pulse"></div>
              </th>
              <th className="px-4 py-3 text-left">
                <div className="h-4 w-20 bg-gray-700 rounded animate-pulse"></div>
              </th>
              <th className="px-4 py-3 text-left">
                <div className="h-4 w-24 bg-gray-700 rounded animate-pulse"></div>
              </th>
              <th className="px-4 py-3 text-left">
                <div className="h-4 w-16 bg-gray-700 rounded animate-pulse"></div>
              </th>
              <th className="px-4 py-3 text-left">
                <div className="h-4 w-16 bg-gray-700 rounded animate-pulse"></div>
              </th>
              <th className="px-4 py-3 text-center">
                <div className="h-4 w-12 bg-gray-700 rounded animate-pulse mx-auto"></div>
              </th>
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <TableRowSkeleton key={i} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);
