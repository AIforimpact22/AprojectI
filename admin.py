import streamlit as st
import sqlite3
import os
import base64
import json
import pandas as pd
from github_sync import push_db_to_github

# ---------------------------------
# Utility Functions
# ---------------------------------
def get_connection():
    """Return a connection to the SQLite database."""
    db_path = st.secrets["general"]["db_path"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def push_changes():
    """Push the current database to GitHub."""
    db_path = st.secrets["general"]["db_path"]
    push_db_to_github(db_path)
    st.success("Database pushed to GitHub successfully.")

def backup_database():
    """Create a backup copy of the current database locally."""
    db_path = st.secrets["general"]["db_path"]
    backup_path = db_path + ".backup"
    try:
        with open(db_path, "rb") as original, open(backup_path, "wb") as backup:
            backup.write(original.read())
        st.success(f"Backup created at {backup_path}")
    except Exception as e:
        st.error(f"Error creating backup: {e}")

def restore_database(uploaded_file):
    """Replace the current database with an uploaded backup."""
    db_path = st.secrets["general"]["db_path"]
    try:
        with open(db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Database restored successfully!")
    except Exception as e:
        st.error(f"Error restoring database: {e}")

def get_table_schema(table):
    """Return the schema information for a table."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        schema = cursor.fetchall()
        conn.close()
        return schema
    except Exception as e:
        st.error(f"Error fetching schema for {table}: {e}")
        return []

def drop_column_from_table(table, col_to_drop):
    """
    Delete a column from a table by:
      1. Creating a new table without the unwanted column.
      2. Copying data from the old table to the new table.
      3. Dropping the old table.
      4. Renaming the new table to the old table name.
    """
    # Do not allow dropping the computed column "total" in the users table.
    if table == "users" and col_to_drop == "total":
        st.error("Cannot drop the computed column 'total'.")
        return
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Get current table schema
        cursor.execute(f"PRAGMA table_info({table})")
        schema_info = cursor.fetchall()
        if not schema_info:
            st.error(f"Could not retrieve schema for {table}.")
            return

        # Build a list of columns to keep (excluding col_to_drop)
        columns_to_keep = [col["name"] for col in schema_info if col["name"] != col_to_drop]
        if len(columns_to_keep) == len(schema_info):
            st.error(f"Column '{col_to_drop}' not found in table '{table}'.")
            return

        # 2. Create a new table schema (temporary name)
        new_table = f"{table}_temp"
        new_columns_def = []
        for col in schema_info:
            if col["name"] == col_to_drop:
                continue
            col_def = f"{col['name']} {col['type']}"
            if col["pk"]:
                col_def += " PRIMARY KEY"
            new_columns_def.append(col_def)
        new_columns_def_str = ", ".join(new_columns_def)
        create_new_table_sql = f"CREATE TABLE {new_table} ({new_columns_def_str});"
        cursor.execute(create_new_table_sql)

        # 3. Copy data from old table to new table
        cols_str = ", ".join(columns_to_keep)
        copy_data_sql = f"INSERT INTO {new_table} ({cols_str}) SELECT {cols_str} FROM {table};"
        cursor.execute(copy_data_sql)

        # 4. Drop old table
        cursor.execute(f"DROP TABLE {table};")

        # 5. Rename new table to the old table name
        cursor.execute(f"ALTER TABLE {new_table} RENAME TO {table};")

        conn.commit()
        st.success(f"Column '{col_to_drop}' deleted successfully from table '{table}'.")
    except Exception as e:
        st.error(f"Error deleting column: {e}")
    finally:
        conn.close()

def view_json_data():
    """Display the contents of user_progress.json file in a professional way."""
    try:
        # Assuming the JSON file is in the same directory as the app
        json_path = "user_progress.json"
        with open(json_path, "r") as file:
            json_data = json.load(file)
        
        # Display a summary of users
        st.subheader("User Progress Summary")
        st.info(f"Total Users: {len(json_data)}")
        
        # Create tabs for different view options
        tab1, tab2, tab3 = st.tabs(["Card View", "Table View", "Raw JSON"])
        
        # Tab 1: Card View - Display each user in a separate card
        with tab1:
            # Create a 2-column layout for the cards
            col1, col2 = st.columns(2)
            
            # Distribute users across columns
            for i, (username, progress) in enumerate(json_data.items()):
                # Alternate between columns
                current_col = col1 if i % 2 == 0 else col2
                
                with current_col:
                    with st.expander(f"User: {username}", expanded=True):
                        # Create a metrics row for quick summary
                        metrics_cols = st.columns(len(progress))
                        for j, (week, score) in enumerate(progress.items()):
                            metrics_cols[j].metric(label=week, value=score)
                        
                        # Show progress bar
                        total_possible = 5 * 10  # Assuming 5 weeks with max 10 points each
                        total_score = sum(progress.values())
                        progress_percentage = (total_score / total_possible) * 100
                        st.progress(progress_percentage / 100)
                        st.caption(f"Total Progress: {total_score}/{total_possible} points ({progress_percentage:.1f}%)")
        
        # Tab 2: Table View - Display as a formatted table
        with tab2:
            # Convert JSON to a table format
            table_data = []
            for username, progress in json_data.items():
                row = {"Username": username}
                row.update(progress)
                table_data.append(row)
            
            # Create DataFrame and display as table
            if table_data:
                df = pd.DataFrame(table_data)
                
                # Apply conditional formatting (custom CSS) for better visualization
                # Define function for styling the DataFrame
                def highlight_progress(val):
                    if isinstance(val, (int, float)):
                        color = f"rgba(76, 175, 80, {val/10})" if val > 0 else "#f0f2f6"
                        return f'background-color: {color}'
                    return ""
                
                # Apply styling
                styled_df = df.style.applymap(highlight_progress)
                st.dataframe(styled_df, use_container_width=True)
                
                # Add download button for CSV export
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download as CSV",
                    csv,
                    "user_progress.csv",
                    "text/csv",
                    key="download-csv"
                )
        
        # Tab 3: Raw JSON - Show the JSON with syntax highlighting
        with tab3:
            st.code(json.dumps(json_data, indent=4), language="json")
            
            # Add edit option
            if st.checkbox("Edit JSON data"):
                json_str = st.text_area("Edit JSON", value=json.dumps(json_data, indent=4), height=400)
                if st.button("Save JSON changes"):
                    try:
                        # Parse to ensure valid JSON
                        updated_data = json.loads(json_str)
                        # Write back to file
                        with open(json_path, "w") as file:
                            json.dump(updated_data, file, indent=4)
                        st.success("JSON data updated successfully!")
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid JSON format: {e}")
    
    except FileNotFoundError:
        st.error("user_progress.json file not found. Please check the file path.")
    except json.JSONDecodeError:
        st.error("The file contains invalid JSON data.")
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")

# ---------------------------------
# Admin Authentication
# ---------------------------------
def admin_login():
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        st.title("Admin Login")
        username = st.text_input("Admin Username")
        password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if (username == st.secrets["admin"]["username"] and
                    password == st.secrets["admin"]["password"]):
                st.session_state["admin_logged_in"] = True
                st.success("Logged in as admin!")
            else:
                st.error("Invalid credentials. Please try again.")
    return st.session_state["admin_logged_in"]

# ---------------------------------
# Advanced Admin Interface
# ---------------------------------
if admin_login():
    st.title("Advanced Admin Dashboard")
    st.write("Full control over your SQLite database.")

    # Sidebar for quick navigation
    with st.sidebar:
        st.header("Navigation")
        nav_option = st.radio("Select an operation", [
            "Execute SQL",
            "View Schema",
            "Create Table",
            "Drop Table",
            "Insert Row",
            "Edit Row",
            "Delete Row",
            "Alter Table",      # For schema changes (add or delete column)
            "Backup/Restore",
            "View User Progress JSON",  # New option added here
        ])

    # --- 1. Execute Arbitrary SQL ---
    if nav_option == "Execute SQL":
        st.subheader("Execute Arbitrary SQL")
        st.info("⚠️ Use this with caution. Any valid SQL command can be executed.")
        sql_command = st.text_area("Enter SQL command")
        if st.button("Execute SQL"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(sql_command)
                conn.commit()
                st.success("SQL executed successfully.")
                if sql_command.strip().lower().startswith("select"):
                    results = cursor.fetchall()
                    st.write("Results:", [dict(row) for row in results])
            except Exception as e:
                st.error(f"Error executing SQL: {e}")
            finally:
                conn.close()
        st.button("Push changes to GitHub", on_click=push_changes)

    # --- 2. View Database Schema ---
    elif nav_option == "View Schema":
        st.subheader("View Database Schema")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Filter out system tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            conn.close()
            if tables:
                for table in tables:
                    with st.expander(f"Table: {table}"):
                        schema = get_table_schema(table)
                        if schema:
                            st.table(schema)
                        else:
                            st.write("No schema information available.")
            else:
                st.write("No tables found in the database.")
        except Exception as e:
            st.error(f"Error retrieving tables: {e}")

    # --- 3. Create New Table ---
    elif nav_option == "Create Table":
        st.subheader("Create New Table")
        new_table_name = st.text_input("Enter new table name")
        st.write("Define columns (one per line) in the format: column_name DATA_TYPE")
        st.write("Example:")
        st.code("id INTEGER PRIMARY KEY\nname TEXT\nage INTEGER")
        columns_definition = st.text_area("Columns definition")
        if st.button("Create Table"):
            if new_table_name.strip() == "" or columns_definition.strip() == "":
                st.error("Table name and columns definition are required.")
            else:
                try:
                    query = f"CREATE TABLE {new_table_name} ({columns_definition})"
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    st.success(f"Table '{new_table_name}' created successfully!")
                except Exception as e:
                    st.error(f"Error creating table: {e}")
                finally:
                    conn.close()
        st.button("Push changes to GitHub", on_click=push_changes)

    # --- 4. Drop Table ---
    elif nav_option == "Drop Table":
        st.subheader("Drop Table")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            conn.close()
            table_to_drop = st.selectbox("Select table to drop", tables)
            if st.button("Drop Table"):
                confirm = st.checkbox("I understand this will permanently delete the table.")
                if confirm:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute(f"DROP TABLE {table_to_drop}")
                        conn.commit()
                        st.success(f"Table '{table_to_drop}' dropped successfully!")
                    except Exception as e:
                        st.error(f"Error dropping table: {e}")
                    finally:
                        conn.close()
                else:
                    st.warning("Please confirm that you understand the consequences.")
        except Exception as e:
            st.error(f"Error retrieving tables: {e}")
        st.button("Push changes to GitHub", on_click=push_changes)

    # --- 5. Insert Row ---
    elif nav_option == "Insert Row":
        st.subheader("Insert Row into Table")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            tables = []
        if tables:
            table = st.selectbox("Select Table", tables, key="insert_table")
            schema = get_table_schema(table)
            # If inserting into the users table, exclude the computed column "total"
            if table == "users":
                schema = [col for col in schema if col["name"] != "total"]
            if schema:
                st.write("Table Columns:", [col["name"] for col in schema])
                new_data = {}
                for col in schema:
                    new_data[col["name"]] = st.text_input(f"Enter value for '{col['name']}'", key=f"insert_{col['name']}")
                if st.button("Insert Row"):
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        columns = [col["name"] for col in schema]
                        placeholders = ", ".join(["?"] * len(columns))
                        col_names_str = ", ".join(columns)
                        values = [new_data[col] for col in columns]
                        cursor.execute(
                            f"INSERT INTO {table} ({col_names_str}) VALUES ({placeholders})", values
                        )
                        conn.commit()
                        st.success("Row inserted successfully.")
                    except Exception as e:
                        st.error(f"Error inserting row: {e}")
                    finally:
                        conn.close()
            else:
                st.write("Could not retrieve table schema.")
        st.button("Push changes to GitHub", on_click=push_changes)

    # --- 6. Edit Row ---
    elif nav_option == "Edit Row":
        st.subheader("Edit Row in a Table")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            tables = []
        if tables:
            table = st.selectbox("Select Table", tables, key="edit_table")
            st.write("Enter a WHERE clause to identify the row(s) you want to edit (e.g., id = 1):")
            where_clause = st.text_input("WHERE clause (without 'WHERE')", key="edit_where")
            if st.button("Fetch Row(s)"):
                if where_clause.strip() == "":
                    st.error("WHERE clause cannot be empty.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT * FROM {table} WHERE {where_clause}")
                        rows = cursor.fetchall()
                        if rows:
                            st.write("Rows to edit:")
                            for idx, row in enumerate(rows):
                                st.write(f"Row {idx+1}:", dict(row))
                            st.session_state["edit_rows"] = [dict(r) for r in rows]
                        else:
                            st.warning("No matching rows found.")
                    except Exception as e:
                        st.error(f"Error fetching rows: {e}")
                    finally:
                        conn.close()
            if "edit_rows" in st.session_state and st.session_state["edit_rows"]:
                st.write("Update values for the fetched rows (this example updates the first matching row):")
                # Exclude the computed column "total" if present
                row_data = st.session_state["edit_rows"][0]
                if table == "users" and "total" in row_data:
                    row_data = {k: v for k, v in row_data.items() if k != "total"}
                updated_data = {}
                for key, value in row_data.items():
                    updated_data[key] = st.text_input(f"Value for {key}", value=value, key=f"edit_{key}")
                if st.button("Update Row"):
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        set_clause = ", ".join([f"{col} = ?" for col in updated_data.keys()])
                        values = list(updated_data.values())
                        update_query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                        cursor.execute(update_query, values)
                        conn.commit()
                        st.success("Row updated successfully.")
                        st.session_state.pop("edit_rows")
                    except Exception as e:
                        st.error(f"Error updating row: {e}")
                    finally:
                        conn.close()
        st.button("Push changes to GitHub", on_click=push_changes)

    # --- 7. Delete Row ---
    elif nav_option == "Delete Row":
        st.subheader("Delete Row(s) from Table")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            tables = []
        if tables:
            table = st.selectbox("Select Table", tables, key="delete_table")
            st.write("Provide a WHERE clause to identify rows to delete (e.g., id = 1):")
            where_clause = st.text_input("WHERE clause (without 'WHERE')", key="delete_where")
            if st.button("Delete Row(s)"):
                if where_clause.strip() == "":
                    st.error("WHERE clause cannot be empty.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        query = f"DELETE FROM {table} WHERE {where_clause}"
                        cursor.execute(query)
                        conn.commit()
                        st.success("Row(s) deleted successfully.")
                    except Exception as e:
                        st.error(f"Error deleting row(s): {e}")
                    finally:
                        conn.close()
        st.button("Push changes to GitHub", on_click=push_changes)

    # --- 8. Alter Table (Add or Delete Column) ---
    elif nav_option == "Alter Table":
        st.subheader("Alter Table Options")
        alter_option = st.radio("Choose an alteration:", ["Add Column", "Delete Column"])

        # Get list of tables
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            tables = []

        if tables:
            table = st.selectbox("Select Table to Alter", tables, key="alter_table")
            schema = get_table_schema(table)
            st.write("Current schema:", [f"{col['name']} ({col['type']})" for col in schema])

            if alter_option == "Add Column":
                new_column_name = st.text_input("New Column Name", key="new_column_name")
                new_column_type = st.text_input("Data Type (e.g., TEXT, INTEGER, REAL)", key="new_column_type")
                if st.button("Add Column"):
                    if new_column_name.strip() == "" or new_column_type.strip() == "":
                        st.error("Both the column name and data type are required.")
                    else:
                        try:
                            alter_query = f"ALTER TABLE {table} ADD COLUMN {new_column_name} {new_column_type}"
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute(alter_query)
                            conn.commit()
                            st.success(f"Column '{new_column_name}' added to '{table}' successfully!")
                        except Exception as e:
                            st.error(f"Error adding column: {e}")
                        finally:
                            conn.close()
                st.button("Push changes to GitHub", on_click=push_changes)

            elif alter_option == "Delete Column":
                col_names = [col["name"] for col in schema]
                col_to_delete = st.selectbox("Select Column to Delete", col_names, key="col_to_delete")
                if table == "users" and col_to_delete == "total":
                    st.error("Cannot delete the computed column 'total'.")
                else:
                    st.warning("Deleting a column will recreate the table without the selected column. This operation is irreversible.")
                    if st.button("Delete Column"):
                        drop_column_from_table(table, col_to_delete)
                st.button("Push changes to GitHub", on_click=push_changes)

    # --- 9. Backup / Restore ---
    elif nav_option == "Backup/Restore":
        st.subheader("Backup / Restore Database")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Backup Database")
            if st.button("Create Backup"):
                backup_database()
        with col2:
            st.markdown("### Restore Database")
            uploaded_file = st.file_uploader("Upload backup file", type=["db", "sqlite", "backup"])
            if uploaded_file is not None:
                if st.button("Restore Backup"):
                    restore_database(uploaded_file)
                    st.button("Push changes to GitHub", on_click=push_changes)
    
    # --- 10. View User Progress JSON ---
    elif nav_option == "View User Progress JSON":
        view_json_data()
        # Add a button to push any changes to GitHub if needed
        if st.button("Push changes to GitHub"):
            push_changes()
