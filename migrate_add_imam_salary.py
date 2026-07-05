import sqlite3

# Connect to the database
db_path = "instance/mosque.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column exists by trying to query it
    cursor.execute("PRAGMA table_info(member)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "imam_salary_contri" in columns:
        print("✓ Column imam_salary_contri already exists!")
    else:
        # Add the column to the member table
        cursor.execute("ALTER TABLE member ADD COLUMN imam_salary_contri REAL DEFAULT 0.0")
        conn.commit()
        print("✓ Column imam_salary_contri added successfully!")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()

