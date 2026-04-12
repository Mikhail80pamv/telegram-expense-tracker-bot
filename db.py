import sqlite3
from datetime import datetime, timedelta

DB_NAME = "expenses.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_expense(user_id: int, amount: float, category: str):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)",
            (user_id, amount, category)
        )
        conn.commit()

def get_stats(user_id: int, days: int = 7):
    since_date = datetime.now() - timedelta(days=days)
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT category, SUM(amount) FROM expenses
            WHERE user_id = ? AND created_at >= ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """, (user_id, since_date))
        return cur.fetchall()