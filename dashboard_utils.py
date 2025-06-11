import sqlite3

DATABASE_PATH = "assistant.db"

def save_chart_to_dashboard(user_id: str, chart_name: str, chart_path: str, notes: str = ""):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            chart_name TEXT,
            chart_path TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO user_charts (user_id, chart_name, chart_path, notes)
        VALUES (?, ?, ?, ?)
    """, (user_id, chart_name, chart_path, notes))
    conn.commit()
    conn.close()

def get_user_charts(user_id: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chart_name, chart_path, notes, created_at FROM user_charts
        WHERE user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
