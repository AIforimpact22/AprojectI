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
# Give Week 5 a real tab-count so it isn’t filtered out
_REQUIRED_TABS = {1: 10, 2: 12, 3: 12, 4: 7, 5: 7}
_TOTAL_REQUIRED = sum(_REQUIRED_TABS.values()) or 1

_WEEK_COLORS = {1: "#27c93f", 2: "#0ff", 3: "#b19cd9", 4: "#ffbd2e", 5: "#f44"}

# ───────────────────────────────────────────────────────────────
# Fetch participants & progress
# ───────────────────────────────────────────────────────────────
def _fetch_participants():
    """Return list of dicts with full progress info + DOJ sorted by pct."""
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
            for (fullname, username, doj, w1, w2, w3, w4, w5) in cur.fetchall():
                weeks = {1: w1 or 0, 2: w2 or 0, 3: w3 or 0, 4: w4 or 0, 5: w5 or 0}
                percent = min(100, round(sum(weeks.values()) / _TOTAL_REQUIRED * 100))
                rows.append(
                    {
                        "fullname": fullname or username,
                        "username": username,
                        "doj": doj.strftime("%Y-%m-%d") if doj else "N/A",
                        "percent": percent,
                        "weeks": weeks,
                    }
                )
    except Error as e:
        st.error(f"Database error: {getattr(e, 'msg', e)}")
    return sorted(rows, key=lambda r: (-r["percent"], r["fullname"]))

# ───────────────────────────────────────────────────────────────
# Build HTML
# ───────────────────────────────────────────────────────────────
_HTML_TEMPLATE = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Participants Progress Dashboard</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&display=swap');
:root{
 --bg1:#0d1117;--bg2:#161b22;--bg3:#21262d;--green:#00ff41;--cyan:#00d4ff;
 --purple:#b19cd9;--yellow:#ffcc02;--red:#ff4757;--text:#f0f6fc;--text2:#8b949e;
 --border:#30363d;--glow:rgba(0,255,65,.5);}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:linear-gradient(135deg,#0a0e13 0%,#0d1117 50%,#161b22 100%);
     font-family:'JetBrains Mono',monospace;display:flex;justify-content:center;
     align-items:center;min-height:100vh;padding:20px;color:var(--text);}
.terminal{width:95%;max-width:1000px;background:var(--bg1);border:2px solid var(--green);
          border-radius:12px;box-shadow:0 0 30px rgba(0,255,65,.3),
          inset 0 0 20px rgba(0,255,65,.1);padding:30px;overflow:auto;}
.header{display:flex;align-items:center;margin-bottom:25px;padding-bottom:15px;
        border-bottom:1px solid var(--border);}
.title{color:var(--cyan);font-size:1.8rem;font-weight:700;
       text-shadow:0 0 10px rgba(0,212,255,.4);}
.stats{margin-left:auto;color:var(--text2);font-size:.9rem;}
.participant{padding:18px 0;}
.divider{border-top:1px solid var(--border);}
.p-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}
.p-name{font-size:1.05rem;font-weight:600;color:var(--yellow);}
.p-doj{font-size:.8rem;color:var(--text2);margin-left:10px;}
.badge{display:flex;align-items:center;background:var(--bg3);padding:6px 12px;
       border-radius:20px;border:1px solid var(--border);}
.pct{font-weight:700;margin-right:8px;color:var(--green);}
.o-bar{width:90px;height:8px;background:var(--bg3);border-radius:4px;overflow:hidden;}
.o-prog{height:100%;background:linear-gradient(90deg,var(--green),var(--cyan));
        border-radius:4px;transition:width .8s ease;box-shadow:0 0 6px var(--glow);}
.weeks{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;}
.w-item{display:flex;align-items:center;background:var(--bg2);padding:6px 10px;
        border-radius:6px;border-left:3px solid;}
.w-lbl{font-weight:500;margin-right:6px;min-width:38px;font-size:.85rem;}
.w-prog{flex:1;height:6px;background:var(--bg1);border-radius:3px;overflow:hidden;margin-right:6px;}
.w-bar{height:100%;border-radius:3px;}
.w-count{font-size:.75rem;color:var(--text2);}
</style></head><body>
<div class="terminal">
<div class="header"><h2 class="title">⚡ Progress Dashboard</h2>
<div class="stats">{{STATS}}</div></div>{{ROWS}}</div></body></html>"""

def _week_bar(w: int, done: int) -> str:
    req = _REQUIRED_TABS.get(w, 1) or 1
    pct = min(100, round(done / req * 100))
    color = _WEEK_COLORS.get(w, "#00d4ff")
    return (
        f'<div class="w-item" style="border-left-color:{color};">'
        f'<span class="w-lbl" style="color:{color};">W{w}</span>'
        f'<div class="w-prog"><div class="w-bar" style="background:{color};width:{pct}%;"></div></div>'
        f'<span class="w-count">{done}/{req}</span></div>'
    )

def _build_rows(parts):
    if not parts:
        return "<p class='no-data'>No participants found.</p>"
    stats = (
        f"👥 {len(parts)} participants | "
        f"📊 {sum(p['percent'] for p in parts)/len(parts):.1f}% avg completion"
    )
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
            f'<div class="o-bar"><div class="o-prog" style="width:{p["percent"]}%"></div></div>'
            f'</div></div><div class="weeks">{weeks_html}</div></div>'
            f'<div class="divider"></div>'
        )
    return (
        _HTML_TEMPLATE.replace("{{STATS}}", stats)
        .replace("{{ROWS}}", "\n".join(rows_html))
    )

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
