# admin.py – streamlined MySQL admin dashboard
import streamlit as st
import mysql.connector
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# DB helper
# ──────────────────────────────────────────────────────────────────────────────
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

def _load_df(table):
    conn = _get_conn()
    df   = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def _toggle_approval(username, approve: bool):
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE users SET approved = %s WHERE username = %s",
        (1 if approve else 0, username),
    )
    conn.commit()
    conn.close()

# ──────────────────────────────────────────────────────────────────────────────
# Admin authentication
# ──────────────────────────────────────────────────────────────────────────────
def admin_login():
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        st.title("Admin Login")
        u = st.text_input("Admin Username")
        p = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if (
                u == st.secrets["admin"]["username"]
                and p == st.secrets["admin"]["password"]
            ):
                st.session_state["admin_logged_in"] = True
                st.success("Logged in as admin!")
            else:
                st.error("Invalid credentials.")
    return st.session_state["admin_logged_in"]

# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────
if admin_login():
    st.title("Minimal Admin Dashboard (MySQL)")

    st.sidebar.header("Navigation")
    nav = st.sidebar.radio(
        "Choose view",
        ["Users", "Records", "Progress"],
        key="nav_choice",
    )

    # ---------- USERS --------------------------------------------------------
    if nav == "Users":
        st.subheader("All Users")

        df_users = _load_df("users")
        st.dataframe(df_users, use_container_width=True)

        # Approval toggles
        pending = df_users[df_users["approved"] != 1]
        if not pending.empty:
            st.markdown("### Pending Approvals")
            for _, row in pending.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{row['username']}** – {row['fullname']} ({row['email']})")
                with col2:
                    if st.button("Approve", key=f"approve_{row['username']}"):
                        _toggle_approval(row["username"], True)
                        st.experimental_rerun()

    # ---------- RECORDS ------------------------------------------------------
    elif nav == "Records":
        st.subheader("Assignment / Quiz Scores")

        df_records = _load_df("records")
        st.dataframe(df_records, use_container_width=True)

        csv = df_records.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "records.csv", "text/csv")

    # ---------- PROGRESS -----------------------------------------------------
    elif nav == "Progress":
        st.subheader("Weekly Progress")

        df_prog = _load_df("progress")
        st.dataframe(df_prog, use_container_width=True)

        csv = df_prog.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "progress.csv", "text/csv")
