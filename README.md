# Database Table Viewer and Visualization Tool

A Streamlit-based web application that allows users to connect to a MySQL database, view table data, and generate visualizations using LIDA (Language-based Interactive Data Analytics). The tool also supports exporting visualizations to PowerPoint presentations.

## Features

- MySQL database connection and management
- Interactive database and table selection
- Data visualization using LIDA and Seaborn
- Natural language query interface for generating charts
- Export capabilities to PowerPoint
- Session state management for seamless user experience

## Prerequisites

Before running the application, make sure you have the following:

- Python 3.7+
- MySQL Server installed and running
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Required Python Packages

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit
mysql-connector-python
lida
pillow
python-dotenv
openai
pandas
numpy
python-pptx
```

## Database Configuration

Update the `CONNECTION_STRING` in the code with your MySQL database credentials:

```python
CONNECTION_STRING = {
    "host": "127.0.0.1",  # Your database host
    "user": "your_username",  # Your database username
    "password": "your_password"  # Your database password
}
```

## Running the Application

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

## Usage Guide

1. Click "Step 1: Connect to Database" to establish a connection with your MySQL server
2. Select a database from the dropdown menu
3. Choose a table from the selected database
4. Click "View Table Data" to see the contents of the selected table
5. Enter a natural language query to generate visualizations (e.g., "Create a bar chart showing sales by category")
6. Click "Generate Visualization" to create the chart
7. Optionally, export the generated visualization to PowerPoint using the "Export to PowerPoint" button

## Example Queries

Here are some example visualization queries you can try:

- "Show me a bar chart of sales distribution"
- "Create a scatter plot comparing price and quantity"
- "Generate a pie chart showing category distribution"
- "Make a line graph showing trends over time"

## Troubleshooting

Common issues and solutions:

1. Database Connection Errors:
   - Verify that MySQL server is running
   - Check your database credentials
   - Ensure you have proper permissions

2. Visualization Generation Issues:
   - Verify your OpenAI API key is valid
   - Check if the query is clear and relevant to your data
   - Ensure the selected table has sufficient data

3. PowerPoint Export Issues:
   - Make sure you have write permissions in the directory
   - Verify that python-pptx is properly installed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT 

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualization powered by [LIDA](https://microsoft.github.io/lida/)
- Database connectivity using [MySQL Connector Python](https://dev.mysql.com/doc/connector-python/en/)