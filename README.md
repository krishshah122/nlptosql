# SQL Work Assistant

A web-based tool that allows you to query your database using natural language (English or Hinglish). It uses a FastAPI backend, Groq's Llama3 model for text-to-SQL conversion, and a simple HTML/CSS/JS frontend.

## Features

- **Natural Language to SQL**: Ask questions in English or Hinglish, and get the corresponding SQL query.
- **CSV Data Upload**: Upload a CSV file to automatically create a SQLite table from it.
- **Query Execution**: Execute the generated SQL query directly from the web interface.
- **Query Explanation**: Get a simple explanation of what a SQL query does.
- **Chart Generation**: Generate bar, pie, or line charts based on your data using Plotly.
- **User Dashboard**: Save and view your generated charts on a personalized dashboard.

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **AI Integration**: Groq API (Llama3-8b for SQL generation, Mixtral-8x7b for explanations)
- **Data Processing**: Pandas, Plotly

## Project Structure

- `main.py`: The FastAPI application containing all the endpoints.
- `setup.py`: Script to initialize the SQLite database (`assistant.db`) with sample data.
- `chart_utils.py` & `dashboard_utils.py`: Utilities for generating charts and managing user dashboards.
- `static/`: Contains the frontend assets (`index.html`, `style.css`, `script.js`) and uploaded files.

## Installation & Setup

1. **Install Dependencies**:
   Ensure you have Python installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the Database**:
   Run the setup script to initialize the SQLite database with sample data:
   ```bash
   python setup.py
   ```

3. **Configure the API Key**:
   In `main.py`, locate the `GROQ_API_KEY` variable and replace `"Your Api key"` with your actual Groq API key (you can get one for free at console.groq.com).

4. **Run the Application**:
   Start the FastAPI development server:
   ```bash
   python -m uvicorn main:app --reload
   ```

5. **Access the Web Interface**:
   Open your browser and navigate to `http://127.0.0.1:8000`.
