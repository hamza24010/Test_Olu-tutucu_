import sqlite3
import os

class DBManager:
    def __init__(self, db_path='data/test_olusturucu.db'):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def add_question(self, text, image_path, category=None, difficulty=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO questions (text, image_path, category, difficulty)
            VALUES (?, ?, ?, ?)
        ''', (text, image_path, category, difficulty))
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return question_id

    def get_all_questions(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions ORDER BY created_at DESC')
        questions = cursor.fetchall()
        conn.close()
        return questions

    def delete_question(self, question_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        conn.commit()
        conn.close()
