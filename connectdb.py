import streamlit as st
import mysql.connector
from mysql.connector import Error

# Database connection string (empty initially)
CONNECTION_STRING = {
    "host": "127.0.0.1",
    "user": "vasant",
    "password": "12345"
}

# Streamlit UI
st.title("Database Table Viewer")

# Step 1: Connect to the database
if st.button("Step 1: Connect to Database"):
    try:
        # Attempt to establish connection
        st.write("Attempting to connect to the database...")
        
        # Create a connection using mysql-connector
        connection = mysql.connector.connect(**CONNECTION_STRING)
        
        if connection.is_connected():
            # Check if the connection is established
            st.success("Connection to the database was successful!")
            st.session_state.connection_success = True
            
            # Get the server information
            db_info = connection.get_server_info()
            st.write(f"Connected to MySQL Server version {db_info}")
            
            connection.close()
        else:
            st.error("Failed to connect to the database")
            st.session_state.connection_success = False
            
    except Error as e:
        # Print detailed error message
        st.write(f"Connection failed: {str(e)}")
        st.session_state.connection_success = False

# Step 2: Fetch Databases if connection is successful
if 'connection_success' in st.session_state and st.session_state.connection_success:
    if st.button("Step 2: Fetch Databases"):
        try:
            # Establish a new connection to fetch databases
            connection = mysql.connector.connect(**CONNECTION_STRING)
            cursor = connection.cursor()
            
            # Query to fetch databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            # Show available databases in dropdown
            databases_list = [db[0] for db in databases]
            selected_database = st.selectbox("Select a database", databases_list)
            
            if selected_database:
                st.session_state.selected_database = selected_database
                st.success(f"Selected database: {selected_database}")
                
            cursor.close()
            connection.close()
        
        except Error as e:
            st.write(f"Failed to fetch databases: {str(e)}")

# Step 3: Fetch Tables if a database is selected
if 'selected_database' in st.session_state:
    selected_database = st.session_state.selected_database
    if st.button("Step 3: Fetch Tables"):
        try:
            # Establish a connection to the selected database
            connection = mysql.connector.connect(
                host=CONNECTION_STRING["host"],
                user=CONNECTION_STRING["user"],
                password=CONNECTION_STRING["password"],
                database=selected_database
            )
            cursor = connection.cursor()
            
            # Query to fetch tables in the selected database
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            # Show available tables in dropdown
            tables_list = [table[0] for table in tables]
            selected_table = st.selectbox("Select a table", tables_list)
            
            if selected_table:
                st.session_state.selected_table = selected_table
                st.success(f"Selected table: {selected_table}")
            
            cursor.close()
            connection.close()
        
        except Error as e:
            st.write(f"Failed to fetch tables: {str(e)}")
