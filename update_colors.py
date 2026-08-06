with open("dashboard/app.py", "r") as f:
    content = f.read()

# Replace all old colors with new colors globally
replacements = {
    # Backgrounds
    "#060b18": "#000000",
    "#080d1a": "#09090b",
    "#0a0f1e": "#09090b",
    "rgba(10,15,30,": "rgba(9,9,11,",
    
    # Primary Accent (Indigo -> Red)
    "#6366f1": "#ef4444",
    "#818cf8": "#fca5a5",
    "#a5b4fc": "#fca5a5",
    "rgba(99,102,241,": "rgba(239,68,68,",
    
    # Secondary Accent (Purple -> Dark Red)
    "#8b5cf6": "#dc2626",
    "#a855f7": "#dc2626",
    "#c084fc": "#ef4444",
    "rgba(168,85,247,": "rgba(220,38,38,",
    "rgba(139,92,246,": "rgba(220,38,38,",
    
    # Map Style
    'MAP_STYLE = "open-street-map"': 'MAP_STYLE = "carto-darkmatter"',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open("dashboard/app.py", "w") as f:
    f.write(content)

