import streamlit as st
import mysql.connector
from mysql.connector import Error
from streamlit.components.v1 import html

# ───────────────────────────────────────────────────────────────
# Database helper
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
# Progress constants   ← Week 5 now has 4 required tabs
# ───────────────────────────────────────────────────────────────
_REQUIRED_TABS = {1: 10, 2: 12, 3: 12, 4: 7, 5: 4}
_TOTAL_REQUIRED = sum(_REQUIRED_TABS.values()) or 1

_WEEK_COLORS = {1: "#27c93f", 2: "#0ff", 3: "#b19cd9", 4: "#ffbd2e", 5: "#f44"}

# ───────────────────────────────────────────────────────────────
# Fetch participants & progress
# ───────────────────────────────────────────────────────────────
def _fetch_participants():
    """Return list of dicts with progress info, sorted by completion%."""
    query = (
        "SELECT u.fullname, u.username, u.date_of_joining, "
        "       p.week1track, p.week2track, p.week3track, p.week4track, p.week5track "
        "FROM users u JOIN progress p ON u.username = p.username"
    )
    rows = []
    try:
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute(query)
            for fullname, username, doj, w1, w2, w3, w4, w5 in cur.fetchall():
                weeks = {1: w1 or 0, 2: w2 or 0, 3: w3 or 0, 4: w4 or 0, 5: w5 or 0}
                pct = min(100, round(sum(weeks.values()) / _TOTAL_REQUIRED * 100))
                rows.append(
                    {
                        "fullname": fullname or username,
                        "username": username,
                        "doj": doj.strftime("%Y-%m-%d") if doj else "N/A",
                        "percent": pct,
                        "weeks": weeks,
                    }
                )
    except Error as e:
        st.error(f"Database error: {getattr(e, 'msg', e)}")
    return sorted(rows, key=lambda r: (-r["percent"], r["fullname"]))

# ───────────────────────────────────────────────────────────────
# Build HTML helpers
# ───────────────────────────────────────────────────────────────
_HTML_TEMPLATE = """<!DOCTYPE html><html lang="en"><head> … </head><body><div class="terminal"><div class="header"><h2 class="title">⚡ Progress Dashboard</h2><div class="stats">{{STATS}}</div></div>{{ROWS}}</div></body></html>"""  # template truncated for brevity

def _week_bar(week, done):
    req = _REQUIRED_TABS[week]
    pct = min(100, round(done / req * 100))
    color = _WEEK_COLORS.get(week, "#00d4ff")
    return (
        f'<div class="w-item" style="border-left-color:{color};">'
        f'<span class="w-lbl" style="color:{color};">W{week}</span>'
        f'<div class="w-prog"><div class="w-bar" style="background:{color};width:{pct}%;"></div></div>'
        f'<span class="w-count">{done}/{req}</span></div>'
    )

def _build_rows(parts):
    if not parts:
        return "<p class='no-data'>No participants found.</p>"

    stats = f"👥 {len(parts)} participants | 📊 {sum(p['percent'] for p in parts)/len(parts):.1f}% avg completion"
    rows_html = []
    for p in parts:
        weeks_html = "".join(
            _week_bar(w, c) for w, c in p["weeks"].items() if _REQUIRED_TABS[w]
        )
        rows_html.append(
            f'<div class="participant">'
            f'<div class="p-head"><span class="p-name">{p["fullname"]}</span>'
            f'<span class="p-doj">({p["doj"]})</span>'
            f'<div class="badge"><span class="pct">{p["percent"]}%</span>'
            f'<div class="o-bar"><div class="o-prog" style="width:{p["percent"]}%"></div></div></div></div>'
            f'<div class="weeks">{weeks_html}</div>'
            f'</div><div class="divider"></div>'
        )
    return _HTML_TEMPLATE.replace("{{STATS}}", stats).replace("{{ROWS}}", "\n".join(rows_html))

# ───────────────────────────────────────────────────────────────
# Streamlit entrypoint
# ───────────────────────────────────────────────────────────────
def show():
    st.set_page_config(page_title="Participants", layout="wide")
    parts = _fetch_participants()
    html_content = _build_rows(parts)
    html(html_content, height=min(900, 320 + len(parts) * 70), scrolling=True)

if __name__ == "__main__":
    show()
