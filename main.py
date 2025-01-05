import streamlit as st
import mysql.connector
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import pandas as pd
from datetime import datetime

# Database connection function
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )

# Function to get data from selected table
def get_table_data(table_name):
    conn = connect_to_db()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Function to generate relevant slides based on table content
def generate_slides(table_name, data):
    prs = Presentation()
    
    # Title slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = title_slide.shapes.title
    subtitle = title_slide.placeholders[1]
    title.text = f"{table_name.capitalize()} Analysis Report"
    subtitle.text = f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
    
    # Table specific slides
    if table_name == "customers":
        # Customer Overview slide
        overview_slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = overview_slide.shapes.title
        title.text = "Customer Overview"
        content = overview_slide.placeholders[1]
        content.text = f"""
        Total Customers: {len(data)}
        Countries Represented: {len(data['country'].unique())}
        Cities Represented: {len(data['city'].unique())}
        """
        
        # Customer Distribution slide
        dist_slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = dist_slide.shapes.title
        title.text = "Geographic Distribution"
        content = dist_slide.placeholders[1]
        country_dist = data['country'].value_counts().head(5)
        content.text = "Top 5 Countries:\n" + \
            "\n".join([f"{country}: {count} customers" 
                      for country, count in country_dist.items()])
    
    elif table_name == "orders":
        # Orders Overview slide
        overview_slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = overview_slide.shapes.title
        title.text = "Orders Overview"
        content = overview_slide.placeholders[1]
        content.text = f"""
        Total Orders: {len(data)}
        Total Order Value: ${data['total_amount'].sum():,.2f}
        Average Order Value: ${data['total_amount'].mean():,.2f}
        """
        
        # Order Trends slide
        if 'order_date' in data.columns:
            trend_slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = trend_slide.shapes.title
            title.text = "Order Trends"
            content = trend_slide.placeholders[1]
            monthly_orders = data.groupby(
                pd.to_datetime(data['order_date']).dt.strftime('%Y-%m')
            ).size()
            content.text = "Monthly Order Counts:\n" + \
                "\n".join([f"{month}: {count} orders" 
                          for month, count in monthly_orders.head(6).items()])
    
    elif table_name == "products":
        # Products Overview slide
        overview_slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = overview_slide.shapes.title
        title.text = "Products Overview"
        content = overview_slide.placeholders[1]
        content.text = f"""
        Total Products: {len(data)}
        Categories: {len(data['category'].unique() if 'category' in data.columns else 0)}
        Average Price: ${data['price'].mean():,.2f if 'price' in data.columns else 0}
        """
        
        # Top Products slide
        if 'price' in data.columns:
            top_slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = top_slide.shapes.title
            title.text = "Top Products by Price"
            content = top_slide.placeholders[1]
            top_products = data.nlargest(5, 'price')
            content.text = "Most Expensive Products:\n" + \
                "\n".join([f"{row['product_name']}: ${row['price']:,.2f}" 
                          for _, row in top_products.iterrows()])
    
    # Data Table slide (for all tables)
    table_slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = table_slide.shapes.title
    title.text = f"{table_name.capitalize()} Data Sample"
    
    # Add a sample of the data as a table
    sample_data = data.head(5)
    rows, cols = len(sample_data) + 1, len(sample_data.columns)
    left = top = Inches(1)
    width = Inches(8)
    height = Inches(0.8 * rows)
    
    shape = table_slide.shapes.add_table(rows, cols, left, top, width, height)
    table = shape.table
    
    # Set column headers
    for i, column in enumerate(sample_data.columns):
        table.cell(0, i).text = column
        
    # Fill data
    for i, row in enumerate(sample_data.itertuples()):
        for j, value in enumerate(row[1:]):
            table.cell(i + 1, j).text = str(value)
    
    return prs

# Streamlit UI
st.title("Database PowerPoint Generator")

# Table selection
tables = ["customers", "employees", "offices", "orderdetails", 
          "orders", "payments", "productlines", "products"]
selected_table = st.selectbox("Select a table", tables)

# Generate button
if st.button("Generate PowerPoint"):
    try:
        with st.spinner("Generating PowerPoint..."):
            # Get data from selected table
            data = get_table_data(selected_table)
            
            # Generate presentation
            prs = generate_slides(selected_table, data)
            
            # Save presentation
            output_file = f"{selected_table}_report.pptx"
            prs.save(output_file)
            
            st.success(f"PowerPoint generated successfully! Saved as {output_file}")
            
            # Add download button
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download PowerPoint",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")