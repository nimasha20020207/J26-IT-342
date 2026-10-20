import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, 'database', 'venture_users.db')

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight_kg REAL NOT NULL,
            height_cm REAL NOT NULL,
            resting_hr INTEGER NOT NULL,
            experience_level TEXT NOT NULL,
            has_medical_issue INTEGER NOT NULL,
            medical_notes TEXT,
            preferred_max_hours REAL NOT NULL,
            preferred_scenic TEXT NOT NULL,
            fitness_level TEXT NOT NULL,
            fitness_source TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_registered_user():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "registered": True,
        "name": row["name"],
        "email": row["email"],
        "age": int(row["age"]),
        "weight_kg": float(row["weight_kg"]),
        "height_cm": float(row["height_cm"]),
        "resting_hr": int(row["resting_hr"]),
        "experience_level": row["experience_level"],
        "has_medical_issue": bool(row["has_medical_issue"]),
        "medical_notes": row["medical_notes"] or "None",
        "preferred_max_hours": float(row["preferred_max_hours"]),
        "preferred_scenic": json.loads(row["preferred_scenic"]),
        "fitness_level": row["fitness_level"],
        "fitness_source": row["fitness_source"]
    }