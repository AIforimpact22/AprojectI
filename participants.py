# participants.py  –  show every participant and their progress
import streamlit as st
import pandas as pd
import mysql.connector

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource(ttl=300)  # 5-minute cache to lighten DB load
def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )

def _fetch_progress_df() -> pd.DataFrame:
    """
    Returns one dataframe with:
      fullname | username | week1-5 | as1-4 | quiz1-2 | total
    """
    conn = _get_conn()
    cur = conn.cursor(dictionary=True)

    # Pull users (names) ------------------------------------------------------
    cur.execute("SELECT username, fullname FROM users")
    users = pd.DataFrame(cur.fetchall())

    # Pull week progress ------------------------------------------------------
    cur.execute("""
        SELECT username,
               week1track, week2track, week3track, week4track, week5track
        FROM progress
    """)
    weeks = pd.DataFrame(cur.fetchall())

    # Pull grades -------------------------------------------------------------
    cur.execute("""
        SELECT username, as1, as2, as3, as4, quiz1, quiz2, total
        FROM records
    """)
    grades = pd.DataFrame(cur.fetchall())

    cur.close()
    conn.close()

    # Merge all parts on username --------------------------------------------
    df = (
        users
        .merge(weeks,  how="left", on="username")
        .merge(grades, how="left", on="username")
        .fillna(0)  # if someone hasn’t started yet
        .astype({"week1track": int, "week2track": int, "week3track": int,
                 "week4track": int, "week5track": int})
    )
    return df

def _progress_bar(val: int, maximum: int) -> str:
    """Return an HTML progress bar cell with green/red colouring."""
    pct = int(100 * val / maximum)
    colour = "#0f0" if pct == 100 else "#f44"
    return f"""
      <div style='width:100%;background:#333;border-radius:4px;'>
        <div style='width:{pct}%;background:{colour};height:12px;border-radius:4px;'></div>
      </div>
      <small>{val}/{maximum}</small>
    """

# ──────────────────────────────────────────────────────────────────────────────
# Streamlit page
# ──────────────────────────────────────────────────────────────────────────────
def show():
    st.set_page_config(page_title="Participants Progress", layout="wide")
    st.title("📊 Participants & Progress Tracker")

    df = _fetch_progress_df()

    # Search / filter ---------------------------------------------------------
    with st.sidebar:
        st.header("🔍 Filter")
        query = st.text_input("Search by username or name")
        if query:
            mask = (
                df["username"].str.contains(query, case=False, na=False) |
                df["fullname"].str.contains(query, case=False, na=False)
            )
            df = df[mask]

    if df.empty:
        st.info("No participants match your search.")
        return

    # Build display dataframe with HTML progress bars -------------------------
    display_df = df.copy()
    week_requirements = {1: 10, 2: 10, 3: 12, 4: 12, 5: 7}  # same as gating logic

    for week, req in week_requirements.items():
        col = f"week{week}track"
        display_df[col] = display_df[col].apply(lambda v: _progress_bar(v, req))

    # Round numeric grades for cleaner display
    grade_cols = ["as1", "as2", "as3", "as4", "quiz1", "quiz2", "total"]
    display_df[grade_cols] = display_df[grade_cols].round(2)

    # Rename columns for readability
    display_df = display_df.rename(columns={
        "fullname": "Full Name",
        "username": "Username",
        "week1track": "Week 1",
        "week2track": "Week 2",
        "week3track": "Week 3",
        "week4track": "Week 4",
        "week5track": "Week 5",
        "as1": "As 1", "as2": "As 2", "as3": "As 3", "as4": "As 4",
        "quiz1": "Quiz 1", "quiz2": "Quiz 2",
        "total": "Total"
    })

    # Render ------------------------------------------------------------------
    st.write(f"Showing **{len(display_df)}** participant(s).")
    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    show()
