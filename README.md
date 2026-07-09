# Outage Impact Prioritization System

> A data-driven outage prioritization platform that helps Network Operations Centers (NOC) prioritize incidents based on **real customer and business impact**, rather than technical severity alone.

---

## Overview

Telecom operators often manage outages using multiple disconnected systems:

- Network outage alerts
- Customer complaint logs
- Network usage metrics

Because these systems operate independently, outage prioritization is usually based only on technical severity. This can result in high-impact customer outages being addressed later than less impactful technical incidents.

The **Outage Impact Prioritization System** integrates these data sources into a single analytics platform that calculates an explainable impact score, ranks outages automatically, and highlights unusual regional patterns.

---

## Project Objectives

- Integrate outage alerts, complaint data, and network usage metrics
- Calculate an explainable outage impact score
- Automatically rank outages based on business impact
- Detect regional anomalies in complaint trends
- Provide an interactive dashboard for Network Operations teams
- Improve decision-making with transparent scoring logic

---

## Features

- Data ingestion from three independent datasets
- Automated data cleaning and validation
- Unified outage dataset
- Impact score calculation using:
  - Technical severity
  - Customer complaint volume
  - Network usage
- Dynamic outage ranking
- Region, severity, and time-based filtering
- Explainable scoring breakdown
- Regional anomaly detection
- Interactive Streamlit dashboard
- Report export functionality

---

##  System Architecture

```text
                Outage Alerts
                      │
                      │
Customer Complaints ──┼──► Data Cleaning & Validation
                      │
                      │
                Usage Metrics
                      │
                      ▼
               Data Integration
                      │
                      ▼
           Impact Score Calculation
                      │
                      ▼
          Outage Prioritization Engine
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
  Streamlit Dashboard      Export Reports
```

---

##  Project Structure

```text
Outage-Impact-Prioritization/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── notebooks/
│
├── src/
│   ├── data_ingestion.py
│   ├── preprocessing.py
│   ├── scoring.py
│   ├── anomaly_detection.py
│   ├── dashboard.py
│   └── utils.py
│
├── reports/
│
├── app.py
│
├── requirements.txt
│
├── README.md
│
└── LICENSE
```

---

##  Tech Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Machine Learning / Analytics | Scikit-learn |
| Data Validation | Pandera / Custom Validation |
| Version Control | Git & GitHub |

---

##  Impact Score Methodology

Each outage receives a composite score based on three major factors.

| Factor | Description |
|----------|-------------|
| Technical Severity | Severity level reported by the network |
| Customer Complaints | Number of complaints received |
| Usage Impact | Network traffic affected in the region |

Example scoring formula:

```text
Impact Score =
(0.40 × Severity Score)
+ (0.35 × Complaint Score)
+ (0.25 × Usage Score)
```

> **Note:** The weights are configurable and can be refined using historical outage data and operational feedback.

---

## 📈Dashboard

The Streamlit dashboard provides:

- Ranked outage list
- Impact score explanation
- Regional outage analysis
- Complaint trends
- Usage impact visualization
- Severity distribution
- Region and time filters
- Exportable reports

---

## Functional Requirements

The system supports:

- Importing outage alerts
- Importing customer complaints
- Importing usage metrics
- Dataset integration
- Data quality validation
- Impact score calculation
- Automatic outage re-ranking
- Regional anomaly detection
- Dashboard visualization
- Report export

---

## Success Metrics

The project will be considered successful if it achieves:

- ≥80% agreement with expert outage prioritization
- Dashboard updates within **5 minutes** of new outage data
- ≥95% successful record matching across datasets
- Reduced outage prioritization time
- Dashboard usability for non-technical users

---

## 📁 Data Sources

The project combines three datasets.

### 1. Outage Alerts

Contains information such as:

- Outage ID
- Region
- Timestamp
- Severity
- Network component
- Status

### 2. Customer Complaints

Contains:

- Complaint ID
- Region
- Timestamp
- Complaint category
- Customer count

### 3. Usage Metrics

Contains:

- Region
- Timestamp
- Network traffic
- Active users
- Peak utilization

---

## Data Pipeline

```text
Raw Data
     │
     ▼
Cleaning
     │
     ▼
Validation
     │
     ▼
Integration
     │
     ▼
Impact Score
     │
     ▼
Ranking
     │
     ▼
Dashboard
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/Outage-Impact-Prioritization.git
cd Outage-Impact-Prioritization
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit dashboard

```bash
streamlit run app.py
```

---

## Future Enhancements

- Real-time streaming with Kafka
- Predictive outage impact using Machine Learning
- Crew dispatch recommendations
- SLA breach prediction
- Mobile dashboard
- Automated alert notifications
- Geographic outage heat maps

---

## Stakeholders

### Primary Users

- NOC Engineers

### Secondary Users

- NOC Managers
- Customer Support Leads
- Regional Operations Analysts

### Decision Makers

- Head of Network Operations

### Business Beneficiaries

- Finance and Leadership
- Telecom Customers

---

## Project Scope

### Included

- Data integration
- Data cleaning
- Impact scoring
- Outage ranking
- Basic anomaly detection
- Streamlit dashboard

### Excluded

- Real-time streaming
- Automatic repair dispatch
- Future outage prediction
- Mobile application

---

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature-name
```

3. Commit your changes.

```bash
git commit -m "Add feature"
```

4. Push to your branch.

```bash
git push origin feature-name
```

5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## Team

Developed as part of a telecom analytics project focused on improving outage prioritization through data integration, explainable scoring, and operational intelligence.
