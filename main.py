from fastapi import FastAPI, HTTPException, UploadFile, File,Form

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import pandas as pd
import requests
import json
import os
from typing import Optional, List, Dict
from dashboard_utils import save_chart_to_dashboard, get_user_charts
from chart_utils import generate_chart

app = FastAPI(title="SQL Work Assistant")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database connection
DATABASE_PATH = "assistant.db"

class QueryRequest(BaseModel):
    question: str
    database_schema: Optional[str] = None

class DatabaseConnection(BaseModel):
    db_type: str
    connection_string: Optional[str] = None

# Free AI API configuration (using Groq - free tier)
GROQ_API_KEY = "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"
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set. Get a free key from console.groq.com")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_database_schema():
    """Get current database schema"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            schema[table_name] = [{"name": col[1], "type": col[2]} for col in columns]
        
        conn.close()
        return schema
    except Exception as e:
        return {}

def generate_sql_query(question: str, schema: dict) -> str:
    """Generate SQL query using free AI API"""
    
    # Prepare schema context
    schema_text = ""
    for table, columns in schema.items():
        cols = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
        schema_text += f"Table {table}: {cols}\n"
    
    prompt = f"""
    You are a SQL expert. Generate a SQL query based on the user's question.
    
    Database Schema:
    {schema_text}
    
    User Question: {question}
    
    Rules:
    1. Return only the SQL query, no explanations
    2. Use proper SQL syntax
    3. Handle both English and Hinglish inputs
    4. If question is in Hinglish, understand the intent
    
    SQL Query:
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3-8b-8192",  # Free model
            "messages": [
                {"role": "system", "content": "You are a SQL expert assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            sql_query = result['choices'][0]['message']['content'].strip()
            # Clean up the response
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            return sql_query
        else:
            # Fallback to simple pattern matching for common queries
            return generate_simple_query(question, schema)
            
    except Exception as e:
        return generate_simple_query(question, schema)

def generate_simple_query(question: str, schema: dict) -> str:
    """Fallback simple query generation"""
    question_lower = question.lower()
    
    # Get first table name as default
    table_name = list(schema.keys())[0] if schema else "your_table"
    
    if any(word in question_lower for word in ['show', 'display', 'get', 'fetch', 'dikhao', 'batao']):
        return f"SELECT * FROM {table_name} LIMIT 10;"
    elif any(word in question_lower for word in ['count', 'kitne', 'how many']):
        return f"SELECT COUNT(*) FROM {table_name};"
    elif any(word in question_lower for word in ['max', 'maximum', 'highest', 'sabse zyada']):
        # Try to find numeric column
        numeric_col = "id"  # default
        return f"SELECT MAX({numeric_col}) FROM {table_name};"
    else:
        return f"SELECT * FROM {table_name} LIMIT 10;"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/generate-query")
async def generate_query(request: QueryRequest):
    """Generate SQL query from natural language"""
    try:
        schema = get_database_schema()
        sql_query = generate_sql_query(request.question, schema)
        
        return {
            "success": True,
            "query": sql_query,
            "explanation": f"Generated query for: {request.question}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-query")
async def execute_query(query: dict):
    """Execute SQL query and return results"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(query["sql"])
        
        if query["sql"].strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append(dict(zip(columns, row)))
            
            conn.close()
            return {
                "success": True,
                "data": data,
                "columns": columns,
                "row_count": len(data)
            }
        else:
            conn.commit()
            conn.close()
            return {
                "success": True,
                "message": "Query executed successfully",
                "affected_rows": cursor.rowcount
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    try:
        print("Received file:", file.filename)
        file_location = f"static/uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        print("Saved file to:", file_location)
        # Read file content for debugging
        content = await file.read()
        print("File size:", len(content))

        # Rewind the file pointer for pandas
        file.file.seek(0)

        # Read CSV file
        df = pd.read_csv(file.file)
        print("DataFrame shape:", df.shape)

        # Create table name from filename
        table_name = file.filename.replace('.csv', '').replace(' ', '_')

        # Save to SQLite
        conn = sqlite3.connect(DATABASE_PATH)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()

        return {
            "success": True,
            "message": f"Data uploaded successfully to table '{table_name}'",
            "rows": len(df),
            "columns": list(df.columns)
        }
        
    except Exception as e:
        print("Error in upload-data:", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/schema")
async def get_schema():
    """Get database schema"""
    schema = get_database_schema()
    return {"schema": schema}

@app.post("/explain-query")
async def explain_query(query: dict):
    """Explain what a SQL query does"""
    try:
        prompt = f"""
        Explain this SQL query in simple terms (support both English and Hindi):
        
        {query['sql']}
        
        Provide a clear explanation of what this query does.
        """
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            explanation = result['choices'][0]['message']['content']
            return {"explanation": explanation}
        else:
            return {"explanation": "This query retrieves data from your database."}
            
    except Exception as e:
        return {"explanation": "Unable to explain query at the moment."}

@app.post("/generate-chart")
async def generate_chart_endpoint(
    file_name: str = Form(...),
    chart_type: str = Form(...),
    x_col: str = Form(...),
    y_col: str = Form(...),
    user_id: str = Form(...)
):
    try:
        # 🔍 Log the received data
        print("Received form data:")
        print("file_name:", file_name)
        print("chart_type:", chart_type)
        print("x_col:", x_col)
        print("y_col:", y_col)
        print("user_id:", user_id)

        # 🔍 Check file path existence
        filepath = f"static/uploads/{file_name}"
        print("Checking if file exists:", filepath)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found. Upload it first.")
        
        # 🔍 Load data and log a sample
        df = pd.read_csv(filepath)
        print("Dataframe head:\n", df.head())

        # 🔍 Generate chart
        chart_path = generate_chart(df, chart_type, x_col, y_col)
        print("Chart generated at:", chart_path)

        # 🔍 Save chart to dashboard
        save_chart_to_dashboard(user_id, f"{chart_type} chart of {y_col} by {x_col}", chart_path)
        print("Chart saved to dashboard for user:", user_id)

        return {"success": True, "chart_url": chart_path}
    except Exception as e:
        print("Error in /generate-chart:", str(e))  # 🔍 Log the error
        raise HTTPException(status_code=400, detail=str(e))

# Get user dashboard
@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    try:
        charts = get_user_charts(user_id)
        return {"success": True, "charts": charts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
