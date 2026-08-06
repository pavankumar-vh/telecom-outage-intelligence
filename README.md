<div align="center">
  
#  NOC Intelligence Platform
### *Enterprise Outage Impact Prioritization*

[![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)](#-status)
[![Version](https://img.shields.io/badge/Version-0.8.0-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](#)

</div>

---

##  Overview

The **NOC Intelligence Platform** is an enterprise-grade solution designed to revolutionize how Network Operations Centers (NOCs) handle telecom outages. 

Traditionally, NOC operators triage network events based strictly on technical severity—a reactive approach that completely misses the human element. This platform solves that critical gap by unifying **three disparate data streams** into a single, explainable metric. 

By analyzing technical **Network Alerts**, real-time **Customer Complaint Logs**, and regional **Usage Metrics**, the engine calculates an intelligent **Impact Score**. This ensures your teams are always fixing the issues that matter most to your business and your customers.

---

##  Key Capabilities

- **Intelligent Impact Scoring:** Proprietary algorithm blending severity (40%), customer complaints (35%), and raw traffic impact (25%).
- **Explainable AI:** Complete transparency into why an incident is prioritized, breaking down the exact drivers behind the score.
- **Smart Anomaly Detection:** Real-time flagging of complaint spikes, unusually massive customer bases, and abnormal regional concentrations.
- **Geospatial Intelligence:** Interactive, dark-themed geographic heatmaps overlaying outages against active usage density.
- **Enterprise Dashboard:** A highly optimized, responsive control center built for NOC operators with pagination, fast search, and comprehensive data export.

---

##  System Architecture

### Frontend / Dashboard Layer
- **Framework:** Streamlit for rapid data visualization and control panels.
- **Styling:** Custom true-dark CSS styling tailored for enterprise NOC environments.
- **Visuals:** Plotly and Folium for rich, interactive, and performant charting.

### Backend / Analytics Engine
- **Framework:** FastAPI (Python 3.10+) serving high-concurrency API endpoints.
- **Processing Engine:** Pandas & NumPy for vectorized scoring and anomaly calculations.
- **Resilience:** Built-in error boundaries, data quality validation, and graceful fallbacks.

---

##  Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Git**

### 1. Backend API Setup

```bash
# Clone the repository and enter the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies and launch the server
pip install -r requirements.txt
python main.py
```
*The API will be available at `http://localhost:8000`*

### 2. Dashboard Interface Setup

```bash
# Open a new terminal and enter the dashboard directory
cd dashboard

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies and launch the dashboard
pip install -r requirements.txt
streamlit run app.py
```
*The NOC Command Center will be accessible at `http://localhost:8501`*

---

##  API Reference

### Data Pipeline & Health
- `GET /health` - System health and uptime metrics.
- `GET /api/data-quality` - Validation metrics, join success rates, and missing value checks.

### Incident Intelligence
- `GET /api/ranked-incidents` - Retrieves the active incidents array, fully scored and ranked.
- `GET /api/ranked-incidents/{region}` - Regional subset of ranked incidents.

### Anomaly Engine
- `GET /api/anomalies` - Returns all actively detected anomalies across the network.
- `GET /api/anomalies/{severity}` - Filters anomalies by threat level (`high`, `medium`, `low`).

---

##  Testing & Validation

The scoring and anomaly engines are fully unit-tested to ensure enterprise reliability.

```bash
cd backend
pytest
```

---

##  Security & Code Standards

- **Clean Architecture:** Strict separation of data ingestion, business logic, and API presentation.
- **Data Validation:** Pydantic models enforce strict type safety across all network payloads.
- **Responsive & Accessible:** Dashboard UI components adhere to accessibility standards while maintaining a high-density data display.

---

<div align="center">
  <p>Built with precision for modern Network Operations Centers.</p>
</div>
