import sqlite3
import os

db_path = r"C:\Users\DELL pro\.gemini\antigravity\scratch\centra-med-app\centra_med.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

try:
    c.execute("ALTER TABLE production_records ADD COLUMN low_prod_reason TEXT;")
    print("Added low_prod_reason")
except Exception as e:
    print(e)

try:
    c.execute("ALTER TABLE production_records ADD COLUMN high_waste_reason TEXT;")
    print("Added high_waste_reason")
except Exception as e:
    print(e)

conn.commit()
conn.close()
