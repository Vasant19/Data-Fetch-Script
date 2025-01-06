import streamlit as st
import mysql.connector
from mysql.connector import Error
import lida
from lida import Manager, TextGenerationConfig, llm
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os
import openai
import pandas as pd
import numpy as np
import random
from pptx import Presentation
from pptx.util import Inches
from io import BytesIO

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    openai.api_key = api_key
else:
    raise ValueError("OpenAI API key not found in environment variables!")

# Database connection string
CONNECTION_STRING = {
    "host": "127.0.0.1",
    "user": "vasant",
    "password": "12345"
}

# Helper functions
def base64_to_image(base64_string):
    byte_data = base64.b64decode(base64_string)
    return Image.open(BytesIO(byte_data))

def set_random_seed(seed):
    np.random.seed(seed)
    random.seed(seed)

def generate_ppt(image):
    prs = Presentation()
    
    # Add slide
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Layout 5 is blank
    
    # Add image to slide
    img_stream = BytesIO()
    image.save(img_stream, format='PNG')
    img_stream.seek(0)
    slide.shapes.add_picture(img_stream, Inches(0.5), Inches(0.5), width=Inches(9))
    
    # Save PPT to memory buffer
    ppt_stream = BytesIO()
    prs.save(ppt_stream)
    ppt_stream.seek(0)
    
    return ppt_stream

# Initialize session state variables
if 'connection_established' not in st.session_state:
    st.session_state.connection_established = False
if 'selected_database' not in st.session_state:
    st.session_state.selected_database = None
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = None
if 'chart_image' not in st.session_state:
    st.session_state.chart_image = None

# Streamlit UI
st.title("Database Table Viewer")

# Step 1: Connect to the database
if st.button("Step 1: Connect to Database"):
    try:
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

        selected_db = st.selectbox(
            "Select a database",
            databases_list,
            key='database_selector',
            index=databases_list.index(st.session_state.selected_database)
            if st.session_state.selected_database in databases_list else 0
        )

        if selected_db != st.session_state.selected_database:
            st.session_state.selected_database = selected_db
            st.session_state.selected_table = None
            st.rerun()

        cursor.close()

    except Error as e:
        st.error(f"Failed to fetch databases: {str(e)}")

# Step 3: Fetch and Select Tables
if st.session_state.selected_database:
    try:
        db_connection = mysql.connector.connect(
            **CONNECTION_STRING,
            database=st.session_state.selected_database
        )
        cursor = db_connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        tables_list = [table[0] for table in tables]

        if tables_list:
            selected_table = st.selectbox(
                "Select a table",
                tables_list,
                key='table_selector',
                index=tables_list.index(st.session_state.selected_table)
                if st.session_state.selected_table in tables_list else 0
            )

            if selected_table != st.session_state.selected_table:
                st.session_state.selected_table = selected_table
                st.rerun()
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
            query = f"SELECT * FROM {st.session_state.selected_table}"
            db_connection = mysql.connector.connect(
                **CONNECTION_STRING,
                database=st.session_state.selected_database
            )
            df = pd.read_sql(query, db_connection)
            st.session_state.df = df

            if not df.empty:
                st.write(df.head())
            else:
                st.info("No data found in the selected table")

            db_connection.close()

        except Error as e:
            st.error(f"Failed to fetch data: {str(e)}")

# Display current selections
if st.session_state.selected_database:
    st.sidebar.write(f"Current Database: {st.session_state.selected_database}")
if st.session_state.selected_table:
    st.sidebar.write(f"Current Table: {st.session_state.selected_table}")

# Final Step: Generate Visualization
if 'selected_table' in st.session_state and 'df' in st.session_state:
    try:
        lida = Manager(text_gen=llm("openai"))
        textgen_config = TextGenerationConfig(
            n=1, temperature=0.5, model="gpt-4o-mini", use_cache=True
        )

        user_query = st.text_input(
            "Enter your query for visualization:",
            placeholder="E.g., Give me a simple chart relevant to the selected table. Make sure the labelled text is visible "
        )

        if st.button("Generate Visualization"):
            set_random_seed(42)
            if not user_query.strip():
                st.warning("Please enter a valid query!")
            else:
                try:
                    df = st.session_state.df
                    summary = lida.summarize(data=df, summary_method="default", textgen_config=textgen_config)
                    st.session_state.summary = summary

                    library = "seaborn"
                    charts = lida.visualize(
                        summary=summary,
                        goal=user_query,
                        textgen_config=textgen_config,
                        library=library
                    )

                    if charts and len(charts) > 0:
                        st.write(f"Number of charts generated: {len(charts)}")
                        image_base64 = charts[0].raster
                        img = base64_to_image(image_base64)
                        st.session_state.chart_image = img  # Store image in session state
                        st.image(img)
                        
                    else:
                        st.error("No charts generated.")
                except Exception as e:
                    st.error(f"Failed to generate visualization: {str(e)}")

    except Exception as e:
        st.error(f"Error initializing LIDA Manager or configuration: {str(e)}")

# Export to PowerPoint button
if st.session_state.chart_image:
    if st.button("Export to PowerPoint"):
        ppt_stream = generate_ppt(st.session_state.chart_image)
        
        # Provide download link
        st.download_button(
            label="Download PowerPoint",
            data=ppt_stream,
            file_name="generated_chart.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
