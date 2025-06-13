# admin.py – read-only admin dashboard (MySQL backend)
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _get_conn():
    """Connect to the MySQL database using [mysql] in secrets.toml"""
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )


def _fetch_progress():
    """
    Returns a pandas DataFrame with:
      username · fullname · week1 … week5 · total_tabs · percent_complete
    """
    conn = _get_conn()
    q = """
        SELECT p.username,
               p.fullname,
               p.week1track, p.week2track, p.week3track, p.week4track, p.week5track
        FROM progress AS p
        ORDER BY p.fullname
    """
    df = pd.read_sql(q, conn)

    # calculate totals (assumes week1 max 10, week2 max 12, week3 max 12, week4 max 12, week5 max 7)
    week_max = {1: 10, 2: 12, 3: 12, 4: 12, 5: 7}
    df["total_tabs"] = (
        df["week1track"] + df["week2track"] + df["week3track"] +
        df["week4track"] + df["week5track"]
    )
    max_possible = sum(week_max.values())
    df["percent_complete"] = (df["total_tabs"] / max_possible * 100).round(1)
    conn.close()
    return df, max_possible


def _style_df(df):
    def _bg(val, divisor):
        pct = 0 if divisor == 0 else val / divisor
        shade = int(255 - pct * 155)  # dark→light
        return f"background-color: rgb({shade},{shade},{shade})"

    styled = df.style
    for wk in range(1, 6):
        styled = styled.applymap(
            lambda v, _div=wk: _bg(v, {1:10,2:12,3:12,4:12,5:7}[_div]),
            subset=[f"week{wk}track"],
        )
    styled = styled.bar(
        subset=["percent_complete"],
        color="#4CAF50"
    )
    return styled


# ──────────────────────────────────────────────────────────────────────────────
# Admin authentication
# ──────────────────────────────────────────────────────────────────────────────
def _admin_login():
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        st.title("Admin Login")
        u = st.text_input("Admin Username")
        p = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if u == st.secrets["admin"]["username"] and p == st.secrets["admin"]["password"]:
                st.session_state["admin_logged_in"] = True
                st.success("Logged in!")
            else:
                st.error("Invalid credentials.")
    return st.session_state["admin_logged_in"]


# ──────────────────────────────────────────────────────────────────────────────
# Main app
# ──────────────────────────────────────────────────────────────────────────────
if _admin_login():
    st.title("Participant Progress Overview")

    df, max_possible = _fetch_progress()

    # search/filter
    search = st.text_input("Filter by name or username").lower().strip()
    if search:
        df = df[
            df["fullname"].str.lower().str.contains(search) |
            df["username"].str.lower().str.contains(search)
        ]

    st.subheader(f"Total participants: {len(df)}")
    styled_df = _style_df(df)
    st.dataframe(styled_df, use_container_width=True)

    # downloadable CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "progress.csv", "text/csv")
