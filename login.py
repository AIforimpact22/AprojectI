# login.py - Manages user authentication, registration, and password recovery
import streamlit as st
import mysql.connector
from mysql.connector import errorcode, IntegrityError
import smtplib
from email.message import EmailMessage
import datetime

from database import create_tables
from theme import apply_dark_theme
from github_sync import push_db_to_github  # unchanged, still called after registration


# ──────────────────────────────────────────────────────────────────────────────
# Helpers                                                                     │
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


def send_password_email(recipient_email, username, password):
    """
    Sends an email with the user's password using TLS on port 587.
    """
    try:
        smtp_server   = st.secrets["smtp"]["server"]
        smtp_port     = st.secrets["smtp"]["port"]
        smtp_email    = st.secrets["smtp"]["email"]
        smtp_password = st.secrets["smtp"]["password"]

        msg = EmailMessage()
        msg.set_content(
            f"Hi {username},\n\n"
            "We received a request to send you back your password.\n"
            f"Here is your password: {password}\n\n"
            "If you have any questions, please contact us.\n\n"
            "AI For Impact team"
        )
        msg["Subject"] = "Password Recovery"
        msg["From"]    = smtp_email
        msg["To"]      = recipient_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# DB operations                                                               │
# ──────────────────────────────────────────────────────────────────────────────
def register_user(fullname, email, phone, username, password, date_of_joining):
    """
    Registers a new user in the MySQL database with approved status 0.
    Returns True on success, False otherwise.
    """
    conn = _get_conn()
    cur  = conn.cursor()

    # Ensure password is unique
    cur.execute("SELECT 1 FROM users WHERE password = %s", (password,))
    if cur.fetchone():
        conn.close()
        return False

    try:
        cur.execute(
            """
            INSERT INTO users
                (fullname, email, phone, username, password, date_of_joining)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (fullname, email, phone, username, password, date_of_joining),
        )
        conn.commit()
    except IntegrityError:
        conn.close()
        return False

    conn.close()
    return True


def login_user(username, password):
    """
    Validates username/password and checks if the user is approved.
    Returns the user row if valid and approved, "not_approved" if not approved,
    or None if invalid.
    """
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password),
    )
    user = cur.fetchone()
    conn.close()

    if user:
        approved = user[6]    # 7th column is 'approved'
        if approved != 1:
            return "not_approved"
    return user


# ──────────────────────────────────────────────────────────────────────────────
# UI                                                                          │
# ──────────────────────────────────────────────────────────────────────────────
def show_login_create_account():
    """
    Renders the login, create account, and forgot password tabs.
    """
    apply_dark_theme()
    create_tables()  # Ensure database and tables exist

    tabs = st.tabs(["Login", "Create Account", "Forgot Password"])

    # ─────────────────────────
    # LOGIN TAB
    with tabs[0]:
        st.subheader("🔑 Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = login_user(username, password)
            if user == "not_approved":
                st.error("Your account has not been approved yet. Please wait for admin approval.")
            elif user:
                st.session_state["logged_in"] = True
                st.session_state["username"]   = username
                st.session_state["page"]       = "home"
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    # ─────────────────────────
    # CREATE ACCOUNT TAB
    with tabs[1]:
        st.subheader("🆕 Create Account")
        reg_fullname  = st.text_input("Full Name", key="reg_fullname")
        reg_email     = st.text_input("Email", key="reg_email")
        reg_phone     = st.text_input("Mobile Number", key="reg_phone")
        reg_username  = st.text_input("Username", key="reg_username")
        reg_password  = st.text_input("Password", type="password", key="reg_password")
        reg_doj       = st.date_input("Date of Joining", value=datetime.date.today(), key="reg_doj")

        if st.button("Register"):
            if all([reg_fullname, reg_email, reg_phone, reg_username, reg_password, reg_doj]):
                try:
                    phone_int = int(reg_phone)
                except ValueError:
                    st.error("❌ Please enter a valid phone number (digits only).")
                    return

                success = register_user(
                    reg_fullname, reg_email, phone_int,
                    reg_username, reg_password, reg_doj
                )
                if not success:
                    st.error("⚠️ Username or Password already exists. Choose a different one.")
                else:
                    st.success("✅ Account created! Please wait for admin approval before logging in.")
                    # still push the (possibly obsolete) db file if your workflow needs it
                    push_db_to_github(st.secrets["general"]["db_path"])
            else:
                st.error("⚠️ Please fill out all fields.")

    # ─────────────────────────
    # FORGOT PASSWORD TAB
    with tabs[2]:
        st.subheader("🔒 Forgot Password")
        forgot_email = st.text_input("Enter your registered email", key="forgot_email")
        if st.button("Retrieve Password"):
            if not forgot_email:
                st.error("Please enter an email address.")
            else:
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "SELECT username, password FROM users WHERE email = %s",
                    (forgot_email,),
                )
                result = cur.fetchone()
                conn.close()

                if result:
                    username, password = result
                    if send_password_email(forgot_email, username, password):
                        st.success("Your password has been sent to your email address.")
                    else:
                        st.error("Failed to send email. Please try again later.")
                else:
                    st.error("This email is not registered in our system.")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    show_login_create_account()
