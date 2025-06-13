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
<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Participants</title><style>@import url('https://fonts.googleapis.com/css2?family=Inconsolata:wght@400;700&display=swap');:root{--bg:#0a0a12;--green:#0f0;--cyan:#0ff;--glow:rgba(0,255,0,.7);--text-shadow:0 0 8px var(--glow);}*{margin:0;padding:0;box-sizing:border-box;}body{background:#000;font-family:'Inconsolata',monospace;display:flex;justify-content:center;align-items:center;min-height:100vh;} .terminal{width:90%;max-width:850px;height:80vh;background:var(--bg);border:1px solid var(--green);border-radius:8px;box-shadow:0 0 25px rgba(0,255,0,.5),inset 0 0 10px rgba(0,255,0,.2);padding:20px;overflow:auto;color:#e0e0e0;text-shadow:var(--text-shadow);} .title{color:var(--cyan);margin-bottom:15px;} .participant{margin:8px 0;} .bar{display:inline-block;height:14px;min-width:30px;background:linear-gradient(to right,var(--green),var(--cyan));box-shadow:0 0 5px var(--glow);} .weeks{margin-left:25px;font-size:0.8rem;line-height:1.4;} .wbar{display:inline-block;height:10px;margin-left:4px;vertical-align:middle;box-shadow:0 0 3px var(--glow);} </style></head><body><div class=\"terminal\"><h3 class=\"title\">Participants Progress</h3>{{ROWS}}</div></body></html>"""


def _week_bar(week_num, done):
    req = _REQUIRED_TABS.get(week_num, 1) or 1
    pct = min(100, round(done / req * 100))
    width = max(5, pct)  # ensure visible bar
    color = _WEEK_COLORS.get(week_num, "#0ff")
    return (
        f'<span style="color:{color};">W{week_num}:{done}/{req}</span>'
        f'<span class="wbar" style="background:{color};width:{width}px;"></span>'
    )


def _build_rows(parts):
    if not parts:
        return "<p>No participants found.</p>"
    out = []
    for p in parts:
        bar_w = max(5, p["percent"])  # overall bar width in %
        header = (
            f'<div class="participant"><span style="color:var(--green);">{p["fullname"]}</span>'
            f' — {p["percent"]}% <span class="bar" style="width:{bar_w}%;"></span></div>'
        )
        weeks_html = " ".join(_week_bar(w, c) for w, c in p["weeks"].items() if _REQUIRED_TABS[w])
        out.append(header + f'<div class="weeks">{weeks_html}</div>')
    return "\n".join(out)

# ───────────────────────────────────────────────────────────────
# Streamlit entrypoint
# ───────────────────────────────────────────────────────────────

def show():
    st.set_page_config(page_title="Participants", layout="wide")
    parts = _fetch_participants()
    html_content = _HTML_TEMPLATE.replace("{{ROWS}}", _build_rows(parts))
    # Height adjusts dynamically, cap at 900px
    box_h = min(900, 220 + len(parts) * 40)
    html(html_content, height=box_h, scrolling=True)

if __name__ == "__main__":
    show()
