import streamlit as st
import mysql.connector
from mysql.connector import Error

# Database connection string (empty initially)
CONNECTION_STRING = {
    "host": "127.0.0.1",
    "user": "vasant",
    "password": "12345"
}

# Initialize session state variables
if 'connection_established' not in st.session_state:
    st.session_state.connection_established = False
if 'selected_database' not in st.session_state:
    st.session_state.selected_database = None
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = None

# Streamlit UI
st.title("Database Table Viewer")

# Step 1: Connect to the database
if st.button("Step 1: Connect to Database"):
    try:
        # Attempt to establish connection
        st.write("Attempting to connect to the database...")
        connection = mysql.connector.connect(**CONNECTION_STRING)

        if connection.is_connected():
            st.success("Connection to the database was successful!")
            db_info = connection.get_server_info()
            st.write(f"Connected to MySQL Server version {db_info}")
            st.session_state.connection_established = True
            st.session_state.connection = connection
        else:
            st.error("Failed to connect to the database")

    except Error as e:
        st.error(f"Connection failed: {str(e)}")

# Step 2: Fetch and Select Database
if st.session_state.connection_established:
    try:
        cursor = st.session_state.connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        databases_list = [db[0] for db in databases]
        
        # Create a selection widget for databases
        selected_db = st.selectbox(
            "Select a database",
            databases_list,
            key='database_selector',
            index=databases_list.index(st.session_state.selected_database) if st.session_state.selected_database in databases_list else 0
        )

        # Update selected database in session state when changed
        if selected_db != st.session_state.selected_database:
            st.session_state.selected_database = selected_db
            st.session_state.selected_table = None  # Reset table selection when database changes
            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()

        cursor.close()

    except Error as e:
        st.error(f"Failed to fetch databases: {str(e)}")

# Step 3: Fetch and Select Tables
if st.session_state.selected_database:
    try:
        # Create a new connection for the selected database
        db_connection = mysql.connector.connect(
            **CONNECTION_STRING,
            database=st.session_state.selected_database
        )
        cursor = db_connection.cursor()
        
        # Fetch tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        tables_list = [table[0] for table in tables]

        # Create a selection widget for tables
        if tables_list:
            selected_table = st.selectbox(
                "Select a table",
                tables_list,
                key='table_selector',
                index=tables_list.index(st.session_state.selected_table) if st.session_state.selected_table in tables_list else 0
            )

            # Update selected table in session state when changed
            if selected_table != st.session_state.selected_table:
                st.session_state.selected_table = selected_table
                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
        else:
            st.warning("No tables found in the selected database")

        cursor.close()
        db_connection.close()

    except Error as e:
        st.error(f"Failed to fetch tables: {str(e)}")

# Step 4: View Table Data
if st.session_state.selected_table:
    if st.button("View Table Data"):
        try:
            # Connect to the selected database
            db_connection = mysql.connector.connect(
                **CONNECTION_STRING,
                database=st.session_state.selected_database
            )
            cursor = db_connection.cursor(dictionary=True)  # Use dictionary cursor for named columns

            # Fetch data
            cursor.execute(f"SELECT * FROM {st.session_state.selected_table}")
            rows = cursor.fetchall()

            if rows:
                # Display data as a DataFrame for better visualization
                import pandas as pd
                df = pd.DataFrame(rows)

                # Show the first few rows
                st.write(df.head())  # You can use df.head() to preview the data

            else:
                st.info("No data found in the selected table")

            cursor.close()
            db_connection.close()

        except Error as e:
            st.error(f"Failed to fetch data: {str(e)}")

# Display current selections
if st.session_state.selected_database:
    st.sidebar.write(f"Current Database: {st.session_state.selected_database}")
if st.session_state.selected_table:
    st.sidebar.write(f"Current Table: {st.session_state.selected_table}")
