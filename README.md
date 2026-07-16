# NOC Outage Impact Prioritization System

A comprehensive MVP for helping telecom Network Operations Centers (NOCs) prioritize outages by combining network alerts, customer complaints, and usage metrics into a single, explainable impact score.

## Project Overview

This application addresses a critical gap in telecom outage management: currently, operators decide outage priorities based on technical severity alerts alone, without visibility into actual customer impact. 

By centralizing three data sources:
- **Network Outage Alerts** - Technical severity and scope
- **Customer Complaint Logs** - Voice of customer
- **Usage Metrics** - Business impact (affected traffic volume)

The system calculates an explainable **Impact Score** that reflects real business impact, allowing teams to prioritize what truly matters first.

---

## 🚀 Technology Stack

### Frontend
- **React 18** - UI library
- **Vite** - Build tool for fast development
- **Tailwind CSS** - Utility-first styling
- **React Router** - Navigation
- **Recharts** - Data visualization
- **React Icons** - Icon library

### Backend
- **Python 3.10+**
- **FastAPI** - Modern, fast web framework
- **Pandas** - Data processing and analysis
- **NumPy** - Numerical computations

### Dashboard
- **Streamlit** - Data dashboard framework

### Version Control
- **Git** - Distributed version control
- **GitHub** - Repository hosting

## 📁 Project Structure

```
telecom-outage-intelligence/
├── frontend/                    # React + Vite application
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   ├── pages/              # Page-level components
│   │   ├── layouts/            # Layout wrappers
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API client services
│   │   ├── assets/             # Images, icons, etc.
│   │   ├── App.jsx             # Main app component
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── public/                 # Static assets
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── index.html
│
├── backend/                     # FastAPI application
│   ├── api/                    # API route handlers
│   │   ├── data.py             # Data ingestion endpoints
│   │   ├── incidents.py        # Incident ranking endpoints
│   │   └── anomalies.py        # Anomaly detection endpoints
│   ├── services/               # Business logic layer
│   ├── models/                 # Pydantic models & schemas
│   ├── utils/                  # Utility functions
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variables template
│
├── dashboard/                  # Streamlit dashboard
│   ├── app.py                  # Main dashboard application
│   └── requirements.txt        # Python dependencies
│
├── data/                       # Data directory
│   ├── outage_alerts.csv       # Network outage alerts (Phase 2)
│   ├── complaint_logs.csv      # Customer complaints (Phase 2)
│   ├── usage_metrics.csv       # Regional usage data (Phase 2)
│   └── README.md               # Data documentation
│
├── docs/                       # Project documentation
│   ├── ARCHITECTURE.md         # System architecture
│   ├── API.md                  # API documentation
│   └── DEPLOYMENT.md           # Deployment guide
│
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── PHASE_ROADMAP.md           # Development phase breakdown
```

## ⚡ Quick Start

### Prerequisites
- **Node.js 18+** and npm (for frontend)
- **Python 3.10+** (for backend and dashboard)
- **Git**

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

### Dashboard Setup

```bash
cd dashboard
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## 🗺️ Development Roadmap

The project is built in **8 incremental phases**, each leaving the application in a working state:

### Phase 1: Project Initialization ✅ 
- ✅ Set up React + Vite frontend with Tailwind CSS
- ✅ Initialize FastAPI backend
- ✅ Set up Streamlit dashboard
- ✅ Create project folder structure
- ✅ Configure environment files and dependencies

### Phase 2: Data Pipeline ✅
- ✅ Load datasets (outage alerts, complaints, usage metrics)
- ✅ Clean and normalize datasets
- ✅ Join datasets on region and timestamp proximity
- ✅ Validate data quality (95%+ join success rate)
- ✅ Expose `/api/processed-data` endpoint
- ✅ Create data quality metrics endpoint
- ✅ Data summary statistics endpoint
- ✅ Test pipeline with sample data (10 incidents, 7 regions, 9,330 affected customers)

### Phase 3: Impact Scoring Engine ✅
- ✅ Implement explainable scoring algorithm
- ✅ Combine severity (40%) + complaints (35%) + usage impact (25%)
- ✅ Generate detailed explanations for each score
- ✅ Rank incidents by impact score
- ✅ Expose `/api/ranked-incidents` endpoint
- ✅ Add regional ranking endpoint `/api/ranked-incidents/{region}`
- ✅ Comprehensive unit tests (7/7 passing)
- ✅ Test with real data pipeline (10 incidents scored successfully)
- ✅ Scoring formula validated across critical, major, warning, and minor severities

### Phase 4: Anomaly Detection ✅
- ✅ Implement complaint spike detection (1.5x baseline threshold)
- ✅ Implement regional concentration detection (3+ incidents in region)
- ✅ Implement customer base anomaly detection (1.8x baseline customers)
- ✅ Implement high impact region detection (1.6x regional traffic baseline)
- ✅ Create `/api/anomalies` endpoint with all anomaly types
- ✅ Add `/api/anomalies/{severity}` endpoint for severity filtering
- ✅ Add `/api/anomalies/region/{region}` endpoint for regional filtering
- ✅ Comprehensive unit tests (7/7 passing)
- ✅ Test with real data pipeline (5 incidents with anomalies detected)
- ✅ Anomaly severity levels: HIGH, MEDIUM, LOW

### Phase 5: Dashboard MVP ✅
- ✅ Build KPI cards (active outages, avg impact score, affected customers, regions impacted)
- ✅ Create incident table with impact scores, severity, and anomaly flags
- ✅ Add region filter with all available regions
- ✅ Add severity filter (Critical, Major, Warning, Minor)
- ✅ Add impact score range slider filter
- ✅ Display severity distribution pie chart
- ✅ Display regional impact bar chart
- ✅ Display impact score distribution chart
- ✅ Display complaints vs impact score chart
- ✅ Create expandable incident rows with detailed scoring breakdown
- ✅ Integrate anomaly flags into incident table
- ✅ Add actionable recommendations display
- ✅ Connect all backend APIs (ranked incidents, anomalies)
- ✅ Add auto-refresh every 30 seconds
- ✅ Add manual refresh button with loading state
- ✅ Add error handling and alerts
- ✅ Dark theme with Tailwind CSS styling
- ✅ Responsive design (mobile, tablet, desktop)

### Phase 6: Incident Detail Views ✅
- ✅ Build incident detail drill-down screen
- ✅ Show incident timeline with event progression
- ✅ Display complaint history progression chart
- ✅ Show impact metrics over time (traffic vs users)
- ✅ Add regional incidents view with component breakdown
- ✅ Show detailed impact explanation with score component breakdown
- ✅ Link from incident table rows to detail views
- ✅ Implement React Router for navigation
- ✅ Support related incidents in same region with quick navigation
- ✅ Add back navigation to dashboard
- ✅ Responsive design for all screen sizes
- ✅ Loading states and error handling

### Phase 7: Polish & UX ✅
- ✅ Implement error boundary for crash recovery
- ✅ Add loading skeleton screens for smooth UX
- ✅ Create empty state displays for no data
- ✅ Add search functionality across incident table
- ✅ Implement column sorting (ascending/descending)
- ✅ Add pagination for large incident lists
- ✅ Implement CSV export capability
- ✅ Add loading spinners and error messages
- ✅ Improve error handling throughout
- ✅ Responsive design for all features

### Phase 8: MVP Completion
- End-to-end testing
- Bug fixes and optimization
- Final documentation
- Production-ready build
- Deployment setup

## 🎯 Key Features

### Explainable Impact Scores
Each outage gets a score based on:
- **Technical Severity** (from alerts)
- **Customer Impact** (complaint volume and spike rate)
- **Business Impact** (affected customer base and traffic volume)

The reasoning is always transparent, showing which factors contributed most to the ranking.

### Smart Anomaly Detection
Automatically flags unusual patterns:
- Complaint spikes in regions
- Outages affecting unexpectedly large customer bases
- Regional deviations from normal patterns

### Real-time Ranking
As new data arrives, the incident priority automatically re-ranks, ensuring operators always see the highest-impact items first.

### Regional Intelligence
Understand impact by geographic region:
- Which regions are most affected
- Regional health trends
- Correlation between outages and complaints

## 🔌 API Reference

### Health Check
```
GET /health
```

### Data Pipeline (Phase 2)
```
GET /api/processed-data
```
Returns cleaned and joined dataset with data quality metrics.

```
GET /api/data-quality
```
Returns validation metrics (join success rate, complete records, etc.).

```
GET /api/data-summary
```
Returns summary statistics (total incidents, regions, affected customers, etc.).

### Incident Ranking (Phase 3)
```
GET /api/ranked-incidents
```
Returns all incidents ranked by impact score (highest to lowest).

**Response Format:**
```json
{
  "status": "success",
  "total_incidents": 10,
  "incidents": [
    {
      "outage_id": "INC-4029",
      "region": "US-SOUTH-01",
      "timestamp": "2026-07-15T10:15:00",
      "severity": "Critical",
      "duration_minutes": 180,
      "overall_score": 75.0,
      "rank": 1,
      "severity_score": {
        "level": "Critical",
        "normalized_value": 1.0,
        "contribution": 40.0
      },
      "complaint_score": {
        "complaint_count": 3,
        "max_escalation": 4,
        "normalized_value": 0.85,
        "contribution": 29.75
      },
      "usage_score": {
        "avg_traffic_gbps": 550.5,
        "peak_active_users": 105000,
        "peak_utilization": 92.5,
        "normalized_value": 0.75,
        "contribution": 18.75
      },
      "explanation": "[HIGH] Impact Score: 75.0/100 | Severity: Critical incident | Complaints: 3 reports (escalation level 4) | Usage Impact: 105,000 users, 550.5 Gbps | Primary driver: SEVERITY"
    }
  ]
}
```

**Scoring Formula:**
- Impact Score = (0.40 × Severity) + (0.35 × Complaints) + (0.25 × Usage Impact)
- All components normalized to 0-100 scale
- Results ranked highest to lowest impact

```
GET /api/ranked-incidents/{region}
```
Returns incidents ranked by impact score for a specific region.

### Anomalies (Phase 4)
```
GET /api/anomalies
```
Returns all detected anomalies in incident data with severity levels.

**Anomaly Types:**
- `complaint_spike` - Complaints exceed 1.5x baseline (severity: HIGH/MEDIUM/LOW)
- `customer_base_anomaly` - Affected customers exceed 1.8x baseline
- `regional_concentration` - 3+ incidents in same region
- `high_impact_region` - Traffic exceeds 1.6x regional baseline

**Response Format:**
```json
{
  "status": "success",
  "total_incidents_analyzed": 10,
  "incidents_with_anomalies": 5,
  "total_anomalies": 7,
  "high_severity_anomalies": 1,
  "incidents": [
    {
      "outage_id": "INC-4029",
      "region": "US-SOUTH-01",
      "incident_severity": "Critical",
      "complaint_count": 3,
      "affected_customers": 2950,
      "avg_traffic_gbps": 550.5,
      "has_anomalies": true,
      "total_flags": 1,
      "high_severity_count": 1,
      "primary_concern": "Unusual customer base affected: 2,950 customers (baseline: 933)",
      "anomaly_flags": [
        {
          "outage_id": "INC-4029",
          "region": "US-SOUTH-01",
          "anomaly_type": "customer_base_anomaly",
          "severity": "high",
          "description": "Unusual customer base affected: 2,950 customers (baseline: 933)",
          "threshold_value": 1677.4,
          "actual_value": 2950.0,
          "deviation_percent": 215.8,
          "recommendation": "This incident impacts more customers than typical - escalate to management"
        }
      ]
    }
  ]
}
```

```
GET /api/anomalies/{severity}
```
Returns anomalies filtered by severity level (high, medium, low).

```
GET /api/anomalies/region/{region}
```
Returns anomalies detected in a specific region.

## ⚙️ Environment Variables

### Backend (.env)
```
ENVIRONMENT=development
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
```

## 📊 Running Tests

```bash
# Backend tests (Phase 3+)
cd backend
pytest
```

## 🏗️ Building for Production

### Frontend
```bash
cd frontend
npm run build
```

Build artifacts will be in `frontend/dist/`

### Backend
```bash
# Ensure all dependencies are installed
pip install -r backend/requirements.txt
```

Run with production ASGI server:
```bash
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## 📖 Documentation

- [API Documentation](./docs/API.md) - Detailed endpoint documentation
- [Architecture](./docs/ARCHITECTURE.md) - System design and data flow
- [Deployment Guide](./docs/DEPLOYMENT.md) - Production deployment instructions

## 💻 Code Quality Standards

- **Clean Architecture** - Clear separation of concerns
- **Reusable Components** - DRY principle throughout
- **Meaningful Structure** - Logical folder organization
- **Modular Code** - Single responsibility principle
- **Minimal Comments** - Self-documenting code where possible
- **Type Safety** - Pydantic models for API validation

## 🌿 Git Workflow

This project uses feature branches per development phase:

```bash
git checkout -b feature/phase-X-description
# ... implement phase ...
git commit -m "feat(phase-X): description"
git push -u origin feature/phase-X-description
```

## 📝 Contributing

1. Create a feature branch for your phase
2. Implement features incrementally
3. Ensure code compiles and tests pass
4. Commit with descriptive messages
5. Push to GitHub

## 📄 License

[To be determined]

## 📌 Status

- **Current Phase**: 7 - Polish & UX ✅
- **Next Phase**: 8 - MVP Completion

---

**Last Updated**: July 16, 2026  
**Version**: 0.7.0 - MVP Phase 7 Complete
