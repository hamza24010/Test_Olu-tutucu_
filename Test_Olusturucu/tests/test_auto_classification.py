import pytest
import os
import sqlite3
from src.db.db_manager import DBManager

class TestAutoClassification:
    def test_schema_migration_and_data(self):
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
        
        assert "subject" in columns
        assert "grade_level" in columns
        assert "difficulty" in columns
        
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
        assert len(questions) == 1
        q = questions[0]
        
        print(f"Question Row: {q}")
        
        # Verify data presence
        assert "Matematik" in q
        assert "9. Sınıf" in q
        assert 3 in q
        
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
