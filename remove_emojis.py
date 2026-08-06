import re
import io

def remove_emojis(text):
    # Regex for matching most emojis
    emoji_pattern = re.compile(
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])|"  # flags (iOS)
        u"[\u2600-\u26FF\u2700-\u27BF]|" # misc symbols and dingbats
        u"(\U0001f300-\U0001f5ff)|"  # symbols & pictographs
        u"(\U0001f600-\U0001f64f)|"  # emoticons
        u"(\U0001f680-\U0001f6ff)|"  # transport & map symbols
        u"(\U0001f700-\U0001f77f)|"  # alchemical symbols
        u"(\U0001f780-\U0001f7ff)|"  # Geometric Shapes Extended
        u"(\U0001f800-\U0001f8ff)|"  # Supplemental Arrows-C
        u"(\U0001f900-\U0001f9ff)|"  # Supplemental Symbols and Pictographs
        u"(\U0001fa00-\U0001fa6f)|"  # Chess Symbols
        u"(\U0001fa70-\U0001faff)|"  # Symbols and Pictographs Extended-A
        u"[\u2B50\u231A\u23F0\u23F3\u2328\u2693\u26F9\u26A1\u26D4\u2620\u2622\u2623\u26CE\u26A0\u2B05\u2B06\u2B07\u2B08\u2705\u274C\u274E\u2753\u2754\u2755\u2757\u2714\u2716\u2795\u2796\u2797\u27B0\u27BF]"
        "+", flags=re.UNICODE)
    
    # Also explicitly define the ones we know
    known_emojis = ["📊", "🗺️", "📍", "⚠️", "🔬", "📋", "🔄", "⬇", "📅", "💡", "🔴", "⚠", "🛰️", "📖", "✨", "🏗️", "🚀", "📡", "🧪", "🔒", "🎨", "🖤", "🗺", "📄", "✅"]
    
    # First regex
    text = emoji_pattern.sub(r'', text)
    
    # Then explicitly
    for e in known_emojis:
        text = text.replace(e, "")
    
    # Clean up double spaces left behind
    text = text.replace("  Dashboard", "Dashboard")
    text = text.replace("  Geographic Map", "Geographic Map")
    text = text.replace("  Regional Analysis", "Regional Analysis")
    text = text.replace("  Anomaly Intelligence", "Anomaly Intelligence")
    text = text.replace("  Data Explorer", "Data Explorer")
    text = text.replace("  Refresh Now", "Refresh Now")
    text = text.replace("  PRD Status", "PRD Status")
    
    return text

for file_path in ["dashboard/app.py", "README.md"]:
    with io.open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = remove_emojis(content)
    
    with io.open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

