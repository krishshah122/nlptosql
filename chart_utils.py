import plotly.express as px
import pandas as pd
import os

def generate_chart(data: pd.DataFrame, chart_type: str, x_col: str, y_col: str) -> str:
    """
    Generates a chart and saves it as an interactive HTML file.
    """
    if chart_type == "bar":
        fig = px.bar(data, x=x_col, y=y_col, title=f"Bar chart of {y_col} by {x_col}")
    elif chart_type == "pie":
        fig = px.pie(data, names=x_col, values=y_col, title=f"Pie chart of {y_col} by {x_col}")
    elif chart_type == "line":
        fig = px.line(data, x=x_col, y=y_col, title=f"Line chart of {y_col} over {x_col}")
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    # Save chart to static folder
    chart_folder = "static/charts"
    os.makedirs(chart_folder, exist_ok=True)
    chart_file = f"{chart_folder}/{chart_type}_{x_col}_{y_col}.html"
    fig.write_html(chart_file)
    
    return f"/{chart_file}"
