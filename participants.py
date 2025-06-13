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
    query = (
        "SELECT fullname, username, week1track, week2track, week3track, "
        "       week4track, week5track FROM progress"
    )
    rows = []
    try:
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute(query)
            for (fullname, username, w1, w2, w3, w4, w5) in cur.fetchall():
                weeks = {1: w1 or 0, 2: w2 or 0, 3: w3 or 0, 4: w4 or 0, 5: w5 or 0}
                percent = min(100, round(sum(weeks.values()) / _TOTAL_REQUIRED * 100))
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

_HTML_TEMPLATE = """<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Participants</title><style>@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');:root{--bg1:#0d1117;--bg2:#161b22;--bg3:#21262d;--g:#00ff41;--c:#00d4ff;--p:#b19cd9;--y:#ffcc02;--r:#ff4757;--txt:#f0f6fc;--txt2:#8b949e;--border:#30363d;--glow:rgba(0,255,65,.4);}*{margin:0;padding:0;box-sizing:border-box;}body{background:#000;font-family:'JetBrains Mono',monospace;color:var(--txt);display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px;} .terminal{width:95%;max-width:1000px;background:var(--bg1);border:2px solid var(--g);border-radius:12px;box-shadow:0 0 25px var(--glow),inset 0 0 15px rgba(0,255,65,.1);padding:30px;overflow:auto;} .title{color:var(--c);font-size:1.8rem;margin-bottom:20px;} .participant{margin:12px 0;padding-bottom:18px;} .divider{border:none;border-bottom:1px solid var(--border);margin:12px 0;} .participant-name{font-weight:600;background:linear-gradient(45deg,var(--g),var(--c));-webkit-background-clip:text;-webkit-text-fill-color:transparent;} .percentage{color:var(--g);font-weight:700;margin-right:8px;} .overall-bar{width:100px;height:8px;background:var(--bg3);border-radius:4px;display:inline-block;vertical-align:middle;} .overall-progress{height:100%;background:linear-gradient(90deg,var(--g),var(--c));border-radius:4px;} .weeks{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:6px;margin-top:10px;font-size:.8rem;} .week-item{display:flex;align-items:center;background:var(--bg2);padding:4px 8px;border-radius:4px;border-left:3px solid;} .week-label{margin-right:6px;} .week-progress{flex:1;height:6px;background:var(--bg1);border-radius:3px;margin-right:6px;overflow:hidden;} .week-bar{height:100%;border-radius:3px;} .week-count{color:var(--txt2);} </style></head><body><div class='terminal'><h2 class='title'>⚡ Participants Progress</h2>{{ROWS}}</div></body></html>"""


def _week_html(num, done):
    req = _REQUIRED_TABS.get(num, 1) or 1
    pct = min(100, round(done / req * 100))
    color = _WEEK_COLORS.get(num, "#00d4ff")
    return (
        f"<div class='week-item' style='border-left-color:{color};'>"
        f"<span class='week-label' style='color:{color};'>W{num}</span>"
        f"<div class='week-progress'><div class='week-bar' style='background:{color};width:{pct}%;'></div></div>"
        f"<span class='week-count'>{done}/{req}</span></div>"
    )


def _build_rows(parts):
    if not parts:
        return "<p class='no-data'>No participants found.</p>"
    html_rows = []
    for p in parts:
        overall = max(5, p["percent"])
        weeks_html = "".join(_week_html(w, c) for w, c in p["weeks"].items() if _REQUIRED_TABS[w])
        participant_html = (
            f"<div class='participant'>"
            f"<span class='participant-name'>{p['fullname']} ({p['username']})</span> — "
            f"<span class='percentage'>{p['percent']}%</span>"
            f"<span class='overall-bar'><span class='overall-progress' style='width:{overall}%;'></span></span>"
            f"<div class='weeks'>{weeks_html}</div>"
            f"</div><hr class='divider'>"
        )
        html_rows.append(participant_html)
    return "\n".join(html_rows)

# ───────────────────────────────────────────────────────────────
# Streamlit entrypoint
# ───────────────────────────────────────────────────────────────

def show():
    st.set_page_config(page_title="Participants", layout="wide")
    data = _fetch_participants()
    content = _HTML_TEMPLATE.replace("{{ROWS}}", _build_rows(data))
    html(content, height=min(900, 300 + len(data) * 80), scrolling=True)

if __name__ == "__main__":
    show()
