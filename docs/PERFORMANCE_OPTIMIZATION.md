"""
Frontend performance optimization configuration
Lazy loading, code splitting, and memoization setup
"""

# Code splitting entry points for Vite
# Add to vite.config.js rollupOptions.output
VITE_CODE_SPLIT_CONFIG = {
    "build": {
        "rollupOptions": {
            "output": {
                "manualChunks": {
                    "vendor": [
                        "react",
                        "react-dom",
                        "react-router-dom"
                    ],
                    "recharts": [
                        "recharts"
                    ],
                    "utils": [
                        "react-icons"
                    ]
                }
            }
        }
    }
}

# React lazy loading configuration
LAZY_LOADING_COMPONENTS = {
    "IncidentDetail": "frontend/src/pages/IncidentDetail.jsx",
    "RegionalImpactView": "frontend/src/pages/RegionalImpactView.jsx",
    "Dashboard": "frontend/src/pages/Dashboard.jsx"
}

# Memoization optimization hints
MEMOIZATION_CANDIDATES = {
    "getFilteredIncidents": "Expensive calculation - filter 1000+ incidents",
    "calculateMetrics": "Expensive calculation - aggregate metrics",
    "getRankedIncidents": "Expensive calculation - sort and process",
    "getAvailableRegions": "Can be memoized - regions don't change",
    "FilterBar": "Prevent re-renders when parent updates",
    "IncidentTable": "Expensive rendering - memoize table rows",
    "Charts": "Expensive rendering - prevent unnecessary re-renders"
}

# Performance thresholds
PERFORMANCE_TARGETS = {
    "first_contentful_paint": "< 1.5s",
    "largest_contentful_paint": "< 2.5s",
    "time_to_interactive": "< 3.5s",
    "cumulative_layout_shift": "< 0.1",
    "bundle_size": "< 200kb (gzipped)",
    "initial_load": "< 3s on 4G",
    "route_transition": "< 500ms"
}
