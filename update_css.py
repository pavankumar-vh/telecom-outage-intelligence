import re

with open("dashboard/app.py", "r") as f:
    content = f.read()

# Replace Map Style
content = content.replace('MAP_STYLE = "open-street-map"', 'MAP_STYLE = "carto-darkmatter"')

# Replace CSS block
new_css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif !important; }

.stApp {
    background: #000000 !important;
    color:#e2e8f0 !important;
}

[data-testid="stSidebar"] {
    background: #09090b !important;
    border-right:1px solid rgba(239,68,68,0.18) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.8) !important;
}
[data-testid="stSidebar"] * { color:#cbd5e1 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stDateInput label { color:#94a3b8 !important; font-size:0.7rem !important; letter-spacing:0.08em !important; text-transform:uppercase !important; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#09090b; }
::-webkit-scrollbar-thumb { background:linear-gradient(180deg,#ef4444,#dc2626); border-radius:99px; }

/* Header */
.noc-header {
    background: linear-gradient(135deg,rgba(239,68,68,0.12) 0%,rgba(220,38,38,0.08) 50%,rgba(185,28,28,0.12) 100%);
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
    background:linear-gradient(135deg,#fca5a5 0%,#ef4444 40%,#b91c1c 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin:0; padding:0;
}
.noc-header-sub { color:#64748b; font-size:0.8rem; letter-spacing:0.12em; text-transform:uppercase; margin-top:6px; }
.noc-header-meta { display:flex; gap:24px; margin-top:14px; }
.noc-meta-item { display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#64748b; }
.noc-meta-dot { width:6px; height:6px; border-radius:99px; }
.noc-meta-dot.green  { background:#22c55e; box-shadow:0 0 6px #22c55e; }
.noc-meta-dot.yellow { background:#eab308; box-shadow:0 0 6px #eab308; }

/* KPI Cards */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; }
.kpi-card {
    background:#09090b; border-radius:16px; padding:24px;
    border:1px solid rgba(255,255,255,0.05); 
    position:relative; overflow:hidden;
    transition:transform 0.2s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.kpi-card:hover { transform:translateY(-3px); border-color:rgba(239,68,68,0.4); box-shadow:0 8px 32px rgba(239,68,68,0.12); }
.kpi-card::before { content:''; position:absolute; top:0;left:0;right:0;height:2px;border-radius:16px 16px 0 0; }
.kpi-card.indigo::before { background:linear-gradient(90deg,#ef4444,#dc2626); }
.kpi-card.red::before    { background:linear-gradient(90deg,#ef4444,#f97316); }
.kpi-card.purple::before { background:linear-gradient(90deg,#ef4444,#ec4899); }
.kpi-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#eab308); }
.kpi-glow { position:absolute; top:-20px; right:-20px; width:100px; height:100px; border-radius:50%; opacity:0.04; pointer-events:none; }
.kpi-card.indigo .kpi-glow { background:#ef4444; }
.kpi-card.red    .kpi-glow { background:#ef4444; }
.kpi-card.purple .kpi-glow { background:#ef4444; }
.kpi-card.amber  .kpi-glow { background:#f59e0b; }
.kpi-label { font-size:0.68rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#64748b; margin-bottom:12px; }
.kpi-value { font-size:2.6rem; font-weight:900; color:#f8fafc; line-height:1; letter-spacing:-0.02em; }
.kpi-sub   { font-size:0.72rem; color:#475569; margin-top:8px; }
.kpi-icon  { position:absolute; bottom:18px; right:20px; font-size:1.8rem; opacity:0.08; color:#ef4444; }

/* Section headers */
.section-header { display:flex; align-items:center; gap:12px; margin:28px 0 18px; }
.section-header-bar { width:3px; height:24px; border-radius:99px; background:linear-gradient(180deg,#ef4444,#b91c1c); }
.section-header-title { font-size:0.85rem; font-weight:700; color:#94a3b8; letter-spacing:0.1em; text-transform:uppercase; }
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
.sbar-fill.c1 { background:linear-gradient(90deg,#ef4444,#dc2626); }
.sbar-fill.c2 { background:linear-gradient(90deg,#dc2626,#eab308); }
.sbar-fill.c3 { background:linear-gradient(90deg,#eab308,#84cc16); }
.sbar-fill.c4 { background:linear-gradient(90deg,#22c55e,#10b981); }
.sbar-val { font-size:0.82rem; font-weight:700; color:#f8fafc; min-width:38px; text-align:right; font-family:'JetBrains Mono',monospace; }

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
.stat-pair { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05); }
.stat-pair:last-child { border-bottom:none; }
.stat-key { font-size:0.77rem; color:#64748b; }
.stat-val { font-size:0.77rem; font-weight:600; color:#f8fafc; font-family:'JetBrains Mono',monospace; }

/* Map container */
.map-container {
    background:#09090b; border:1px solid rgba(255,255,255,0.1);
    border-radius:16px; overflow:hidden;
}
.map-legend-item { display:flex; align-items:center; gap:8px; font-size:0.75rem; color:#94a3b8; }
.map-legend-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }

/* Nav radio */
div[data-testid="stRadio"] > div { display:flex; flex-direction:column; gap:4px; }
div[data-testid="stRadio"] label {
    background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05);
    border-radius:10px; padding:10px 14px !important; cursor:pointer;
    font-size:0.82rem !important; font-weight:500 !important; transition:all 0.18s ease;
}
div[data-testid="stRadio"] label:hover { border-color:rgba(239,68,68,0.35); background:rgba(239,68,68,0.08); }

/* Expander */
details summary {
    background:#09090b !important; border:1px solid rgba(255,255,255,0.1) !important;
    border-radius:12px !important; padding:14px 18px !important; color:#94a3b8 !important;
    font-size:0.85rem !important; transition:border-color 0.2s ease, background 0.2s ease;
}
details summary:hover { border-color:rgba(239,68,68,0.35) !important; background:rgba(239,68,68,0.06) !important; }
details[open] summary { border-radius:12px 12px 0 0 !important; border-bottom-color:transparent !important; background:rgba(239,68,68,0.1) !important; }
details[open] > div:last-child { background:#09090b !important; border:1px solid rgba(255,255,255,0.1) !important; border-top:none !important; border-radius:0 0 12px 12px !important; padding:16px 18px !important; }

/* Inputs */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,
.stDateInput input {
    background:#09090b !important; border:1px solid rgba(255,255,255,0.1) !important;
    border-radius:10px !important; color:#f8fafc !important; font-family:'Inter',sans-serif !important;
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
.stDataFrame { border-radius:14px !important; overflow:hidden !important; border:1px solid rgba(255,255,255,0.1) !important; }

/* Metrics */
[data-testid="metric-container"] {
    background:#09090b !important; border:1px solid rgba(255,255,255,0.05) !important;
    border-radius:12px !important; padding:16px 20px !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] { color:#64748b !important; font-size:0.72rem !important; text-transform:uppercase !important; letter-spacing:0.08em !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color:#f8fafc !important; font-weight:800 !important; }

hr { border:none !important; height:1px !important; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent) !important; margin:24px 0 !important; }
"""

# Now replace the CSS block using regex
content = re.sub(r'<style>.*?/* Sidebar branding */', new_css + '\n/* Sidebar branding */', content, flags=re.DOTALL)

with open("dashboard/app.py", "w") as f:
    f.write(content)

