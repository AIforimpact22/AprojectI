# control.py – Admin Control Panel for User Approvals (MySQL edition)
import streamlit as st
import mysql.connector
from mysql.connector import IntegrityError

# ──────────────────────────────────────────────────────────────────────────────
# DB helper                                                                    │
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

# ──────────────────────────────────────────────────────────────────────────────
# Admin authentication                                                         │
# ──────────────────────────────────────────────────────────────────────────────
def admin_login():
    st.subheader("Admin Login")
    admin_username = st.text_input("Admin Username", key="admin_username")
    admin_password = st.text_input("Admin Password", type="password", key="admin_password")
    if st.button("Login as Admin"):
        if (admin_username == st.secrets["admin"]["username"]
                and admin_password == st.secrets["admin"]["password"]):
            st.session_state["admin_logged_in"] = True
            st.success("Admin login successful!")
        else:
            st.error("Invalid admin credentials.")

# ──────────────────────────────────────────────────────────────────────────────
# Data helpers                                                                 │
# ──────────────────────────────────────────────────────────────────────────────
def get_pending_users():
    """
    Return a list of tuples:
        (rowid, fullname, email, phone, username)
    where approved == 0
    """
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute(
        """
        SELECT id, fullname, email, phone, username
        FROM users
        WHERE approved = 0
        """)
    pending = cur.fetchall()
    conn.close()
    return pending

def update_user_approval(rowid, new_status):
    """
    Set approved = new_status for the given user id.
    new_status:  1  → approved
                -1  → rejected
    """
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE users SET approved = %s WHERE id = %s",
        (new_status, rowid)
    )
    conn.commit()
    conn.close()

# ──────────────────────────────────────────────────────────────────────────────
# Admin UI                                                                     │
# ──────────────────────────────────────────────────────────────────────────────
def show_admin_panel():
    st.title("Admin Control Panel")
    st.write("Approve or Reject new user accounts")

    pending_users = get_pending_users()
    if pending_users:
        for user in pending_users:
            rowid, fullname, email, phone, username = user
            st.markdown(f"**Name:** {fullname} (*{username}*)")
            st.markdown(f"**Email:** {email}")
            st.markdown(f"**Phone:** {phone}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Approve", key=f"approve_{rowid}"):
                    update_user_approval(rowid, 1)
                    st.success(f"User {username} has been approved.")
                    st.experimental_rerun()
            with col2:
                if st.button("Reject", key=f"reject_{rowid}"):
                    update_user_approval(rowid, -1)
                    st.error(f"User {username} has been rejected.")
                    st.experimental_rerun()
            st.markdown("---")
    else:
        st.info("No pending users for approval.")

# ──────────────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.get("admin_logged_in", False):
        admin_login()
    else:
        show_admin_panel()

if __name__ == '__main__':
    main()
