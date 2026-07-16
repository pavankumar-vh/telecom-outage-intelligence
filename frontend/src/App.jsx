import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-dark-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">NOC Outage Impact Dashboard</h1>
        <p className="text-gray-400 mb-8">Telecom Outage Impact Prioritization System</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
            <h2 className="text-xl font-semibold mb-2">Active Outages</h2>
            <p className="text-3xl font-bold text-brand-primary">—</p>
            <p className="text-gray-400 text-sm mt-2">Loading data...</p>
          </div>
          
          <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
            <h2 className="text-xl font-semibold mb-2">Avg Impact Score</h2>
            <p className="text-3xl font-bold text-brand-secondary">—</p>
            <p className="text-gray-400 text-sm mt-2">Loading data...</p>
          </div>
          
          <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
            <h2 className="text-xl font-semibold mb-2">Regions Affected</h2>
            <p className="text-3xl font-bold">—</p>
            <p className="text-gray-400 text-sm mt-2">Loading data...</p>
          </div>
        </div>

        <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <h2 className="text-2xl font-bold mb-4">Ranked Incidents</h2>
          <p className="text-gray-400">No incident data available yet.</p>
        </div>
      </div>
    </div>
  )
}

export default App
