import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# ඔයාගේ PostgreSQL Database විස්තර මෙතන දෙන්න
DB_HOST = "localhost"
DB_NAME = "hiking_db"
DB_USER = "postgres"
DB_PASS = "udula" # ඔයාගේ pgAdmin password එක

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL,
            weight_kg REAL NOT NULL,
            height_cm REAL NOT NULL,
            resting_hr INTEGER NOT NULL,
            experience_level VARCHAR(50) NOT NULL,
            has_medical_issue INTEGER NOT NULL,
            medical_notes TEXT,
            preferred_max_hours REAL NOT NULL,
            preferred_scenic TEXT NOT NULL,
            fitness_level VARCHAR(50) NOT NULL,
            fitness_source VARCHAR(50) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def get_registered_user():
    init_db()
    conn = get_db_connection()
    # RealDictCursor මගින් දත්ත Dictionary එකක් ලෙස ලබාගැනීමට පහසු කරයි
    cursor = conn.cursor(cursor_factory=RealDictCursor) 
    cursor.execute("SELECT * FROM user_profile LIMIT 1")
    row = cursor.fetchone()
    
    cursor.close()
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
        "preferred_scenic": json.loads(row["preferred_scenic"]) if isinstance(row["preferred_scenic"], str) else row["preferred_scenic"],
        "fitness_level": row["fitness_level"],
        "fitness_source": row["fitness_source"]
    }