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
        st.write("Attempting to connect to the database...")
        engine = create_engine(CONNECTION_STRING)
        
        # Try connecting to the database
        with engine.connect() as connection:
            # Check if the connection is established
            st.success("Connection to the database was successful!")
            return True
    except Exception as e:
        # Print detailed error message
        st.error(f"Connection failed: {str(e)}")
        return False

# Streamlit UI
st.title("Database Table Viewer")

# Step 1: Connect to the database
if st.button("Step 1: Connect to Database"):
    connection_success = connect_to_database()
    if connection_success:
        st.session_state.connection_success = True
    else:
        st.session_state.connection_success = False
