import streamlit as st
from sqlalchemy import create_engine, inspect
import pandas as pd

# Database connection string (empty initially)
CONNECTION_STRING = ""

def connect_to_database():
    """Connect to the database and fetch available databases"""
    global CONNECTION_STRING
    CONNECTION_STRING = "mysql+mysqlconnector://vasant:12345@127.0.0.1/"
    try:
        # Attempt to establish connection
        engine = create_engine(CONNECTION_STRING)
        engine.connect()  # This will attempt to establish a connection
        st.success("Connection to the database was successful!")
        return True
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        return False

def get_databases():
    """Fetch available database names"""
    engine = create_engine(CONNECTION_STRING)
    inspector = inspect(engine)
    return inspector.get_schema_names()

def get_tables(database_name):
    """Fetch table names from the selected database"""
    engine = create_engine(f"mysql+mysqlconnector://vasant:12345@127.0.0.1/{database_name}")
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_table_data(table_name, database_name):
    """Fetch data from the selected database and table"""
    engine = create_engine(f"mysql+mysqlconnector://vasant:12345@127.0.0.1/{database_name}")
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)

# Streamlit UI
st.title("Database Table Viewer")

# Step 1: Connect to the database
if st.button("Step 1: Connect to Database"):
    connection_success = connect_to_database()
    if connection_success:
        st.session_state.connection_success = True
    else:
        st.session_state.connection_success = False

# Step 2: Fetch databases if connection succeeded
if 'connection_success' in st.session_state and st.session_state.connection_success:
    if st.button("Step 2: Fetch Databases"):
        try:
            with st.spinner("Fetching databases..."):
                databases = get_databases()
                if databases:
                    st.session_state.databases = databases
                    st.success("Databases fetched successfully!")
                else:
                    st.error("No databases found.")
        except Exception as e:
            st.error(f"Error fetching databases: {str(e)}")

# Step 3: Select a database once fetched
if 'databases' in st.session_state:
    selected_database = st.selectbox("Select a database", st.session_state.databases)
    if selected_database:
        st.session_state.selected_database = selected_database
        st.success(f"Selected database: {selected_database}")

# Step 4: Fetch tables for the selected database
if 'selected_database' in st.session_state:
    if st.button("Step 4: Fetch Tables"):
        try:
            with st.spinner(f"Fetching tables for {st.session_state.selected_database}..."):
                tables = get_tables(st.session_state.selected_database)
                if tables:
                    st.session_state.tables = tables
                    st.success("Tables fetched successfully!")
                else:
                    st.error("No tables found.")
        except Exception as e:
            st.error(f"Error fetching tables: {str(e)}")

# Step 5: Select a table once tables are fetched
if 'tables' in st.session_state:
    selected_table = st.selectbox("Select a table", st.session_state.tables)
    if selected_table:
        st.session_state.selected_table = selected_table
        st.success(f"Selected table: {selected_table}")

# Step 6: Display data from the selected table
if 'selected_table' in st.session_state:
    if st.button("Step 6: Fetch Table Data"):
        try:
            with st.spinner(f"Fetching data from {st.session_state.selected_table}..."):
                data = get_table_data(st.session_state.selected_table, st.session_state.selected_database)
                st.session_state.data = data
                st.success("Data fetched successfully!")
                st.write(f"Showing data from {st.session_state.selected_table}:")
                st.dataframe(data)
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
