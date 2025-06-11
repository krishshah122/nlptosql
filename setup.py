

import sqlite3
import os

def setup_database():
    """Initialize the database"""
    conn = sqlite3.connect('assistant.db')
    cursor = conn.cursor()
    
    # Create a sample table for demonstration
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sample_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER,
            city TEXT,
            salary REAL
        )
    ''')
    
    # Insert sample data
    sample_data = [
        (1, 'Rahul Sharma', 'rahul@email.com', 28, 'Mumbai', 75000),
        (2, 'Priya Singh', 'priya@email.com', 25, 'Delhi', 65000),
        (3, 'Amit Kumar', 'amit@email.com', 32, 'Bangalore', 85000),
        (4, 'Sneha Patel', 'sneha@email.com', 29, 'Pune', 70000),
        (5, 'Vikash Gupta', 'vikash@email.com', 35, 'Chennai', 90000)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO sample_users (id, name, email, age, city, salary)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
