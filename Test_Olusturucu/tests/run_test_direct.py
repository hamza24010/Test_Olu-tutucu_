import os
import sqlite3
from src.db.db_manager import DBManager

def test_schema_migration_and_data():
    # Use a temporary DB
    db_path = "tests/test_classification.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize DB (triggers migration)
    db = DBManager(db_path)
    
    # Verify schema
    conn = db._get_connection()
    c = conn.cursor()
    c.execute("PRAGMA table_info(questions)")
    columns = [row[1] for row in c.fetchall()]
    conn.close()
    
    print(f"Columns found: {columns}")
    
    if "subject" not in columns: print("FAIL: subject missing")
    if "grade_level" not in columns: print("FAIL: grade_level missing")
    if "difficulty" not in columns: print("FAIL: difficulty missing")
    
    # Insert data
    q_id = db.add_question(
        text="Simulated question",
        image_path="path/to/img.png",
        subject="Matematik",
        grade_level="9. Sınıf",
        difficulty=3
    )
    
    # Retrieve
    questions = db.get_all_questions()
    if len(questions) != 1: print("FAIL: Question count mismatch")
    
    q = questions[0]
    print(f"Question Row: {q}")
    
    # Verify data presence
    if "Matematik" not in q: print("FAIL: Subject data missing")
    if "9. Sınıf" not in q: print("FAIL: Grade data missing")
    if 3 not in q: print("FAIL: Difficulty data missing") # Check integer 3
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    print("Test Complete")

if __name__ == "__main__":
    try:
        test_schema_migration_and_data()
    except Exception as e:
        print(f"Test Failed with error: {e}")
