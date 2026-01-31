import sqlite3
import os

from .init_db import init_db

class DBManager:
    def __init__(self, db_path='data/test_olusturucu.db'):
        self.db_path = db_path
        init_db(self.db_path)
        self._migrate_schema()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _migrate_schema(self):
        """Ensures the database schema has all required columns."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Check existing columns
            cursor.execute("PRAGMA table_info(questions)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'subject' not in columns:
                cursor.execute("ALTER TABLE questions ADD COLUMN subject TEXT")
            if 'grade_level' not in columns:
                cursor.execute("ALTER TABLE questions ADD COLUMN grade_level TEXT")
            # difficulty exists in original code's INSERT, but ensuring it won't hurt if table was old
            if 'difficulty' not in columns:
                cursor.execute("ALTER TABLE questions ADD COLUMN difficulty INTEGER")
            
            conn.commit()
        except Exception as e:
            print(f"Schema migration error: {e}")
        finally:
            conn.close()

    def add_question(self, text, image_path, subject=None, grade_level=None, difficulty=None, category=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        # Use subject as category if not provided, for backward compatibility logic
        final_category = category if category else subject
        
        cursor.execute('''
            INSERT INTO questions (text, image_path, category, difficulty, subject, grade_level)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (text, image_path, final_category, difficulty, subject, grade_level))
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return question_id

    def get_all_questions(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions ORDER BY created_at DESC, id DESC')
        questions = cursor.fetchall()
        conn.close()
        return questions

    def delete_question(self, question_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        conn.commit()
        conn.close()

    def delete_all_questions(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM questions')
        conn.commit()
        conn.close()
