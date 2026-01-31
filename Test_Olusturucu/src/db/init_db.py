import sqlite3
import os

def init_db(db_path=None):
    if db_path is None:
        db_path = os.path.join('data', 'test_olusturucu.db')
        os.makedirs('data', exist_ok=True)
    elif db_path != ':memory:':
        # Create directory if path provided and not memory
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Soru tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            image_path TEXT,
            category TEXT,
            difficulty INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Test tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Test soruları tablosu (ilişki tablosu)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_questions (
            test_id INTEGER,
            question_id INTEGER,
            FOREIGN KEY(test_id) REFERENCES tests(id),
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Veritabanı başarıyla oluşturuldu: {db_path}")

if __name__ == "__main__":
    init_db()
