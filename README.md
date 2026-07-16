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

### Phase 3: Impact Scoring Engine
- Build explainable scoring algorithm
- Combine severity + complaint volume + usage impact
- Generate reasoning/explanation per incident
- Rank incidents by impact
- Unit test scoring logic

### Phase 4: Anomaly Detection
- Detect complaint spikes
- Identify regional anomalies
- Flag unusual patterns
- Integrate anomalies into incident ranking

### Phase 5: Dashboard MVP
- Build KPI cards (active outages, avg score, regions)
- Create incident table with impact scores
- Add region, severity, and time filters
- Display trend charts and complaint graphs
- Connect to backend APIs

### Phase 6: Incident Detail Views
- Build incident detail drill-down screen
- Show incident timeline
- Display complaint history
- Add regional impact view with map
- Show impact explanation

### Phase 7: Polish & UX
- Add loading and error states
- Implement empty states
- Add search functionality
- Support sorting and pagination
- Add CSV export capability
- Optimize component performance

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

### Data Pipeline
```
GET /api/processed-data
```
Returns cleaned and joined dataset.

### Incident Ranking
```
GET /api/ranked-incidents
```
Returns incidents ranked by impact score with explanations.

### Anomalies
```
GET /api/anomalies
```
Returns detected anomalies and flags.

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

- **Current Phase**: 2 - Data Pipeline ✅
- **Next Phase**: 3 - Impact Scoring Engine

---

**Last Updated**: July 16, 2026  
**Version**: 0.2.0 - MVP Phase 2 Complete
