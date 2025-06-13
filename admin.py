# admin.py – Advanced Admin Dashboard (now MySQL only, no GitHub push)
import streamlit as st
import mysql.connector
from mysql.connector import Error, IntegrityError
import json, pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# DB helper                                                                    │
# ──────────────────────────────────────────────────────────────────────────────
def get_connection():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )

# Schema helper – INFORMATION_SCHEMA.COLUMNS
def get_table_schema(table):
    try:
        conn = get_connection(); cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT COLUMN_NAME AS name,
                   COLUMN_TYPE AS type,
                   IS_NULLABLE = 'NO' AS notnull,
                   COLUMN_KEY = 'PRI' AS pk
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s
            ORDER BY ORDINAL_POSITION
            """,
            (table,),
        )
        schema = cur.fetchall()
        conn.close()
        return schema
    except Error as e:
        st.error(f"Error fetching schema for {table}: {e}")
        return []

# List user tables (skip information_schema / mysql)
def list_tables():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables

# ──────────────────────────────────────────────────────────────────────────────
# Admin login                                                                  │
# ──────────────────────────────────────────────────────────────────────────────
def admin_login():
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        st.title("Admin Login")
        u = st.text_input("Admin Username")
        p = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if u == st.secrets["admin"]["username"] and p == st.secrets["admin"]["password"]:
                st.session_state["admin_logged_in"] = True
                st.success("Logged in as admin!")
            else:
                st.error("Invalid credentials.")
    return st.session_state["admin_logged_in"]

# ──────────────────────────────────────────────────────────────────────────────
# Main dashboard                                                               │
# ──────────────────────────────────────────────────────────────────────────────
if admin_login():
    st.title("Advanced Admin Dashboard (MySQL)")
    with st.sidebar:
        nav = st.radio(
            "Navigation",
            [
                "Execute SQL",
                "View Schema",
                "Create Table",
                "Drop Table",
                "Insert Row",
                "Edit Row",
                "Delete Row",
                "Alter Table",
                "View User Progress",
            ],
        )

    # 1 ─ Execute arbitrary SQL ------------------------------------------------
    if nav == "Execute SQL":
        st.subheader("Execute SQL")
        sql = st.text_area("Enter SQL command")
        if st.button("Run"):
            try:
                conn = get_connection(); cur = conn.cursor(dictionary=True)
                cur.execute(sql)
                if sql.strip().lower().startswith("select"):
                    rows = cur.fetchall()
                    st.dataframe(pd.DataFrame(rows))
                conn.commit()
                st.success("Success.")
            except Error as e:
                st.error(f"MySQL error: {e}")
            finally:
                conn.close()

    # 2 ─ View schema ----------------------------------------------------------
    elif nav == "View Schema":
        st.subheader("Database Schema")
        for tbl in list_tables():
            with st.expander(tbl):
                schema = get_table_schema(tbl)
                st.table(schema)

    # 3 ─ Create table ---------------------------------------------------------
    elif nav == "Create Table":
        name = st.text_input("Table name")
        st.write("Columns (one per line, e.g. `id INT PRIMARY KEY`, `name VARCHAR(100)`)")
        cols = st.text_area("Definition")
        if st.button("Create"):
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute(f"CREATE TABLE {name} ({cols})")
                conn.commit()
                st.success(f"Table `{name}` created.")
            except Error as e:
                st.error(e)
            finally:
                conn.close()

    # 4 ─ Drop table -----------------------------------------------------------
    elif nav == "Drop Table":
        tbl = st.selectbox("Select table", list_tables())
        if st.button("Drop"):
            if st.checkbox("Really drop?"):
                try:
                    conn = get_connection(); cur = conn.cursor()
                    cur.execute(f"DROP TABLE {tbl}")
                    conn.commit()
                    st.success("Dropped.")
                except Error as e:
                    st.error(e)
                finally:
                    conn.close()

    # 5 ─ Insert row -----------------------------------------------------------
    elif nav == "Insert Row":
        tbl = st.selectbox("Table", list_tables())
        schema = get_table_schema(tbl)
        data = {}
        for col in schema:
            data[col["name"]] = st.text_input(col["name"], key=f"ins_{col['name']}")
        if st.button("Insert"):
            cols = ", ".join(data.keys())
            vals = list(data.values())
            ph   = ", ".join(["%s"] * len(vals))
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute(f"INSERT INTO {tbl} ({cols}) VALUES ({ph})", vals)
                conn.commit()
                st.success("Inserted.")
            except IntegrityError as e:
                st.error(f"Integrity error: {e}")
            except Error as e:
                st.error(e)
            finally:
                conn.close()

    # 6 ─ Edit row -------------------------------------------------------------
    elif nav == "Edit Row":
        tbl = st.selectbox("Table", list_tables(), key="edit_tbl")
        where = st.text_input("WHERE clause (e.g. id=1)")
        if st.button("Fetch"):
            try:
                conn = get_connection(); cur = conn.cursor(dictionary=True)
                cur.execute(f"SELECT * FROM {tbl} WHERE {where}")
                rows = cur.fetchall()
                conn.close()
                if not rows:
                    st.warning("No rows.")
                else:
                    st.session_state["rows_to_edit"] = rows
            except Error as e:
                st.error(e)

        if "rows_to_edit" in st.session_state:
            row = st.session_state["rows_to_edit"][0]
            new_vals = {}
            for k, v in row.items():
                new_vals[k] = st.text_input(k, value=v, key=f"up_{k}")
            if st.button("Update"):
                set_clause = ", ".join([f"{k}=%s" for k in new_vals])
                try:
                    conn = get_connection(); cur = conn.cursor()
                    cur.execute(
                        f"UPDATE {tbl} SET {set_clause} WHERE {where}",
                        list(new_vals.values()),
                    )
                    conn.commit()
                    st.success("Updated.")
                    st.session_state.pop("rows_to_edit")
                except Error as e:
                    st.error(e)
                finally:
                    conn.close()

    # 7 ─ Delete row -----------------------------------------------------------
    elif nav == "Delete Row":
        tbl = st.selectbox("Table", list_tables(), key="del_tbl")
        where = st.text_input("WHERE clause")
        if st.button("Delete"):
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute(f"DELETE FROM {tbl} WHERE {where}")
                conn.commit()
                st.success("Deleted.")
            except Error as e:
                st.error(e)
            finally:
                conn.close()

    # 8 ─ Alter table (add / drop column) --------------------------------------
    elif nav == "Alter Table":
        tbl = st.selectbox("Table", list_tables(), key="alt_tbl")
        choice = st.radio("Action", ["Add Column", "Drop Column"])
        if choice == "Add Column":
            col = st.text_input("Column definition (e.g. `age INT`)")
            if st.button("Add"):
                try:
                    conn = get_connection(); cur = conn.cursor()
                    cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col}")
                    conn.commit()
                    st.success("Column added.")
                except Error as e:
                    st.error(e)
                finally:
                    conn.close()
        else:  # Drop column
            cols = [c["name"] for c in get_table_schema(tbl)]
            col = st.selectbox("Column to drop", cols)
            if st.button("Drop"):
                st.warning("MySQL requires table rebuild for dropping columns in some versions.")
                try:
                    conn = get_connection(); cur = conn.cursor()
                    cur.execute(f"ALTER TABLE {tbl} DROP COLUMN {col}")
                    conn.commit()
                    st.success("Dropped.")
                except Error as e:
                    st.error(e)
                finally:
                    conn.close()

    # 9 ─ View user progress ---------------------------------------------------
    elif nav == "View User Progress":
        st.subheader("User Progress")
        try:
            conn = get_connection(); cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT p.username,
                       p.fullname,
                       week1track, week2track, week3track, week4track, week5track
                FROM progress p
                ORDER BY p.fullname
                """
            )
            rows = cur.fetchall()
            conn.close()
            df = pd.DataFrame(rows)
            if not df.empty:
                df.rename(columns={
                    "fullname": "Full Name",
                    "week1track": "Week 1",
                    "week2track": "Week 2",
                    "week3track": "Week 3",
                    "week4track": "Week 4",
                    "week5track": "Week 5",
                }, inplace=True)
                st.dataframe(df, use_container_width=True)
            else:
                st.write("No data.")
        except Error as e:
            st.error(e)
