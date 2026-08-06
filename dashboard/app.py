"""
NOC Outage Impact Intelligence — Industry-Grade Dashboard
Streamlit · FastAPI Backend · 101K usage metrics data
Geographic heatmap via OpenStreetMap (Plotly Mapbox)

Caching Strategy:
  Layer 1 — Parquet files: pre-aggregated at startup (daily/hourly/region),
             read in <5ms vs re-aggregating 101K rows every render.
  Layer 2 — @st.cache_data: API responses (30s TTL) + parquet reads (1h TTL)
             keyed by file mtime so stale data is never served.
  Layer 3 — st.session_state: map density jitter points generated once
             per session (~500ms first time, instant thereafter).
  Layer 4 — Plotly figures: chart data built from cached aggregates only,
             no raw-row iteration during render.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import time
import io
import os

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NOC Intelligence Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════
API_BASE     = os.environ.get("NOC_API_URL", "http://localhost:8000")
DATA_DIR     = os.environ.get("NOC_DATA_DIR", "../data")
REFRESH_SECS = 30

SEVERITY_COLORS = {
    "Critical": "#ef4444",
    "Major":    "#f97316",
    "Warning":  "#eab308",
    "Minor":    "#22c55e",
}
SEVERITY_ORDER = ["Critical", "Major", "Warning", "Minor"]

REGION_PALETTE = [
    "#ef4444", "#f59e0b", "#10b981", "#3b82f6",
    "#ec4899", "#dc2626", "#14b8a6", "#f97316",
]

# Real-world coordinates for each region
REGION_COORDS = {
    "US-EAST-01":  {"lat": 40.7128, "lon": -74.0060,  "city": "New York"},
    "US-SOUTH-01": {"lat": 29.7604, "lon": -95.3698,  "city": "Houston"},
    "US-WEST-01":  {"lat": 47.6062, "lon": -122.3321, "city": "Seattle"},
    "EMEA-WEST":   {"lat": 51.5074, "lon": -0.1278,   "city": "London"},
    "EMEA-EAST":   {"lat": 50.1109, "lon":  8.6821,   "city": "Frankfurt"},
    "ASIA-PAC":    {"lat": 35.6762, "lon": 139.6503,  "city": "Tokyo"},
    "ASIA-SOUTH":  {"lat":  1.3521, "lon": 103.8198,  "city": "Singapore"},
    "LATAM":       {"lat": -23.5505,"lon": -46.6333,  "city": "São Paulo"},
}

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    margin=dict(l=12, r=12, t=50, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11)),
    hovermode="x unified",
    xaxis=dict(
        gridcolor="rgba(239,68,68,0.05)",
        zerolinecolor="rgba(239,68,68,0.1)",
        tickfont=dict(color="#64748b", size=11),
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="rgba(239,68,68,0.05)",
        zerolinecolor="rgba(239,68,68,0.1)",
        tickfont=dict(color="#64748b", size=11),
        showgrid=True,
    ),
)


MAP_STYLE = "carto-darkmatter"  # Free, no API key required

# ══════════════════════════════════════════════════════════
# CSS DESIGN SYSTEM
# ══════════════════════════════════════════════════════════
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif !important; }

.stApp {
    background: radial-gradient(ellipse at 20% 0%, rgba(239,68,68,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 100%, rgba(220,38,38,0.06) 0%, transparent 50%),
                linear-gradient(160deg, #000000 0%, #09090b 40%, #09090b 100%) !important;
    color:#e2e8f0 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #09090b 0%, #09090b 100%) !important;
    border-right:1px solid rgba(239,68,68,0.18) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
}
[data-testid="stSidebar"] * { color:#cbd5e1 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stDateInput label { color:#64748b !important; font-size:0.7rem !important; letter-spacing:0.08em !important; text-transform:uppercase !important; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#000000; }
::-webkit-scrollbar-thumb { background:linear-gradient(180deg,#ef4444,#dc2626); border-radius:99px; }

/* Header */
.noc-header {
    background: linear-gradient(135deg,rgba(239,68,68,0.12) 0%,rgba(220,38,38,0.08) 50%,rgba(59,130,246,0.12) 100%);
    border:1px solid rgba(239,68,68,0.25); border-radius:20px;
    padding:32px 40px; margin-bottom:32px; position:relative; overflow:hidden;
}
.noc-header::before {
    content:''; position:absolute; top:-60%; left:-20%; width:60%; height:200%;
    background:radial-gradient(ellipse, rgba(239,68,68,0.08) 0%, transparent 70%); pointer-events:none;
}
.noc-header::after {
    content:''; position:absolute; bottom:0; right:0; left:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(239,68,68,0.4),transparent);
}
.noc-header-title {
    font-size:1.9rem; font-weight:900; letter-spacing:-0.02em;
    background:linear-gradient(135deg,#fca5a5 0%,#ef4444 40%,#38bdf8 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin:0; padding:0;
}
.noc-header-sub { color:#475569; font-size:0.8rem; letter-spacing:0.12em; text-transform:uppercase; margin-top:6px; }
.noc-header-meta { display:flex; gap:24px; margin-top:14px; }
.noc-meta-item { display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#475569; }
.noc-meta-dot { width:6px; height:6px; border-radius:99px; }
.noc-meta-dot.green  { background:#22c55e; box-shadow:0 0 6px #22c55e; }
.noc-meta-dot.yellow { background:#eab308; box-shadow:0 0 6px #eab308; }

/* KPI Cards */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; }
.kpi-card {
    background:rgba(9,9,11,0.85); border-radius:16px; padding:24px;
    border:1px solid rgba(239,68,68,0.18); backdrop-filter:blur(16px);
    position:relative; overflow:hidden;
    transition:transform 0.2s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.kpi-card:hover { transform:translateY(-3px); border-color:rgba(239,68,68,0.4); box-shadow:0 8px 32px rgba(239,68,68,0.12); }
.kpi-card::before { content:''; position:absolute; top:0;left:0;right:0;height:2px;border-radius:16px 16px 0 0; }
.kpi-card.indigo::before { background:linear-gradient(90deg,#ef4444,#fca5a5); }
.kpi-card.red::before    { background:linear-gradient(90deg,#ef4444,#f97316); }
.kpi-card.purple::before { background:linear-gradient(90deg,#dc2626,#ec4899); }
.kpi-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#eab308); }
.kpi-glow { position:absolute; top:-20px; right:-20px; width:100px; height:100px; border-radius:50%; opacity:0.04; pointer-events:none; }
.kpi-card.indigo .kpi-glow { background:#ef4444; }
.kpi-card.red    .kpi-glow { background:#ef4444; }
.kpi-card.purple .kpi-glow { background:#dc2626; }
.kpi-card.amber  .kpi-glow { background:#f59e0b; }
.kpi-label { font-size:0.68rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#475569; margin-bottom:12px; }
.kpi-value { font-size:2.6rem; font-weight:900; color:#f1f5f9; line-height:1; letter-spacing:-0.02em; }
.kpi-sub   { font-size:0.72rem; color:#334155; margin-top:8px; }
.kpi-icon  { position:absolute; bottom:18px; right:20px; font-size:1.8rem; opacity:0.08; }

/* Section headers */
.section-header { display:flex; align-items:center; gap:12px; margin:28px 0 18px; }
.section-header-bar { width:3px; height:24px; border-radius:99px; background:linear-gradient(180deg,#ef4444,#dc2626); }
.section-header-title { font-size:0.85rem; font-weight:700; color:#64748b; letter-spacing:0.1em; text-transform:uppercase; }
.section-header-count { background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.25); color:#fca5a5; font-size:0.7rem; font-weight:700; padding:2px 10px; border-radius:99px; }

/* Badges */
.badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:99px; font-size:0.68rem; font-weight:700; letter-spacing:0.04em; }
.badge::before { content:''; width:5px; height:5px; border-radius:50%; }
.badge-Critical { background:rgba(239,68,68,0.15); color:#fca5a5; border:1px solid rgba(239,68,68,0.3); }
.badge-Critical::before { background:#ef4444; box-shadow:0 0 4px #ef4444; }
.badge-Major    { background:rgba(249,115,22,0.15); color:#fdba74; border:1px solid rgba(249,115,22,0.3); }
.badge-Major::before    { background:#f97316; box-shadow:0 0 4px #f97316; }
.badge-Warning  { background:rgba(234,179,8,0.15);  color:#fde68a; border:1px solid rgba(234,179,8,0.3); }
.badge-Warning::before  { background:#eab308; box-shadow:0 0 4px #eab308; }
.badge-Minor    { background:rgba(34,197,94,0.15);  color:#86efac; border:1px solid rgba(34,197,94,0.3); }
.badge-Minor::before    { background:#22c55e; box-shadow:0 0 4px #22c55e; }

/* Score bar */
.sbar { display:flex; align-items:center; gap:8px; }
.sbar-track { flex:1; height:5px; background:rgba(239,68,68,0.12); border-radius:99px; overflow:hidden; }
.sbar-fill { height:100%; border-radius:99px; }
.sbar-fill.c1 { background:linear-gradient(90deg,#ef4444,#f97316); }
.sbar-fill.c2 { background:linear-gradient(90deg,#f97316,#eab308); }
.sbar-fill.c3 { background:linear-gradient(90deg,#eab308,#84cc16); }
.sbar-fill.c4 { background:linear-gradient(90deg,#22c55e,#10b981); }
.sbar-val { font-size:0.82rem; font-weight:700; color:#e2e8f0; min-width:38px; text-align:right; font-family:'JetBrains Mono',monospace; }

/* Anomaly chips */
.achip { display:inline-flex; align-items:center; gap:3px; background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.28); color:#fca5a5; border-radius:4px; padding:2px 7px; font-size:0.63rem; font-weight:700; letter-spacing:0.04em; }

/* Flag cards */
.flag-card { border-radius:10px; padding:12px 14px; margin-bottom:8px; }
.flag-card.high   { background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.25); border-left:3px solid #ef4444; }
.flag-card.medium { background:rgba(234,179,8,0.07);  border:1px solid rgba(234,179,8,0.25);  border-left:3px solid #eab308; }
.flag-card.low    { background:rgba(34,197,94,0.07);  border:1px solid rgba(34,197,94,0.25);  border-left:3px solid #22c55e; }
.flag-sev { font-size:0.67rem; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px; }
.flag-sev.high   { color:#ef4444; }
.flag-sev.medium { color:#eab308; }
.flag-sev.low    { color:#22c55e; }
.flag-desc { font-size:0.78rem; color:#94a3b8; margin-bottom:4px; }
.flag-rec  { font-size:0.73rem; color:#ef4444; font-style:italic; }

/* Explanation */
.expl-box { background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.22); border-radius:10px; padding:12px 16px; margin-top:10px; }
.expl-label { font-size:0.65rem; font-weight:700; color:#ef4444; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:5px; }
.expl-text  { font-size:0.78rem; color:#94a3b8; line-height:1.6; }

/* Stat pair */
.stat-pair { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid rgba(239,68,68,0.07); }
.stat-pair:last-child { border-bottom:none; }
.stat-key { font-size:0.77rem; color:#475569; }
.stat-val { font-size:0.77rem; font-weight:600; color:#e2e8f0; font-family:'JetBrains Mono',monospace; }

/* Map container */
.map-container {
    background:rgba(9,9,11,0.85); border:1px solid rgba(239,68,68,0.22);
    border-radius:16px; overflow:hidden;
}
.map-legend-item { display:flex; align-items:center; gap:8px; font-size:0.75rem; color:#94a3b8; }
.map-legend-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }

/* Nav radio */
div[data-testid="stRadio"] > div { display:flex; flex-direction:column; gap:4px; }
div[data-testid="stRadio"] label {
    background:rgba(9,9,11,0.6); border:1px solid rgba(239,68,68,0.15);
    border-radius:10px; padding:10px 14px !important; cursor:pointer;
    font-size:0.82rem !important; font-weight:500 !important; transition:all 0.18s ease;
}
div[data-testid="stRadio"] label:hover { border-color:rgba(239,68,68,0.35); background:rgba(239,68,68,0.08); }

/* Expander */
details summary {
    background:rgba(9,9,11,0.7) !important; border:1px solid rgba(239,68,68,0.18) !important;
    border-radius:12px !important; padding:14px 18px !important; color:#94a3b8 !important;
    font-size:0.85rem !important; transition:border-color 0.2s ease, background 0.2s ease;
}
details summary:hover { border-color:rgba(239,68,68,0.35) !important; background:rgba(239,68,68,0.06) !important; }
details[open] summary { border-radius:12px 12px 0 0 !important; border-bottom-color:transparent !important; background:rgba(239,68,68,0.1) !important; }
details[open] > div:last-child { background:rgba(9,9,11,0.5) !important; border:1px solid rgba(239,68,68,0.18) !important; border-top:none !important; border-radius:0 0 12px 12px !important; padding:16px 18px !important; }

/* Inputs */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,
.stDateInput input {
    background:rgba(9,9,11,0.8) !important; border:1px solid rgba(239,68,68,0.2) !important;
    border-radius:10px !important; color:#e2e8f0 !important; font-family:'Inter',sans-serif !important;
}
.stSelectbox [data-baseweb="select"] > div:hover,
.stTextInput input:focus,
.stDateInput input:focus { border-color:rgba(239,68,68,0.45) !important; box-shadow:0 0 0 3px rgba(239,68,68,0.1) !important; }

/* Buttons */
.stButton > button {
    background:linear-gradient(135deg,rgba(239,68,68,0.2),rgba(220,38,38,0.2)) !important;
    border:1px solid rgba(239,68,68,0.35) !important; border-radius:10px !important;
    color:#fca5a5 !important; font-weight:600 !important; font-size:0.82rem !important; transition:all 0.2s ease !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,rgba(239,68,68,0.35),rgba(220,38,38,0.35)) !important;
    border-color:rgba(239,68,68,0.6) !important; box-shadow:0 4px 16px rgba(239,68,68,0.2) !important; transform:translateY(-1px) !important;
}
.stDownloadButton > button {
    background:linear-gradient(135deg,rgba(20,184,166,0.2),rgba(16,185,129,0.2)) !important;
    border:1px solid rgba(20,184,166,0.35) !important; color:#5eead4 !important;
}
.stDownloadButton > button:hover {
    background:linear-gradient(135deg,rgba(20,184,166,0.35),rgba(16,185,129,0.35)) !important;
    border-color:rgba(20,184,166,0.6) !important; box-shadow:0 4px 16px rgba(20,184,166,0.2) !important;
}

/* DataFrames */
.stDataFrame { border-radius:14px !important; overflow:hidden !important; border:1px solid rgba(239,68,68,0.18) !important; }

/* Metrics */
[data-testid="metric-container"] {
    background:rgba(9,9,11,0.8) !important; border:1px solid rgba(239,68,68,0.18) !important;
    border-radius:12px !important; padding:16px 20px !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] { color:#64748b !important; font-size:0.72rem !important; text-transform:uppercase !important; letter-spacing:0.08em !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color:#f1f5f9 !important; font-weight:800 !important; }

hr { border:none !important; height:1px !important; background:linear-gradient(90deg,transparent,rgba(239,68,68,0.2),transparent) !important; margin:24px 0 !important; }

/* Sidebar branding */
.sb-logo { text-align:center; padding:20px 0 16px; }
.sb-logo-icon { font-size:2.2rem; }
.sb-logo-name { font-size:1rem; font-weight:800; color:#fca5a5 !important; letter-spacing:0.04em; margin-top:4px; }
.sb-logo-tag  { font-size:0.6rem; color:#334155 !important; letter-spacing:0.14em; text-transform:uppercase; margin-top:2px; }
.sb-section   { font-size:0.62rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#ef4444 !important; margin:20px 0 8px; padding-left:4px; }
.sb-divider   { height:1px; background:linear-gradient(90deg,transparent,rgba(239,68,68,0.2),transparent); margin:16px 0; }
.sb-info      { font-size:0.68rem; color:#1e293b !important; text-align:center; padding:12px 0 4px; line-height:1.8; }

/* PRD badge */
.prd-badge { display:inline-flex; align-items:center; gap:6px; background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.25); color:#86efac; padding:3px 10px; border-radius:99px; font-size:0.68rem; font-weight:700; }
.prd-badge.warn { background:rgba(234,179,8,0.1); border-color:rgba(234,179,8,0.25); color:#fde68a; }
.prd-badge.miss { background:rgba(239,68,68,0.1); border-color:rgba(239,68,68,0.25); color:#fca5a5; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PARQUET PRE-AGGREGATION BOOTSTRAP
# ══════════════════════════════════════════════════════════
def _mtime(path: str) -> float:
    """Return file modification time, or 0 if file doesn't exist."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def ensure_parquet_aggregates():
    """Run once at startup: convert raw CSVs to pre-aggregated parquet files.
    Skips if parquet is newer than the CSV source."""
    csv_path     = os.path.join(DATA_DIR, "usage_metrics.csv")
    parquet_raw  = os.path.join(DATA_DIR, "usage_metrics.parquet")
    parquet_daily  = os.path.join(DATA_DIR, "usage_daily.parquet")
    parquet_hourly = os.path.join(DATA_DIR, "usage_hourly.parquet")
    parquet_region = os.path.join(DATA_DIR, "usage_region_stats.parquet")

    if not os.path.exists(csv_path):
        return

    csv_mtime = _mtime(csv_path)
    needs_rebuild = any(
        _mtime(p) < csv_mtime
        for p in [parquet_raw, parquet_daily, parquet_hourly, parquet_region]
    )

    if not needs_rebuild:
        return

    # Build all aggregates from raw CSV in one pass
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df = df.assign(
        date=df["timestamp"].dt.date,
        hour=df["timestamp"].dt.hour,
    )

    # Raw (full) parquet
    df.to_parquet(parquet_raw, index=False)

    # Daily aggregation per region
    (df.groupby(["date", "region"])
       .agg(avg_traffic=("traffic_gbps", "mean"),
            avg_users=("active_users", "mean"),
            avg_util=("peak_utilization_percent", "mean"))
       .reset_index()
       .to_parquet(parquet_daily, index=False))

    # Hourly aggregation per region
    (df.groupby(["region", "hour"])
       .agg(avg_traffic=("traffic_gbps", "mean"),
            avg_users=("active_users", "mean"),
            avg_util=("peak_utilization_percent", "mean"))
       .reset_index()
       .to_parquet(parquet_hourly, index=False))

    # Region-level summary stats
    (df.groupby("region")
       .agg(avg_traffic=("traffic_gbps", "mean"),
            avg_users=("active_users", "mean"),
            peak_util=("peak_utilization_percent", "max"),
            latest_util=("peak_utilization_percent", "last"),
            data_points=("traffic_gbps", "count"))
       .reset_index()
       .to_parquet(parquet_region, index=False))


# ══════════════════════════════════════════════════════════
# DATA LOADING  (Layer 1+2 cache: parquet + st.cache_data)
# ══════════════════════════════════════════════════════════

def _parquet_cache_key(filename: str) -> float:
    """Cache key based on file modification time — auto-invalidates on CSV change."""
    return _mtime(os.path.join(DATA_DIR, filename))


@st.cache_data(ttl=3600, show_spinner=False)
def load_usage_timeseries(_mtime_key: float = 0) -> pd.DataFrame:
    """Load full 101K usage rows from parquet (fast) or CSV (fallback)."""
    parquet = os.path.join(DATA_DIR, "usage_metrics.parquet")
    csv     = os.path.join(DATA_DIR, "usage_metrics.csv")
    if os.path.exists(parquet):
        df = pd.read_parquet(parquet)
        if "date" not in df.columns:
            df = df.assign(date=df["timestamp"].dt.date, hour=df["timestamp"].dt.hour)
        return df
    if os.path.exists(csv):
        df = pd.read_csv(csv, parse_dates=["timestamp"])
        return df.assign(date=df["timestamp"].dt.date, hour=df["timestamp"].dt.hour)
    return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def load_usage_daily(_mtime_key: float = 0) -> pd.DataFrame:
    """Pre-aggregated daily traffic per region — 154 rows, loads in <5ms."""
    path = os.path.join(DATA_DIR, "usage_daily.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    # Fallback: compute from raw
    df = load_usage_timeseries(_mtime_key)
    if df.empty:
        return pd.DataFrame()
    return (df.groupby(["date", "region"])
              .agg(avg_traffic=("traffic_gbps", "mean"),
                   avg_users=("active_users", "mean"),
                   avg_util=("peak_utilization_percent", "mean"))
              .reset_index())


@st.cache_data(ttl=3600, show_spinner=False)
def load_usage_hourly(_mtime_key: float = 0) -> pd.DataFrame:
    """Pre-aggregated hourly traffic per region — 168 rows, loads in <5ms."""
    path = os.path.join(DATA_DIR, "usage_hourly.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    df = load_usage_timeseries(_mtime_key)
    if df.empty:
        return pd.DataFrame()
    return (df.groupby(["region", "hour"])
              .agg(avg_traffic=("traffic_gbps", "mean"))
              .reset_index())


@st.cache_data(ttl=3600, show_spinner=False)
def load_region_stats(_mtime_key: float = 0) -> pd.DataFrame:
    """Per-region summary stats — 7 rows."""
    path = os.path.join(DATA_DIR, "usage_region_stats.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    df = load_usage_timeseries(_mtime_key)
    if df.empty:
        return pd.DataFrame()
    return (df.groupby("region")
              .agg(avg_traffic=("traffic_gbps", "mean"),
                   avg_users=("active_users", "mean"),
                   peak_util=("peak_utilization_percent", "max"),
                   latest_util=("peak_utilization_percent", "last"),
                   data_points=("traffic_gbps", "count"))
              .reset_index())


@st.cache_data(ttl=3600, show_spinner=False)
def load_complaint_logs(_mtime_key: float = 0) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "complaint_logs.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, parse_dates=["timestamp"])


# ══════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=30, show_spinner=False)
def fetch_ranked_incidents():
    try:
        r = requests.get(f"{API_BASE}/api/ranked-incidents", timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e), "incidents": []}


@st.cache_data(ttl=30, show_spinner=False)
def fetch_anomalies():
    try:
        r = requests.get(f"{API_BASE}/api/anomalies", timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"status": "error", "incidents": [], "total_anomalies": 0}


def clear_all_cache():
    fetch_ranked_incidents.clear()
    fetch_anomalies.clear()
    load_usage_timeseries.clear()
    load_usage_daily.clear()
    load_usage_hourly.clear()
    load_region_stats.clear()
    load_complaint_logs.clear()
    # Also reset map density in session state so it regenerates
    st.session_state.pop("map_density", None)
    st.session_state.pop("map_density_key", None)


# ══════════════════════════════════════════════════════════
# DATA TRANSFORMS
# ══════════════════════════════════════════════════════════
def incidents_to_df(incidents: list) -> pd.DataFrame:
    if not incidents:
        return pd.DataFrame()
    rows = []
    for inc in incidents:
        cs = inc.get("complaint_score", {}) or {}
        us = inc.get("usage_score", {}) or {}
        ss = inc.get("severity_score", {}) or {}
        ts_raw = inc.get("timestamp", "")
        try:
            ts = pd.to_datetime(ts_raw)
        except Exception:
            ts = None
        rows.append({
            "rank":               inc.get("rank", 0),
            "outage_id":          inc.get("outage_id", ""),
            "region":             inc.get("region", ""),
            "severity":           inc.get("severity", ""),
            "overall_score":      round(inc.get("overall_score", 0), 1),
            "duration_minutes":   inc.get("duration_minutes", 0),
            "complaint_count":    cs.get("complaint_count", inc.get("complaint_count", 0)),
            "affected_customers": inc.get("affected_customers", 0),
            "avg_traffic_gbps":   round(us.get("avg_traffic_gbps", inc.get("avg_traffic_gbps", 0)) or 0, 1),
            "peak_active_users":  us.get("peak_active_users", inc.get("peak_active_users", 0)),
            "component":          inc.get("component", ""),
            "status":             inc.get("status", "Active"),
            "timestamp":          ts,
            "explanation":        inc.get("explanation", ""),
            "sev_contribution":   round(ss.get("contribution", 0), 1),
            "cmp_contribution":   round(cs.get("contribution", 0), 1),
            "usg_contribution":   round(us.get("contribution", 0), 1),
        })
    df = pd.DataFrame(rows)
    # Attach coordinates
    df["lat"]  = df["region"].map(lambda r: REGION_COORDS.get(r, {}).get("lat", 0))
    df["lon"]  = df["region"].map(lambda r: REGION_COORDS.get(r, {}).get("lon", 0))
    df["city"] = df["region"].map(lambda r: REGION_COORDS.get(r, {}).get("city", r))
    return df


def build_anomaly_map(anomaly_data: dict) -> dict:
    result = {}
    for inc in anomaly_data.get("incidents", []):
        result[inc.get("outage_id", "")] = inc.get("anomaly_flags", [])
    return result


def apply_filters(df: pd.DataFrame, region: str, severity: str,
                  score_range: tuple, date_range: tuple | None = None) -> pd.DataFrame:
    if df.empty:
        return df
    if region != "All Regions":
        df = df[df["region"] == region]
    if severity != "All Severities":
        df = df[df["severity"] == severity]
    df = df[(df["overall_score"] >= score_range[0]) & (df["overall_score"] <= score_range[1])]
    if date_range and df["timestamp"].notna().any():
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        mask = df["timestamp"].isna() | ((df["timestamp"] >= start) & (df["timestamp"] <= end))
        df = df[mask]
    return df


# ══════════════════════════════════════════════════════════
# PLOTLY HELPERS
# ══════════════════════════════════════════════════════════
def pl(title="", height=300, **overrides) -> dict:
    layout = {**PLOTLY_BASE, "height": height}
    if title:
        layout["title"] = dict(text=title, font=dict(color="#64748b", size=13, family="Inter"), x=0, pad=dict(l=4))
    layout.update(overrides)
    return layout


def score_color_class(score: float) -> str:
    if score >= 80: return "c1"
    if score >= 60: return "c2"
    if score >= 40: return "c3"
    return "c4"


def downsample_timeseries(df: pd.DataFrame, time_col: str, val_cols: list, max_pts: int = 400) -> pd.DataFrame:
    """Downsample dense timeseries to prevent slop and improve UX."""
    if df.empty or len(df) <= max_pts:
        return df
    df_sorted = df.sort_values(time_col).copy()
    window_size = max(2, len(df_sorted) // max_pts)
    for col in val_cols:
        if col in df_sorted.columns and pd.api.types.is_numeric_dtype(df_sorted[col]):
            df_sorted[col] = df_sorted[col].rolling(window=window_size, min_periods=1, center=True).mean()
    step = max(1, len(df_sorted) // max_pts)
    return df_sorted.iloc[::step].copy()


# ══════════════════════════════════════════════════════════
# GEOGRAPHIC MAP
# ══════════════════════════════════════════════════════════
def render_geographic_map(df: pd.DataFrame, usage_df: pd.DataFrame, map_layer: str):
    """Full-featured OpenStreetMap geographic heatmap with all filter context."""
    section_header("Geographic Intelligence Map", f"{len(df)} incidents · {len(usage_df):,} telemetry pts")

    if df.empty:
        st.info("No incident data to map. Apply different filters or check backend connection.")
        return

    # ── Map layer controls ──
    lc1, lc2, lc3 = st.columns(3)
    map_mode    = lc1.selectbox("Map Layer", ["Incident Severity", "Impact Score Heatmap", "Traffic Density", "Anomaly Concentration"], key="map_mode")
    map_size_by = lc2.selectbox("Bubble Size", ["overall_score", "affected_customers", "complaint_count", "duration_minutes"], key="map_size")
    show_usage  = lc3.checkbox("Overlay usage density", value=True, key="map_usage")

    fig = go.Figure()

    # ── Usage density heatmap layer (from 101K rows) ──
    if show_usage and not usage_df.empty:
        # Aggregate to region centroids
        usage_agg = usage_df.groupby("region").agg(
            avg_traffic=("traffic_gbps", "mean"),
            avg_users=("active_users", "mean"),
        ).reset_index()
        usage_agg["lat"] = usage_agg["region"].map(lambda r: REGION_COORDS.get(r, {}).get("lat", 0))
        usage_agg["lon"] = usage_agg["region"].map(lambda r: REGION_COORDS.get(r, {}).get("lon", 0))
        usage_agg = usage_agg[usage_agg["lat"] != 0]

        # Build heatmap-style density using many copies jittered around centroid
        hm_lats, hm_lons, hm_weights = [], [], []
        import random
        rng = random.Random(42)
        for _, row in usage_agg.iterrows():
            n = max(10, int(row["avg_traffic"] / 30))
            for _ in range(n):
                hm_lats.append(row["lat"] + rng.gauss(0, 1.5))
                hm_lons.append(row["lon"] + rng.gauss(0, 1.5))
                hm_weights.append(row["avg_traffic"])

        fig.add_trace(go.Densitymapbox(
            lat=hm_lats, lon=hm_lons, z=hm_weights,
            radius=40, opacity=0.35,
            colorscale=[
                [0.0, "rgba(9,9,11,0)"],
                [0.3, "rgba(239,68,68,0.4)"],
                [0.6, "rgba(220,38,38,0.5)"],
                [0.85,"rgba(249,115,22,0.6)"],
                [1.0, "rgba(239,68,68,0.75)"],
            ],
            showscale=False,
            name="Traffic Density",
            hoverinfo="skip",
        ))

    # ── Incident bubbles ──
    size_col = map_size_by if map_size_by in df.columns else "overall_score"
    df_map = df[df["lat"] != 0].copy()

    # Normalize size to 8–55 px range
    raw_sizes = df_map[size_col].fillna(0).astype(float)
    s_min, s_max = raw_sizes.min(), raw_sizes.max()
    if s_max > s_min:
        norm = (raw_sizes - s_min) / (s_max - s_min)
    else:
        norm = pd.Series([0.5] * len(raw_sizes))
    bubble_sizes = (norm * 47 + 8).tolist()

    lats, lons, sizes, colors, texts, hovers = [], [], [], [], [], []
    pulse_lats, pulse_lons, pulse_sizes, pulse_colors = [], [], [], []

    for i, (_, row) in enumerate(df_map.iterrows()):
        sev_color = SEVERITY_COLORS.get(row["severity"], "#ef4444")
        score = row["overall_score"]
        score_color = "#ef4444" if score >= 80 else "#f97316" if score >= 60 else "#eab308" if score >= 40 else "#22c55e"
        bubble_color = sev_color if map_mode == "Incident Severity" else score_color

        hover = (
            f"<b>{row['outage_id']}</b><br>"
            f" {row.get('city', row['region'])} ({row['region']})<br>"
            f"️ {row['severity']} | Rank #{int(row['rank'])}<br>"
            f" Impact Score: <b>{score:.1f}/100</b><br>"
            f"👥 Affected: {int(row['affected_customers']):,}<br>"
            f"💬 Complaints: {int(row['complaint_count'])}<br>"
            f"⏱ Duration: {int(row['duration_minutes'])}min<br>"
            f"🔧 Component: {row.get('component','—')}"
        )

        lats.append(row["lat"])
        lons.append(row["lon"])
        sizes.append(bubble_sizes[i])
        colors.append(bubble_color)
        texts.append(row["outage_id"])
        hovers.append(hover)

        if row["severity"] == "Critical":
            pulse_lats.append(row["lat"])
            pulse_lons.append(row["lon"])
            pulse_sizes.append(bubble_sizes[i] * 1.6)
            pulse_colors.append(sev_color)

    # Render all incident bubbles as a single trace for O(1) DOM nodes
    if lats:
        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode="markers+text",
            marker=dict(size=sizes, color=colors, opacity=0.88, sizemode="diameter"),
            text=texts, textposition="top center",
            textfont=dict(color="#e2e8f0", size=9, family="JetBrains Mono"),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hovers,
            showlegend=False,
        ))

    # Render all pulse rings as a single trace
    if pulse_lats:
        fig.add_trace(go.Scattermapbox(
            lat=pulse_lats, lon=pulse_lons,
            mode="markers",
            marker=dict(size=pulse_sizes, color=pulse_colors, opacity=0.15, sizemode="diameter"),
            hoverinfo="skip", showlegend=False,
        ))

    # ── Map layout ──
    center_lat = df_map["lat"].mean() if not df_map.empty else 30
    center_lon = df_map["lon"].mean() if not df_map.empty else 0

    fig.update_layout(
        mapbox=dict(
            style=MAP_STYLE,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=1.4,
        ),
        paper_bgcolor="rgba(9,9,11,0.9)",
        height=560,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True})

    # ── Legend ──
    leg_col, stat_col = st.columns([1, 2])
    with leg_col:
        st.markdown("**Legend**")
        for sev, color in SEVERITY_COLORS.items():
            st.markdown(
                f'<div class="map-legend-item"><div class="map-legend-dot" style="background:{color};box-shadow:0 0 6px {color}40"></div>{sev}</div>',
                unsafe_allow_html=True,
            )
        if show_usage:
            st.markdown(
                '<div class="map-legend-item" style="margin-top:8px"><div class="map-legend-dot" style="background:linear-gradient(135deg,#ef4444,#ef4444);opacity:0.6"></div>Usage Density (heatmap)</div>',
                unsafe_allow_html=True,
            )

    with stat_col:
        # Regional summary table
        reg_summary = df_map.groupby("region").agg(
            incidents=("outage_id", "count"),
            avg_score=("overall_score", "mean"),
            total_customers=("affected_customers", "sum"),
            total_complaints=("complaint_count", "sum"),
            city=("city", "first"),
        ).reset_index().sort_values("avg_score", ascending=False)
        reg_summary["avg_score"] = reg_summary["avg_score"].round(1)
        reg_summary["total_customers"] = reg_summary["total_customers"].astype(int)

        st.markdown("**Regional Summary**")
        st.dataframe(
            reg_summary.rename(columns={
                "region": "Region", "city": "City", "incidents": "Incidents",
                "avg_score": "Avg Score", "total_customers": "Customers",
                "total_complaints": "Complaints",
            }),
            use_container_width=True, hide_index=True,
            column_config={
                "Avg Score": st.column_config.ProgressColumn("Avg Score", min_value=0, max_value=100, format="%.1f"),
                "Customers": st.column_config.NumberColumn("Customers"),
            }
        )

    # ── Traffic heatmap by region timeline ──
    if not usage_df.empty:
        st.markdown("---")
        section_header("Telemetry Timeline by Region", f"{len(usage_df):,} data points")

        reg_filter = df["region"].unique().tolist() if not df.empty else sorted(usage_df["region"].unique())

        # Filter usage_df to only regions in current filter
        filtered_usage = usage_df[usage_df["region"].isin(reg_filter)]

        daily = (filtered_usage.groupby(["date", "region"])
                 .agg(avg_traffic=("traffic_gbps", "mean"),
                      avg_util=("peak_utilization_percent", "mean"))
                 .reset_index())

        tc1, tc2 = st.columns(2)
        with tc1:
            fig2 = go.Figure()
            for i, region in enumerate(sorted(daily["region"].unique())):
                rdf = daily[daily["region"] == region].sort_values("date")
                fig2.add_trace(go.Scatter(
                    x=rdf["date"], y=rdf["avg_traffic"].round(1),
                    name=region, mode="lines+markers",
                    line=dict(color=REGION_PALETTE[i % len(REGION_PALETTE)], width=2),
                    marker=dict(size=4),
                    hovertemplate=f"<b>{region}</b><br>%{{x}}<br>Traffic: %{{y:.1f}} Gbps<extra></extra>",
                    fill="tozeroy", fillcolor=f"rgba({','.join(str(int(c*255)) for c in px.colors.hex_to_rgb(REGION_PALETTE[i % len(REGION_PALETTE)]))},0.04)",
                ))
            fig2.update_layout(**pl("Daily Avg Traffic (Gbps)", 280, legend=dict(orientation="h", y=-0.2, font=dict(size=9))))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        with tc2:
            # Heatmap: region × hour
            hourly = (filtered_usage.groupby(["region", "hour"])
                      .agg(avg_traffic=("traffic_gbps", "mean"))
                      .reset_index()
                      .pivot(index="region", columns="hour", values="avg_traffic"))

            fig3 = go.Figure(go.Heatmap(
                z=hourly.values,
                x=[f"{h:02d}:00" for h in hourly.columns],
                y=hourly.index.tolist(),
                colorscale=[
                    [0.0,  "rgba(9,9,11,1)"],
                    [0.3,  "rgba(239,68,68,0.7)"],
                    [0.65, "rgba(220,38,38,0.75)"],
                    [0.85, "rgba(249,115,22,0.8)"],
                    [1.0,  "rgba(239,68,68,1)"],
                ],
                hovertemplate="<b>%{y}</b><br>Hour: %{x}<br>Avg Traffic: %{z:.1f} Gbps<extra></extra>",
                colorbar=dict(tickfont=dict(color="#475569", size=9), outlinewidth=0, len=0.8, bgcolor="rgba(0,0,0,0)"),
            ))
            fig3.update_layout(**pl("Traffic Heatmap — Region × Hour", 280,
                               xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#64748b", size=9), tickangle=0),
                               yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#94a3b8", size=10))))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════
# UI COMPONENTS
# ══════════════════════════════════════════════════════════
def render_header(backend_ok: bool, total: int, last_updated: str):
    status_dot  = '<span class="noc-meta-dot green"></span>' if backend_ok else '<span class="noc-meta-dot yellow"></span>'
    status_text = "Backend Online" if backend_ok else "Backend Offline"
    st.markdown(f"""
    <div class="noc-header">
        <div class="noc-header-title"> NOC Outage Intelligence</div>
        <div class="noc-header-sub">Telecom Outage Impact Prioritization Platform · v0.8.0</div>
        <div class="noc-header-meta">
            <div class="noc-meta-item">{status_dot} {status_text}</div>
            <div class="noc-meta-item"><span class="noc-meta-dot" style="background:#ef4444;box-shadow:0 0 6px #ef4444"></span> {total} Incidents Loaded</div>
            <div class="noc-meta-item"><span class="noc-meta-dot" style="background:#475569"></span> Refreshed {last_updated}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(df: pd.DataFrame, anomaly_count: int, usage_df: pd.DataFrame):
    if df.empty:
        avg_score = 0.0
        affected_k = 0.0
    else:
        avg_score  = round(df["overall_score"].mean(), 1)
        affected_k = round(df["affected_customers"].sum() / 1000, 1)

    score_color = "#ef4444" if avg_score >= 80 else "#f97316" if avg_score >= 60 else "#eab308" if avg_score >= 40 else "#22c55e"
    score_level = "CRITICAL" if avg_score >= 80 else "HIGH" if avg_score >= 60 else "MEDIUM" if avg_score >= 40 else "LOW"

    avg_traffic = round(usage_df["traffic_gbps"].mean(), 1) if not usage_df.empty else 0.0
    peak_users  = f"{int(usage_df['active_users'].max()):,}" if not usage_df.empty else "—"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card red">
        <div class="kpi-glow"></div>
        <div class="kpi-label">Active Outages</div>
        <div class="kpi-value">{len(df)}</div>
        <div class="kpi-sub">Incidents being monitored</div>
        <div class="kpi-icon">🚨</div>
      </div>
      <div class="kpi-card indigo">
        <div class="kpi-glow"></div>
        <div class="kpi-label">Avg Impact Score</div>
        <div class="kpi-value" style="color:{score_color}">{avg_score:.1f}</div>
        <div class="kpi-sub" style="color:{score_color};opacity:0.7">{score_level} overall impact level</div>
        <div class="kpi-icon"></div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-glow"></div>
        <div class="kpi-label">Affected Customers</div>
        <div class="kpi-value">{affected_k:.1f}K</div>
        <div class="kpi-sub">Total impacted user base</div>
        <div class="kpi-icon">👥</div>
      </div>
      <div class="kpi-card amber">
        <div class="kpi-glow"></div>
        <div class="kpi-label">Anomaly Flags</div>
        <div class="kpi-value" style="color:#f59e0b">{anomaly_count}</div>
        <div class="kpi-sub">Unusual patterns detected</div>
        <div class="kpi-icon">️</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Regions Impacted",  df["region"].nunique() if not df.empty else 0)
    m2.metric("Avg Traffic",       f"{avg_traffic} Gbps", help="From 101K usage data points")
    m3.metric("Peak Active Users", peak_users)
    m4.metric("Critical Incidents",int((df["severity"] == "Critical").sum()) if not df.empty else 0)


def section_header(title: str, count=None):
    count_html = f'<span class="section-header-count">{count}</span>' if count is not None else ""
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-bar"></div>
        <div class="section-header-title">{title}</div>
        {count_html}
    </div>
    """, unsafe_allow_html=True)


def badge(severity: str) -> str:
    return f'<span class="badge badge-{severity}">{severity}</span>'


def score_bar(score: float) -> str:
    cls = score_color_class(score)
    return (f'<div class="sbar">'
            f'<div class="sbar-track"><div class="sbar-fill {cls}" style="width:{score}%"></div></div>'
            f'<span class="sbar-val">{score:.1f}</span>'
            f'</div>')


# ══════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════
def render_overview_charts(df: pd.DataFrame, usage_df: pd.DataFrame):
    section_header("Analytics Overview", len(df))
    c1, c2 = st.columns(2)

    with c1:
        sev = df["severity"].value_counts().reindex(SEVERITY_ORDER, fill_value=0).reset_index()
        sev.columns = ["Severity", "Count"]
        nz = sev[sev["Count"] > 0]
        fig = go.Figure(go.Pie(
            labels=nz["Severity"], values=nz["Count"], hole=0.62,
            marker=dict(colors=[SEVERITY_COLORS[s] for s in nz["Severity"]], line=dict(color="#000000", width=3)),
            textfont=dict(color="#e2e8f0", family="Inter", size=11),
            hovertemplate="<b>%{label}</b><br>%{value} incidents (%{percent})<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{len(df)}</b>", x=0.5, y=0.55, showarrow=False, font=dict(size=28, color="#f1f5f9", family="Inter"))
        fig.add_annotation(text="incidents",          x=0.5, y=0.38, showarrow=False, font=dict(size=11, color="#475569", family="Inter"))
        fig.update_layout(**pl("Severity Distribution", 300))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        reg = df.groupby("region").agg(avg_score=("overall_score","mean"), count=("outage_id","count")).reset_index().sort_values("avg_score")
        reg["avg_score"] = reg["avg_score"].round(1)
        bar_colors = [SEVERITY_COLORS["Critical"] if s >= 80 else SEVERITY_COLORS["Major"] if s >= 60 else SEVERITY_COLORS["Warning"] if s >= 40 else SEVERITY_COLORS["Minor"] for s in reg["avg_score"]]
        fig = go.Figure(go.Bar(
            x=reg["avg_score"], y=reg["region"], orientation="h",
            marker=dict(color=bar_colors, line=dict(color="#000000", width=1)),
            text=[f"{v:.1f}" for v in reg["avg_score"]], textposition="outside", textfont=dict(color="#64748b", size=11),
            hovertemplate="<b>%{y}</b><br>Avg Score: %{x:.1f}<br>Incidents: %{customdata}<extra></extra>", customdata=reg["count"],
        ))
        fig.update_layout(**pl("Avg Impact Score by Region", 300,
                               xaxis=dict(range=[0, 105], gridcolor="rgba(239,68,68,0.08)", tickfont=dict(color="#64748b", size=11)),
                               yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#94a3b8", size=11))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    c3, c4 = st.columns(2)
    with c3:
        bins = {"Critical\n(80–100)": 0, "High\n(60–79)": 0, "Medium\n(40–59)": 0, "Low\n(0–39)": 0}
        labels = list(bins.keys())
        for s in df["overall_score"]:
            if s >= 80:   bins[labels[0]] += 1
            elif s >= 60: bins[labels[1]] += 1
            elif s >= 40: bins[labels[2]] += 1
            else:         bins[labels[3]] += 1
        fig = go.Figure(go.Bar(
            x=labels, y=list(bins.values()),
            marker=dict(color=["#ef4444","#f97316","#eab308","#22c55e"], line=dict(color="#000000",width=1), opacity=0.85),
            text=list(bins.values()), textposition="outside", textfont=dict(color="#64748b", size=11),
            hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
        ))
        fig.update_layout(**pl("Impact Score Distribution", 300,
                          xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#94a3b8", size=10)),
                          yaxis=dict(gridcolor="rgba(239,68,68,0.08)", tickfont=dict(color="#64748b", size=11))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c4:
        fig = px.scatter(df, x="complaint_count", y="overall_score", color="severity",
                         color_discrete_map=SEVERITY_COLORS,
                         hover_data={"outage_id":True,"region":True,"severity":True},
                         labels={"complaint_count":"Complaints","overall_score":"Impact Score"},
                         size="affected_customers", size_max=28)
        fig.update_traces(marker=dict(line=dict(width=1,color="#000000"),opacity=0.85))
        fig.update_layout(**pl("Complaints vs Impact Score", 300))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Traffic intelligence
    if not usage_df.empty:
        section_header("Network Traffic Intelligence", f"{len(usage_df):,} data points")
        _render_traffic_charts(usage_df, df)


def _render_traffic_charts(usage_df: pd.DataFrame, incidents_df: pd.DataFrame = None):
    tc1, tc2 = st.columns([3, 1])
    with tc1:
        daily = usage_df.groupby(["date","region"]).agg(avg_traffic=("traffic_gbps","mean"),avg_users=("active_users","mean")).reset_index()
        regions = sorted(daily["region"].unique())
        fig = go.Figure()
        for i, region in enumerate(regions):
            rdf = daily[daily["region"]==region].sort_values("date")
            fig.add_trace(go.Scatter(x=rdf["date"], y=rdf["avg_traffic"].round(1), name=region, mode="lines",
                                     line=dict(color=REGION_PALETTE[i%len(REGION_PALETTE)],width=2),
                                     hovertemplate=f"<b>{region}</b><br>%{{x}}<br>Traffic: %{{y:.1f}} Gbps<extra></extra>"))
        fig.update_layout(**pl("Daily Avg Traffic by Region (Gbps) — 3-Week Window", 320, legend=dict(orientation="h",y=-0.18,font=dict(size=10))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tc2:
        latest = usage_df.sort_values("timestamp").groupby("region")["peak_utilization_percent"].last().reset_index().sort_values("peak_utilization_percent", ascending=False)
        fig = go.Figure()
        for _, row in latest.iterrows():
            u = row["peak_utilization_percent"]
            c = "#ef4444" if u>=90 else "#f97316" if u>=80 else "#eab308" if u>=70 else "#22c55e"
            fig.add_trace(go.Bar(x=[u],y=[row["region"]],orientation="h",marker=dict(color=c,line=dict(color="#000000",width=1)),
                                  text=[f"{u:.0f}%"],textposition="outside",textfont=dict(color="#64748b",size=10),showlegend=False,
                                  hovertemplate=f"<b>{row['region']}</b><br>Peak Utilization: {u:.0f}%<extra></extra>"))
        fig.add_vline(x=90,line_dash="dot",line_color="rgba(239,68,68,0.4)",line_width=1)
        fig.update_layout(**pl("Peak Utilization %", 320, xaxis=dict(range=[0,115],gridcolor="rgba(239,68,68,0.08)",tickfont=dict(color="#64748b",size=10)), yaxis=dict(gridcolor="rgba(0,0,0,0)",tickfont=dict(color="#94a3b8",size=10))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    hourly = usage_df.groupby(["region","hour"]).agg(avg_traffic=("traffic_gbps","mean")).reset_index().pivot(index="region",columns="hour",values="avg_traffic")
    fig = go.Figure(go.Heatmap(z=hourly.values,x=[f"{h:02d}:00" for h in hourly.columns],y=hourly.index.tolist(),
        colorscale=[[0,"rgba(9,9,11,1)"],[0.25,"rgba(239,68,68,0.6)"],[0.6,"rgba(220,38,38,0.7)"],[0.85,"rgba(249,115,22,0.8)"],[1,"rgba(239,68,68,1)"]],
        hovertemplate="<b>%{y}</b><br>Hour: %{x}<br>Avg Traffic: %{z:.1f} Gbps<extra></extra>",
        colorbar=dict(tickfont=dict(color="#475569",size=10),outlinewidth=0,bgcolor="rgba(0,0,0,0)",len=0.8)))
    fig.update_layout(**pl("Traffic Heatmap — Region × Hour of Day (Gbps)",280,
                      xaxis=dict(gridcolor="rgba(0,0,0,0)",tickfont=dict(color="#64748b",size=10),tickangle=0),
                      yaxis=dict(gridcolor="rgba(0,0,0,0)",tickfont=dict(color="#94a3b8",size=11))))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════
# INCIDENT TABLE
# ══════════════════════════════════════════════════════════
def render_incident_table(df: pd.DataFrame, anomaly_map: dict, search: str, sort_by: str):
    if df.empty:
        st.info("No incidents match the current filters.")
        return

    work = df.copy()
    if search:
        mask = (work["outage_id"].str.contains(search,case=False,na=False) |
                work["region"].str.contains(search,case=False,na=False) |
                work["component"].str.contains(search,case=False,na=False) |
                work["severity"].str.contains(search,case=False,na=False))
        work = work[mask]

    if work.empty:
        st.warning(f"No incidents match: `{search}`")
        return

    sort_map = {"Impact Score ↓":("overall_score",False),"Impact Score ↑":("overall_score",True),
                "Complaints ↓":("complaint_count",False),"Duration ↓":("duration_minutes",False),"Customers ↓":("affected_customers",False)}
    col, asc = sort_map.get(sort_by, ("overall_score", False))
    work = work.sort_values(col, ascending=asc)

    section_header("Ranked Incidents", f"{len(work)} of {len(df)}")

    items_per_page = 15
    total_pages = max(1, (len(work) - 1) // items_per_page + 1)
    if total_pages > 1:
        pc1, pc2 = st.columns([5, 1])
        with pc2:
            page = st.number_input(f"Page (1-{total_pages})", min_value=1, max_value=total_pages, value=1, step=1, key="inc_page")
    else:
        page = 1

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    for _, row in work.iloc[start_idx:end_idx].iterrows():
        flags = anomaly_map.get(row["outage_id"], [])
        anomaly_chips = " ".join(f'<span class="achip"> {f.get("anomaly_type","").replace("_"," ").title()}</span>' for f in flags[:3])
        if len(flags) > 3:
            anomaly_chips += f' <span class="achip">+{len(flags)-3} more</span>'
        dur = f"{row['duration_minutes']//60}h {row['duration_minutes']%60}m" if row["duration_minutes"] else "—"
        sev_color = SEVERITY_COLORS.get(row["severity"],"#ef4444")
        status_color = "#22c55e" if str(row["status"]).lower()=="active" else "#475569"
        ts_str = row["timestamp"].strftime("%Y-%m-%d %H:%M") if pd.notna(row["timestamp"]) else "—"

        label = f"#{row['rank']}  {row['outage_id']}  ·  {row['region']}  ·  Score: {row['overall_score']:.1f}  ·  {row['severity']}" + (f"  ·   {len(flags)}" if flags else "")

        with st.expander(label):
            st.markdown(f"""
            <div style="display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:4px 0 12px;border-bottom:1px solid rgba(239,68,68,0.12);margin-bottom:14px;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:700;color:#fca5a5;">#{row['rank']} {row['outage_id']}</span>
                {badge(row['severity'])}
                <span style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);color:#94a3b8;padding:2px 10px;border-radius:99px;font-size:0.72rem;"> {row.get('city',row['region'])}</span>
                <span style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);color:#94a3b8;padding:2px 10px;border-radius:99px;font-size:0.72rem;">⏱ {dur}</span>
                <span style="color:#475569;font-size:0.72rem;">🕐 {ts_str}</span>
                <span style="color:{status_color};font-size:0.75rem;font-weight:600;">● {row['status']}</span>
                {anomaly_chips}
            </div>
            """, unsafe_allow_html=True)

            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown("**🎯 Score Breakdown**")
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=["Severity (40%)", "Complaints (35%)", "Usage (25%)"],
                    y=[row["sev_contribution"], row["cmp_contribution"], row["usg_contribution"]],
                    marker=dict(color=["#ef4444","#f97316","#ef4444"],line=dict(color="#000000",width=1),opacity=0.85),
                    text=[f"{v:.1f}" for v in [row["sev_contribution"],row["cmp_contribution"],row["usg_contribution"]]],
                    textposition="outside", textfont=dict(color="#64748b",size=10),
                    hovertemplate="<b>%{x}</b><br>Contribution: %{y:.1f}<extra></extra>"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=190,showlegend=False,
                                  margin=dict(l=4,r=4,t=8,b=4),
                                  xaxis=dict(tickfont=dict(color="#64748b",size=9),gridcolor="rgba(0,0,0,0)"),
                                  yaxis=dict(gridcolor="rgba(239,68,68,0.08)",tickfont=dict(color="#64748b",size=9),range=[0,45]))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"score_bar_{row['outage_id']}")

                fig2 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=row["overall_score"],
                    number=dict(font=dict(color="#f1f5f9",size=28,family="Inter"),suffix="/100"),
                    gauge=dict(axis=dict(range=[0,100],tickcolor="#334155",tickfont=dict(color="#334155",size=8)),
                               bar=dict(color=sev_color,thickness=0.22),bgcolor="rgba(9,9,11,0.8)",
                               borderwidth=1,bordercolor="rgba(239,68,68,0.2)",
                               steps=[dict(range=[0,40],color="rgba(34,197,94,0.08)"),dict(range=[40,60],color="rgba(234,179,8,0.08)"),
                                      dict(range=[60,80],color="rgba(249,115,22,0.08)"),dict(range=[80,100],color="rgba(239,68,68,0.08)")],
                               threshold=dict(line=dict(color=sev_color,width=2),thickness=0.75,value=row["overall_score"]))))
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",height=140,margin=dict(l=16,r=16,t=4,b=4),font=dict(color="#94a3b8",family="Inter"))
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False}, key=f"score_gauge_{row['outage_id']}")

            with d2:
                st.markdown("** Incident Details**")
                pairs = [("Component",row.get("component","—")),
                         ("City/Area",row.get("city","—")),
                         ("Affected Customers",f"{int(row['affected_customers']):,}" if row["affected_customers"] else "—"),
                         ("Avg Traffic",f"{row['avg_traffic_gbps']:.1f} Gbps"),
                         ("Peak Active Users",f"{int(row['peak_active_users']):,}" if row["peak_active_users"] else "—"),
                         ("Complaint Count",str(int(row["complaint_count"]))),
                         ("Duration",dur),("Status",row.get("status","Active")),("Timestamp",ts_str)]
                st.markdown("".join(f'<div class="stat-pair"><span class="stat-key">{k}</span><span class="stat-val">{v}</span></div>' for k,v in pairs), unsafe_allow_html=True)

            with d3:
                st.markdown("**️ Anomaly Flags**")
                if flags:
                    for f in flags:
                        sev=f.get("severity","low"); cls=sev.lower()
                        atype=f.get("anomaly_type","").replace("_"," ").title()
                        actual=f.get("actual_value",0); thresh=f.get("threshold_value",0); dev=f.get("deviation_percent",0)
                        st.markdown(f'<div class="flag-card {cls}"><div class="flag-sev {cls}">{sev.upper()} · {atype}</div><div class="flag-desc">{f.get("description","")}</div><div style="font-size:0.71rem;color:#334155;margin-bottom:4px;">Actual: <b style="color:#e2e8f0;">{actual:.1f}</b> | Threshold: <b style="color:#e2e8f0;">{thresh:.1f}</b> | Dev: <b>{dev:.1f}%</b></div><div class="flag-rec"> {f.get("recommendation","")}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#334155;font-size:0.82rem;text-align:center;padding:24px 0;"> No anomalies detected</div>', unsafe_allow_html=True)

            if row["explanation"]:
                st.markdown(f'<div class="expl-box"><div class="expl-label">Score Explanation</div><div class="expl-text">{row["explanation"]}</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# REGIONAL ANALYSIS
# ══════════════════════════════════════════════════════════
def render_regional_analysis(df_all: pd.DataFrame, usage_df: pd.DataFrame):
    if df_all.empty:
        st.info("No incident data for regional analysis.")
        return
    section_header("Regional Analysis")
    regions = sorted(df_all["region"].unique())
    sel = st.selectbox("Select Region", regions, key="reg_sel")
    rdf = df_all[df_all["region"] == sel]
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Incidents",    len(rdf))
    k2.metric("Avg Impact Score",   f"{rdf['overall_score'].mean():.1f}" if len(rdf) else "—")
    k3.metric("Affected Customers", f"{int(rdf['affected_customers'].sum()):,}" if len(rdf) else "—")
    k4.metric("Total Complaints",   f"{int(rdf['complaint_count'].sum()):,}" if len(rdf) else "—")
    st.markdown("")
    rc1, rc2 = st.columns(2)
    with rc1:
        sev = rdf["severity"].value_counts().reindex(SEVERITY_ORDER, fill_value=0).reset_index()
        sev.columns = ["Severity","Count"]; nz = sev[sev["Count"]>0]
        fig = go.Figure(go.Pie(labels=nz["Severity"],values=nz["Count"],hole=0.58,
                               marker=dict(colors=[SEVERITY_COLORS[s] for s in nz["Severity"]],line=dict(color="#000000",width=2)),textfont=dict(color="#e2e8f0")))
        fig.update_layout(**pl(f"Severity — {sel}",280))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with rc2:
        if "component" in rdf.columns and rdf["component"].notna().any():
            comp = rdf.groupby("component")["overall_score"].mean().reset_index().sort_values("overall_score")
            comp = comp.assign(overall_score=comp["overall_score"].round(1))
            fig = go.Figure(go.Bar(x=comp["overall_score"],y=comp["component"],orientation="h",
                                   marker=dict(color="#ef4444",opacity=0.75,line=dict(color="#000000",width=1)),
                                   text=[f"{v:.1f}" for v in comp["overall_score"]],textposition="outside",textfont=dict(color="#64748b",size=11)))
            fig.update_layout(**pl(f"Avg Score by Component — {sel}",280,
                              xaxis=dict(range=[0,105],gridcolor="rgba(239,68,68,0.08)",tickfont=dict(color="#64748b",size=10)),
                              yaxis=dict(gridcolor="rgba(0,0,0,0)",tickfont=dict(color="#94a3b8",size=11))))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    if not usage_df.empty and sel in usage_df["region"].unique():
        r_usage = usage_df[usage_df["region"]==sel].sort_values("timestamp")
        r_usage_ds = downsample_timeseries(r_usage, "timestamp", ["traffic_gbps", "active_users"], max_pts=400)
        fig = make_subplots(rows=2,cols=1,shared_xaxes=True,subplot_titles=["Traffic (Gbps)","Active Users"],vertical_spacing=0.08)
        fig.add_trace(go.Scatter(x=r_usage_ds["timestamp"],y=r_usage_ds["traffic_gbps"],mode="lines",name="Traffic",line=dict(color="#ef4444",width=1.5),fill="tozeroy",fillcolor="rgba(239,68,68,0.06)",hovertemplate="%{y:.1f} Gbps<extra></extra>"),row=1,col=1)
        fig.add_trace(go.Scatter(x=r_usage_ds["timestamp"],y=r_usage_ds["active_users"],mode="lines",name="Active Users",line=dict(color="#10b981",width=1.5),fill="tozeroy",fillcolor="rgba(16,185,129,0.06)",hovertemplate="%{y:,.0f}<extra></extra>"),row=2,col=1)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=380,showlegend=False,
                          margin=dict(l=8,r=8,t=44,b=8),font=dict(family="Inter",color="#94a3b8",size=11),
                          title=dict(text=f"Network Telemetry — {sel} (Smoothed, {len(r_usage_ds):,} pts)",font=dict(color="#64748b",size=13),x=0), hovermode="x unified")
        for ax in ["xaxis","xaxis2","yaxis","yaxis2"]:
            fig.update_layout(**{ax:dict(gridcolor="rgba(239,68,68,0.08)",tickfont=dict(color="#64748b",size=10))})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    section_header(f"Incidents in {sel}", len(rdf))
    display_cols = ["rank","outage_id","severity","overall_score","complaint_count","duration_minutes","affected_customers","component","status"]
    avail = [c for c in display_cols if c in rdf.columns]
    st.dataframe(rdf[avail].sort_values("overall_score",ascending=False),use_container_width=True,hide_index=True,
                 column_config={"rank":st.column_config.NumberColumn("Rank",width="small"),"outage_id":st.column_config.TextColumn("Incident ID"),
                                "severity":st.column_config.TextColumn("Severity"),"overall_score":st.column_config.ProgressColumn("Impact Score",min_value=0,max_value=100,format="%.1f"),
                                "complaint_count":st.column_config.NumberColumn("Complaints"),"duration_minutes":st.column_config.NumberColumn("Duration (min)"),
                                "affected_customers":st.column_config.NumberColumn("Affected Cust."),"component":st.column_config.TextColumn("Component"),"status":st.column_config.TextColumn("Status")})


# ══════════════════════════════════════════════════════════
# ANOMALY INTELLIGENCE
# ══════════════════════════════════════════════════════════
def render_anomaly_intelligence(anomaly_data: dict):
    section_header("Anomaly Intelligence")
    if not anomaly_data.get("incidents"):
        st.success(" No anomalies detected in current dataset.")
        return
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Incidents w/ Anomalies", anomaly_data.get("incidents_with_anomalies",0))
    m2.metric("Total Anomaly Flags",    anomaly_data.get("total_anomalies",0))
    m3.metric("High Severity",          anomaly_data.get("high_severity_anomalies",0))
    total_analyzed = anomaly_data.get("total_incidents_analyzed",0)
    with_anom = anomaly_data.get("incidents_with_anomalies",0)
    m4.metric("Detection Rate", f"{round(with_anom/total_analyzed*100)}%" if total_analyzed else "—")
    st.markdown("")
    type_counts,sev_counts = {},{}
    for inc in anomaly_data.get("incidents",[]):
        for f in inc.get("anomaly_flags",[]):
            t=f.get("anomaly_type","unknown").replace("_"," ").title(); s=f.get("severity","low").title()
            type_counts[t]=type_counts.get(t,0)+1; sev_counts[s]=sev_counts.get(s,0)+1
    if type_counts:
        ac1,ac2 = st.columns(2)
        with ac1:
            fig=go.Figure(go.Bar(x=list(type_counts.keys()),y=list(type_counts.values()),
                                  marker=dict(color=["#ef4444","#f59e0b","#10b981","#ec4899"][:len(type_counts)],line=dict(color="#000000",width=1),opacity=0.82),
                                  text=list(type_counts.values()),textposition="outside",textfont=dict(color="#64748b",size=11)))
            fig.update_layout(**pl("Anomalies by Type", 280, xaxis=dict(gridcolor="rgba(0,0,0,0)",tickfont=dict(color="#94a3b8",size=10)), yaxis=dict(gridcolor="rgba(239,68,68,0.08)",tickfont=dict(color="#64748b",size=10))))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        with ac2:
            scm={"High":"#ef4444","Medium":"#eab308","Low":"#22c55e"}
            fig=go.Figure(go.Pie(labels=list(sev_counts.keys()),values=list(sev_counts.values()),hole=0.58,
                                  marker=dict(colors=[scm.get(s,"#ef4444") for s in sev_counts],line=dict(color="#000000",width=2)),textfont=dict(color="#e2e8f0")))
            fig.update_layout(**pl("Anomalies by Severity",280))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    st.markdown("---")
    section_header("Incident Anomaly Detail", len(anomaly_data.get("incidents",[])))
    for inc in anomaly_data.get("incidents",[]):
        oid=inc.get("outage_id",""); region=inc.get("region",""); primary=inc.get("primary_concern",""); flags=inc.get("anomaly_flags",[]); n_high=inc.get("high_severity_count",0)
        with st.expander(f"️  {oid}  —  {region}  ·  {' HIGH SEVERITY' if n_high else f' {len(flags)} flag(s)'}"):
            if primary:
                st.markdown(f'<div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.22);border-radius:10px;padding:12px 16px;margin-bottom:14px;"><div style="font-size:0.67rem;font-weight:800;color:#ef4444;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:5px;">PRIMARY CONCERN</div><div style="font-size:0.82rem;color:#fca5a5;">{primary}</div></div>',unsafe_allow_html=True)
            for f in flags:
                sev=f.get("severity","low"); cls=sev.lower(); atype=f.get("anomaly_type","").replace("_"," ").title()
                actual=f.get("actual_value",0); thresh=f.get("threshold_value",0); dev=f.get("deviation_percent",0)
                st.markdown(f'<div class="flag-card {cls}"><div class="flag-sev {cls}">{sev.upper()} · {atype}</div><div class="flag-desc">{f.get("description","")}</div><div style="font-size:0.71rem;color:#334155;margin-bottom:4px;">Actual: <b style="color:#e2e8f0;">{actual:.1f}</b> | Threshold: <b style="color:#e2e8f0;">{thresh:.1f}</b> | Deviation: <b>{dev:.1f}%</b></div><div class="flag-rec"> {f.get("recommendation","")}</div></div>',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# DATA EXPLORER
# ══════════════════════════════════════════════════════════
def render_data_explorer(usage_df: pd.DataFrame, complaints_df: pd.DataFrame):
    section_header("Data Explorer", f"{len(usage_df):,} usage · {len(complaints_df):,} complaints")
    if usage_df.empty:
        st.info("Usage metrics CSV not found.")
        return
    tab1, tab2 = st.tabs([" Usage Metrics (101K)", "💬 Complaint Logs"])
    with tab1:
        cx1,cx2,cx3 = st.columns(3)
        regions = ["All"] + sorted(usage_df["region"].unique())
        sel_reg = cx1.selectbox("Region", regions, key="de_reg")
        metric  = cx2.selectbox("Metric", ["traffic_gbps","active_users","peak_utilization_percent"], key="de_met")
        agg     = cx3.selectbox("Aggregation", ["Hourly Avg","Daily Avg","Raw (sampled)"], key="de_agg")
        work = usage_df if sel_reg=="All" else usage_df[usage_df["region"]==sel_reg]
        if agg=="Raw (sampled)":
            plot_df = work.sample(min(2000,len(work))).sort_values("timestamp")
            fig=px.scatter(plot_df,x="timestamp",y=metric,color="region",color_discrete_sequence=REGION_PALETTE,labels={metric:metric.replace("_"," ").title()},opacity=0.5)
        elif agg=="Hourly Avg":
            plot_df = work.groupby(["region",work["timestamp"].dt.floor("h")])[metric].mean().reset_index()
            plot_df.columns=["region","timestamp",metric]
            fig=px.line(plot_df,x="timestamp",y=metric,color="region",color_discrete_sequence=REGION_PALETTE,labels={metric:metric.replace("_"," ").title()})
        else:
            plot_df = work.groupby(["region","date"])[metric].mean().reset_index()
            fig=px.line(plot_df,x="date",y=metric,color="region",color_discrete_sequence=REGION_PALETTE,markers=True,labels={metric:metric.replace("_"," ").title()})
        fig.update_layout(**pl(f"{metric.replace('_',' ').title()} — {agg}",380))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown("**Dataset Summary**")
        st.dataframe(work.groupby("region")[["traffic_gbps","active_users","peak_utilization_percent"]].describe().round(1),use_container_width=True)
    with tab2:
        if complaints_df.empty:
            st.info("No complaint log data found.")
            return
        cc1,cc2 = st.columns(2)
        with cc1:
            if "complaint_type" in complaints_df.columns:
                ct=complaints_df["complaint_type"].value_counts()
                fig=go.Figure(go.Pie(labels=ct.index.tolist(),values=ct.values.tolist(),hole=0.55,marker=dict(colors=REGION_PALETTE[:len(ct)],line=dict(color="#000000",width=2)),textfont=dict(color="#e2e8f0")))
                fig.update_layout(**pl("Complaints by Type",280))
                st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        with cc2:
            if "escalation_level" in complaints_df.columns:
                el=complaints_df["escalation_level"].value_counts().reset_index(); el.columns=["Level","Count"]
                elc={"Critical":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#22c55e"}
                fig=go.Figure(go.Bar(x=el["Level"],y=el["Count"],marker=dict(color=[elc.get(l,"#ef4444") for l in el["Level"]],line=dict(color="#000000",width=1),opacity=0.85),
                                      text=el["Count"],textposition="outside",textfont=dict(color="#64748b",size=11)))
                fig.update_layout(**pl("Complaints by Escalation Level", 280, xaxis=dict(gridcolor="rgba(0,0,0,0)",tickfont=dict(color="#94a3b8",size=11)), yaxis=dict(gridcolor="rgba(239,68,68,0.08)",tickfont=dict(color="#64748b",size=10))))
                st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        if "customer_count" in complaints_df.columns and "region" in complaints_df.columns:
            rcust=complaints_df.groupby("region")["customer_count"].sum().reset_index().sort_values("customer_count")
            fig=go.Figure(go.Bar(x=rcust["customer_count"],y=rcust["region"],orientation="h",marker=dict(color="#dc2626",opacity=0.75,line=dict(color="#000000",width=1)),text=[f"{int(v):,}" for v in rcust["customer_count"]],textposition="outside",textfont=dict(color="#64748b",size=11)))
            fig.update_layout(**pl("Total Affected Customers by Region", 280, xaxis=dict(gridcolor="rgba(239,68,68,0.08)",tickfont=dict(color="#64748b",size=10)), yaxis=dict(gridcolor="rgba(0,0,0,0)",tickfont=dict(color="#94a3b8",size=11))))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown("**Complaint Logs Preview**")
        st.dataframe(complaints_df.head(50),use_container_width=True,hide_index=True)





# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
def render_sidebar(df_all: pd.DataFrame, usage_df: pd.DataFrame):
    with st.sidebar:
        st.markdown("""
        <div class="sb-logo">
            <div class="sb-logo-icon"></div>
            <div class="sb-logo-name">NOC Intelligence</div>
            <div class="sb-logo-tag">Outage Prioritization Platform</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section">Navigation</div>', unsafe_allow_html=True)

        view = st.radio("Navigation", [
            "Dashboard",
            "Geographic Map",
            "Regional Analysis",
            "️Anomaly Intelligence",
            "Data Explorer",
        ], label_visibility="collapsed")

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section">Filters</div>', unsafe_allow_html=True)

        regions = ["All Regions"] + (sorted(df_all["region"].unique().tolist()) if not df_all.empty else [])
        sel_region = st.selectbox("Region", regions, key="sb_region")

        sel_sev = st.selectbox("Severity", ["All Severities"] + SEVERITY_ORDER, key="sb_sev")

        score_range = st.slider("Impact Score", 0, 100, (0, 100), step=5, key="sb_score")

        # ── Time window filter (PRD requirement) ──
        st.markdown('<div class="sb-section">Time Window</div>', unsafe_allow_html=True)

        # Determine date range from data
        if not usage_df.empty:
            data_min = usage_df["timestamp"].min().date()
            data_max = usage_df["timestamp"].max().date()
        else:
            data_min = date(2026, 7, 10)
            data_max = date(2026, 7, 31)

        date_from = st.date_input("From", value=data_min, min_value=data_min, max_value=data_max, key="sb_date_from")
        date_to   = st.date_input("To",   value=data_max, min_value=data_min, max_value=data_max, key="sb_date_to")
        date_range = (date_from, date_to) if date_from <= date_to else (data_min, data_max)

        st.markdown('<div class="sb-section">Search</div>', unsafe_allow_html=True)
        search = st.text_input("Search", placeholder="ID, region, component…", key="sb_search", label_visibility="collapsed")

        if "Dashboard" in view or "Geographic" in view:
            st.markdown('<div class="sb-section">Sort Incidents By</div>', unsafe_allow_html=True)
            sort_by = st.selectbox("Sort By", ["Impact Score ↓","Impact Score ↑","Complaints ↓","Duration ↓","Customers ↓"],
                                   label_visibility="collapsed", key="sb_sort")
        else:
            sort_by = "Impact Score ↓"

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section">Data Refresh</div>', unsafe_allow_html=True)
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False, key="sb_auto")
        if st.button("Refresh Now", use_container_width=True):
            clear_all_cache()
            st.rerun()

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sb-info">
            Backend: <code style="color:#ef4444">{API_BASE}</code><br>
            Data: <code style="color:#ef4444">{DATA_DIR}/</code><br>
            Map: <code style="color:#ef4444">OpenStreetMap</code><br>
            Version 0.8.0 · MVP Complete
        </div>
        """, unsafe_allow_html=True)

    return view, sel_region, sel_sev, score_range, date_range, search, sort_by, auto_refresh


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
def main():
    inject_css()

    with st.spinner("Loading intelligence data…"):
        incidents_data = fetch_ranked_incidents()
        anomaly_data   = fetch_anomalies()
        usage_df       = load_usage_timeseries()
        complaints_df  = load_complaint_logs()

    backend_ok  = incidents_data.get("status") != "error"
    df_all      = incidents_to_df(incidents_data.get("incidents", []))
    anomaly_map = build_anomaly_map(anomaly_data)

    view, sel_region, sel_sev, score_range, date_range, search, sort_by, auto_refresh = render_sidebar(df_all, usage_df)

    df = apply_filters(df_all.copy(), sel_region, sel_sev, score_range, date_range)

    render_header(backend_ok, len(df_all), datetime.now().strftime("%H:%M:%S"))

    if not backend_ok:
        st.error(f"️ **Backend Unavailable** — `{API_BASE}` is not responding. Error: `{incidents_data.get('message','Connection refused')}`")

    render_kpi_cards(df, anomaly_data.get("total_anomalies", 0), usage_df)

    # Filter status bar + CSV export
    if not df_all.empty:
        fil_col, exp_col = st.columns([5, 1])
        active_filters = []
        if sel_region != "All Regions":    active_filters.append(f"Region: `{sel_region}`")
        if sel_sev != "All Severities":    active_filters.append(f"Severity: `{sel_sev}`")
        if score_range != (0, 100):        active_filters.append(f"Score: `{score_range[0]}–{score_range[1]}`")
        if search:                         active_filters.append(f"Search: `{search}`")
        filter_str = "  ·  ".join(active_filters) if active_filters else "No filters active"
        fil_col.markdown(f"<div style='color:#334155;font-size:0.78rem;padding:8px 0;'>Showing <b style='color:#94a3b8'>{len(df)}</b> of <b style='color:#94a3b8'>{len(df_all)}</b> incidents  ·  {filter_str}  ·   {date_range[0]} → {date_range[1]}</div>", unsafe_allow_html=True)
        if not df.empty:
            cols = ["rank","outage_id","region","severity","overall_score","duration_minutes","complaint_count","affected_customers","avg_traffic_gbps","component","status"]
            avail = [c for c in cols if c in df.columns]
            buf = io.BytesIO()
            df[avail].to_csv(buf, index=False)
            exp_col.download_button(" Export", data=buf.getvalue(),
                                    file_name=f"noc_incidents_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                    mime="text/csv", use_container_width=True)

    st.markdown("---")

    if "Dashboard" in view:
        if not df.empty:
            render_overview_charts(df, usage_df)
        st.markdown("---")
        render_incident_table(df, anomaly_map, search, sort_by)

    elif "Geographic" in view:
        render_geographic_map(df, usage_df, sort_by)

    elif "Regional" in view:
        render_regional_analysis(df_all, usage_df)

    elif "Anomaly" in view:
        render_anomaly_intelligence(anomaly_data)

    elif "Explorer" in view:
        render_data_explorer(usage_df, complaints_df)


    if auto_refresh:
        time.sleep(REFRESH_SECS)
        clear_all_cache()
        st.rerun()


if __name__ == "__main__":
    main()
