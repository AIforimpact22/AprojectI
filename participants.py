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
# Fetch participants & progress (percentage of total weekly tabs)
# ───────────────────────────────────────────────────────────────

_REQUIRED_TABS = {1: 10, 2: 12, 3: 12, 4: 7, 5: 0}  # week → tab‑count
_TOTAL_REQUIRED = sum(_REQUIRED_TABS.values()) or 1  # avoid div/0


def _fetch_participants():
    """Return list of dicts: [{fullname, username, percent}, …] sorted desc."""
    query = (
        "SELECT fullname, username, week1track, week2track, week3track, "
        "       week4track, week5track "
        "FROM progress ORDER BY fullname"
    )
    rows = []
    try:
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute(query)
            for (fullname, username, w1, w2, w3, w4, w5) in cur.fetchall():
                prog_sum = (w1 or 0) + (w2 or 0) + (w3 or 0) + (w4 or 0) + (w5 or 0)
                percent = min(100, round(prog_sum / _TOTAL_REQUIRED * 100))
                rows.append({"fullname": fullname or username, "username": username, "percent": percent})
    except Error as e:
        st.error(f"Database error: {e.msg if hasattr(e,'msg') else e}")
    return sorted(rows, key=lambda r: (-r["percent"], r["fullname"]))

# ───────────────────────────────────────────────────────────────
# Build dynamic HTML (cyber‑terminal aesthetic)
# ───────────────────────────────────────────────────────────────

_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>Participants Terminal</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inconsolata:wght@400;700&display=swap');
:root{--terminal-bg:#0a0a12;--terminal-green:#0f0;--terminal-cyan:#0ff;--terminal-glow:rgba(0,255,0,.7);--text-shadow:0 0 8px var(--terminal-glow);}
*{margin:0;padding:0;box-sizing:border-box;}body{background:#000;overflow:hidden;font-family:'Inconsolata',monospace;display:flex;justify-content:center;align-items:center;min-height:100vh;perspective:1000px;}
.terminal{width:90%;max-width:800px;height:75vh;border:1px solid var(--terminal-green);border-radius:8px;background:var(--terminal-bg);box-shadow:0 0 30px rgba(0,255,0,.5),inset 0 0 10px rgba(0,255,0,.2);padding:20px;overflow:auto;color:#e0e0e0;text-shadow:var(--text-shadow);}
.participant{margin:6px 0;}
.bar{display:inline-block;height:14px;min-width:30px;background:linear-gradient(to right,var(--terminal-green),var(--terminal-cyan));box-shadow:0 0 5px var(--terminal-glow);}
</style>
</head><body>
<div class=\"terminal\">
<h3 style=\"color:var(--terminal-cyan);margin-bottom:10px;\">Participants Progress</h3>
{{ROWS}}
</div>
</body></html>
"""


def _build_rows(participants):
    lines = []
    for p in participants:
        bar_width = max(5, p["percent"])  # ensure visible bar
        line = (
            f'<div class="participant">'
            f'<span style="color:var(--terminal-green);">{p["fullname"]}</span>'
            f' — {p["percent"]}%'
            f' <span class="bar" style="width:{bar_width}%;"></span>'
            f'</div>'
        )
        lines.append(line)
    return "\n".join(lines) if lines else "<p>No participants found.</p>"


# ───────────────────────────────────────────────────────────────
# Streamlit page entrypoint
# ───────────────────────────────────────────────────────────────

def show():
    st.set_page_config(page_title="Participants", layout="wide")
    parts = _fetch_participants()
    html_content = _HTML_TEMPLATE.replace("{{ROWS}}", _build_rows(parts))
    # Height grows with participants but cap at 800px for usability
    box_height = min(800, 180 + len(parts) * 26)
    html(html_content, height=box_height, scrolling=True)


if __name__ == "__main__":
    show()
