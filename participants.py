import streamlit as st
import mysql.connector
from mysql.connector import Error
from streamlit.components.v1 import html

# ───────────────────────────────────────────────────────────────
# Database helper (reads credentials from [mysql] in secrets)
# ───────────────────────────────────────────────────────────────

def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )

# ───────────────────────────────────────────────────────────────
# Progress constants
# ───────────────────────────────────────────────────────────────

_REQUIRED_TABS = {1: 10, 2: 12, 3: 12, 4: 7, 5: 0}  # week → tab‑count
_TOTAL_REQUIRED = sum(_REQUIRED_TABS.values()) or 1  # avoid div/0 when week5=0

# colours for week bars (terminal‑green gradient look)
_WEEK_COLORS = {
    1: "#27c93f",
    2: "#0ff",
    3: "#b19cd9",
    4: "#ffbd2e",
    5: "#f44",
}

# ───────────────────────────────────────────────────────────────
# Fetch participants & progress
# ───────────────────────────────────────────────────────────────

def _fetch_participants():
    """Return list of dicts with full progress info sorted by overall pct."""
    query = (
        "SELECT fullname, username, week1track, week2track, week3track, "
        "       week4track, week5track "
        "FROM progress"
    )
    rows = []
    try:
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute(query)
            for (fullname, username, w1, w2, w3, w4, w5) in cur.fetchall():
                weeks = {1: w1 or 0, 2: w2 or 0, 3: w3 or 0, 4: w4 or 0, 5: w5 or 0}
                prog_sum = sum(weeks.values())
                percent = min(100, round(prog_sum / _TOTAL_REQUIRED * 100))
                rows.append({
                    "fullname": fullname or username,
                    "username": username,
                    "percent": percent,
                    "weeks": weeks,
                })
    except Error as e:
        st.error(f"Database error: {getattr(e, 'msg', e)}")
    return sorted(rows, key=lambda r: (-r["percent"], r["fullname"]))

# ───────────────────────────────────────────────────────────────
# Build HTML
# ───────────────────────────────────────────────────────────────

_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Participants Progress Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;700&display=swap');
        
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --accent-green: #00ff41;
            --accent-cyan: #00d4ff;
            --accent-purple: #b19cd9;
            --accent-yellow: #ffcc02;
            --accent-red: #ff4757;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --border-color: #30363d;
            --glow-green: rgba(0, 255, 65, 0.5);
            --glow-cyan: rgba(0, 212, 255, 0.4);
            --shadow-main: 0 0 30px rgba(0, 255, 65, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0a0e13 0%, #0d1117 50%, #161b22 100%);
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            color: var(--text-primary);
        }

        .terminal {
            width: 95%;
            max-width: 1000px;
            background: var(--bg-primary);
            border: 2px solid var(--accent-green);
            border-radius: 12px;
            box-shadow: var(--shadow-main), inset 0 0 20px rgba(0, 255, 65, 0.1);
            padding: 30px;
            overflow: auto;
            position: relative;
        }

        .terminal::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan), var(--accent-purple), var(--accent-yellow));
            border-radius: 12px 12px 0 0;
        }

        .header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }

        .title {
            color: var(--accent-cyan);
            font-size: 1.8rem;
            font-weight: 700;
            text-shadow: 0 0 10px var(--glow-cyan);
            margin-right: 20px;
        }

        .stats {
            margin-left: auto;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .participant {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin: 12px 0;
            padding: 18px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .participant:hover {
            border-color: var(--accent-green);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
            transform: translateY(-2px);
        }

        .participant-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
        }

        .participant-name {
            font-size: 1.1rem;
            font-weight: 600;
            background: linear-gradient(45deg, var(--accent-green), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
        }

        .completion-badge {
            display: flex;
            align-items: center;
            background: var(--bg-tertiary);
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid var(--border-color);
        }

        .percentage {
            font-weight: 700;
            margin-right: 10px;
            color: var(--accent-green);
        }

        .overall-bar {
            width: 100px;
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }

        .overall-progress {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
            border-radius: 4px;
            transition: width 0.8s ease;
            box-shadow: 0 0 8px var(--glow-green);
        }

        .weeks-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }

        .week-item {
            display: flex;
            align-items: center;
            background: var(--bg-tertiary);
            padding: 8px 12px;
            border-radius: 6px;
            border-left: 3px solid;
            transition: all 0.2s ease;
        }

        .week-item:hover {
            transform: scale(1.02);
        }

        .week-label {
            font-weight: 500;
            margin-right: 8px;
            min-width: 45px;
        }

        .week-progress {
            flex: 1;
            height: 6px;
            background: var(--bg-primary);
            border-radius: 3px;
            overflow: hidden;
            margin-right: 8px;
        }

        .week-bar {
            height: 100%;
            border-radius: 3px;
            transition: width 0.6s ease;
        }

        .week-count {
            font-size: 0.8rem;
            color: var(--text-secondary);
            min-width: 35px;
            text-align: right;
        }

        .rank-indicator {
            position: absolute;
            top: 10px;
            right: 15px;
            background: var(--accent-green);
            color: var(--bg-primary);
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .no-data {
            text-align: center;
            color: var(--text-secondary);
            font-style: italic;
            margin: 40px 0;
        }

        @keyframes glow-pulse {
            0%, 100% { box-shadow: 0 0 15px rgba(0, 255, 65, 0.3); }
            50% { box-shadow: 0 0 25px rgba(0, 255, 65, 0.5); }
        }

        .terminal {
            animation: glow-pulse 4s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="header">
            <h2 class="title">⚡ Progress Dashboard</h2>
            <div class="stats">{{STATS}}</div>
        </div>
        {{ROWS}}
    </div>
</body>
</html>"""


def _week_bar(week_num, done):
    req = _REQUIRED_TABS.get(week_num, 1) or 1
    pct = min(100, round(done / req * 100))
    width_pct = max(5, pct)  # ensure visible bar
    color = _WEEK_COLORS.get(week_num, "#00d4ff")
    
    return f'''
    <div class="week-item" style="border-left-color: {color};">
        <span class="week-label" style="color: {color};">W{week_num}</span>
        <div class="week-progress">
            <div class="week-bar" style="background: {color}; width: {width_pct}%;"></div>
        </div>
        <span class="week-count">{done}/{req}</span>
    </div>'''


def _build_rows(parts):
    if not parts:
        return '<div class="no-data">No participants found.</div>'
    
    total_participants = len(parts)
    avg_completion = sum(p["percent"] for p in parts) / total_participants if parts else 0
    stats = f"👥 {total_participants} participants | 📊 {avg_completion:.1f}% avg completion"
    
    rows_html = []
    for idx, p in enumerate(parts, 1):
        overall_width = max(5, p["percent"])
        
        # Create week items
        weeks_html = "".join(
            _week_bar(w, count) 
            for w, count in p["weeks"].items() 
            if _REQUIRED_TABS[w] > 0
        )
        
        participant_html = f'''
        <div class="participant">
            <div class="rank-indicator">#{idx}</div>
            <div class="participant-header">
                <div class="participant-name">{p["fullname"]}</div>
                <div class="completion-badge">
                    <span class="percentage">{p["percent"]}%</span>
                    <div class="overall-bar">
                        <div class="overall-progress" style="width: {overall_width}%;"></div>
                    </div>
                </div>
            </div>
            <div class="weeks-container">
                {weeks_html}
            </div>
        </div>'''
        
        rows_html.append(participant_html)
    
    return _HTML_TEMPLATE.replace("{{STATS}}", stats).replace("{{ROWS}}", "\n".join(rows_html))

# ───────────────────────────────────────────────────────────────
# Streamlit entrypoint
# ───────────────────────────────────────────────────────────────

def show():
    st.set_page_config(page_title="Participants", layout="wide")
    parts = _fetch_participants()
    html_content = _build_rows(parts)
    # Height adjusts dynamically, cap at 900px
    box_h = min(900, 300 + len(parts) * 60)
    html(html_content, height=box_h, scrolling=True)
