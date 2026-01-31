use rusqlite::{params, Connection, Result};
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Question {
    pub id: Option<i32>,
    pub text: String,
    pub image_path: String,
    pub image_base64: Option<String>,
    pub subject: Option<String>,
    pub source_pdf: Option<String>,
    pub page_number: Option<i32>,
    pub difficulty: Option<i32>,
    pub topic: Option<String>,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub struct Template {
    pub id: Option<i32>,
    pub name: String,
    pub path: String,
    pub preview_image: Option<String>, // Base64
    pub margins_json: String, // stored as json string
}

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        Ok(Database { conn })
    }

    pub fn init(&self) -> Result<()> {
        // Main Questions Table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                image_path TEXT,
                image_base64 TEXT,
                subject TEXT,
                source_pdf TEXT,
                page_number INTEGER,
                difficulty INTEGER,
                topic TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;
        
        // Templates Table
        self.conn.execute(
             "CREATE TABLE IF NOT EXISTS user_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                preview_image TEXT NOT NULL,
                margins_json TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;

        // Students Table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;

        // Solved Relations
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS student_solved_questions (
                student_id INTEGER,
                question_id INTEGER,
                solved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (student_id, question_id),
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE
            )",
            [],
        )?;

        // Tests History
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE SET NULL
            )",
            [],
        )?;

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS test_questions (
                test_id INTEGER,
                question_id INTEGER,
                FOREIGN KEY(test_id) REFERENCES tests(id) ON DELETE CASCADE,
                FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE
            )",
            [],
        )?;
        
        // MIGRATIONS
        let _ = self.conn.execute("ALTER TABLE questions ADD COLUMN difficulty INTEGER", []);
        let _ = self.conn.execute("ALTER TABLE questions ADD COLUMN topic TEXT", []);
        let _ = self.conn.execute("ALTER TABLE tests ADD COLUMN answer_key TEXT", []); // New Migration
        
        Ok(())
    }

    // --- ARCHIVE / TESTS ---
    pub fn save_test(&self, student_id: Option<i32>, question_ids: Vec<i32>) -> Result<i64> {
        let name = format!("Test - {}", chrono::Local::now().format("%Y-%m-%d %H:%M"));
        
        self.conn.execute(
            "INSERT INTO tests (student_id, name) VALUES (?1, ?2)",
            params![student_id, name]
        )?;
        
        let test_id = self.conn.last_insert_rowid();

        for q_id in question_ids {
            self.conn.execute(
                "INSERT INTO test_questions (test_id, question_id) VALUES (?1, ?2)",
                params![test_id, q_id]
            )?;
        }
        Ok(test_id)
    }

    pub fn list_tests(&self) -> Result<Vec<(i32, String, Option<String>, i32)>> {
        // Returns: id, date, student_name, question_count
        let mut stmt = self.conn.prepare(
            "SELECT t.id, t.created_at, s.name, COUNT(tq.question_id) 
             FROM tests t
             LEFT JOIN students s ON t.student_id = s.id
             LEFT JOIN test_questions tq ON t.id = tq.test_id
             GROUP BY t.id
             ORDER BY t.created_at DESC"
        )?;

        let iter = stmt.query_map([], |row| {
             let date: String = row.get(1)?;
             let s_name: Option<String> = row.get(2)?;
             let count: i32 = row.get(3)?;
             Ok((row.get(0)?, date, s_name, count))
        })?;

        let mut tests = Vec::new();
        for t in iter { tests.push(t?); }
        Ok(tests)
    }

    pub fn get_test_questions(&self, test_id: i32) -> Result<Vec<Question>> {
        let mut stmt = self.conn.prepare(
            "SELECT q.id, q.text, q.image_path, q.image_base64, q.subject, q.source_pdf, q.page_number, q.difficulty, q.topic 
             FROM questions q
             INNER JOIN test_questions tq ON q.id = tq.question_id
             WHERE tq.test_id = ?1"
        )?;
        
        let iter = stmt.query_map(params![test_id], |row| Self::map_row(row))?;
        let mut questions = Vec::new();
        for q in iter { questions.push(q?); }
        Ok(questions)
    }

    pub fn get_test_answer_key(&self, test_id: i32) -> Result<Option<String>> {
        let mut stmt = self.conn.prepare("SELECT answer_key FROM tests WHERE id = ?1")?;
        let mut rows = stmt.query(params![test_id])?;
        
        if let Some(row) = rows.next()? {
            let key: Option<String> = row.get(0)?;
            Ok(key)
        } else {
            Ok(None)
        }
    }

    pub fn save_test_answer_key(&self, test_id: i32, key: String) -> Result<()> {
        self.conn.execute(
            "UPDATE tests SET answer_key = ?1 WHERE id = ?2",
            params![key, test_id]
        )?;
        Ok(())
    }

    // --- STUDENTS ---
    pub fn add_student(&self, name: String) -> Result<i64> {
        self.conn.execute("INSERT INTO students (name) VALUES (?1)", params![name])?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn list_students(&self) -> Result<Vec<(i32, String)>> {
        let mut stmt = self.conn.prepare("SELECT id, name FROM students ORDER BY name ASC")?;
        let iter = stmt.query_map([], |row| Ok((row.get(0)?, row.get(1)?)))?;
        let mut students = Vec::new();
        for s in iter { students.push(s?); }
        Ok(students)
    }

    pub fn delete_student(&self, id: i32) -> Result<()> {
        self.conn.execute("DELETE FROM students WHERE id = ?1", params![id])?;
        Ok(())
    }

    pub fn mark_test_solved(&self, student_id: i32, question_ids: Vec<i32>) -> Result<()> {
        for q_id in question_ids {
            // IGNORE prevents error if already exists
            self.conn.execute(
                "INSERT OR IGNORE INTO student_solved_questions (student_id, question_id) VALUES (?1, ?2)",
                params![student_id, q_id]
            )?;
        }
        Ok(())
    }

    // --- Template Methods ---
    pub fn save_template(&self, t: &Template) -> Result<i64> {
         self.conn.execute(
            "INSERT INTO user_templates (name, path, preview_image, margins_json)
             VALUES (?1, ?2, ?3, ?4)",
            params![t.name, t.path, t.preview_image, t.margins_json],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn update_template(&self, id: i32, name: String, margins_json: String) -> Result<()> {
        self.conn.execute(
            "UPDATE user_templates SET name = ?1, margins_json = ?2 WHERE id = ?3",
            params![name, margins_json, id],
        )?;
        Ok(())
    }

    pub fn get_templates(&self) -> Result<Vec<Template>> {
        let mut stmt = self.conn.prepare("SELECT id, name, path, preview_image, margins_json FROM user_templates ORDER BY created_at DESC")?;
        let iter = stmt.query_map([], |row| {
            Ok(Template {
                id: row.get(0)?,
                name: row.get(1)?,
                path: row.get(2)?,
                preview_image: row.get(3)?,
                margins_json: row.get(4)?,
            })
        })?;
        
        let mut templates = Vec::new();
        for t in iter {
            templates.push(t?);
        }
        Ok(templates)
    }

    pub fn delete_template(&self, id: i32) -> Result<()> {
        self.conn.execute("DELETE FROM user_templates WHERE id = ?1", params![id])?;
        Ok(())
    }

    // --- Question Methods ---
    pub fn insert_question(&self, q: &Question) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO questions (text, image_path, image_base64, subject, source_pdf, page_number, difficulty, topic)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                q.text,
                q.image_path,
                q.image_base64,
                q.subject,
                q.source_pdf,
                q.page_number,
                q.difficulty,
                q.topic
    ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn get_questions_paginated(
        &self, 
        page: i32, 
        limit: i32, 
        search: String, 
        topic: Option<String>, 
        difficulty: Option<i32>
    ) -> Result<(Vec<Question>, i32)> {
        let offset = (page - 1) * limit;
        
        let mut query = String::from("SELECT id, text, image_path, image_base64, subject, source_pdf, page_number, difficulty, topic FROM questions WHERE 1=1");
        let mut count_query = String::from("SELECT COUNT(*) FROM questions WHERE 1=1");
        
        let mut final_params: Vec<Box<dyn rusqlite::ToSql>> = Vec::new();
        
        if !search.is_empty() {
            query.push_str(" AND (text LIKE ? OR topic LIKE ?)");
            count_query.push_str(" AND (text LIKE ? OR topic LIKE ?)");
            let s = format!("%{}%", search);
            final_params.push(Box::new(s.clone())); // for text
            final_params.push(Box::new(s));         // for topic
        }
        
        if let Some(t) = &topic {
            query.push_str(" AND topic = ?");
            count_query.push_str(" AND topic = ?");
            final_params.push(Box::new(t.clone()));
        }
        
        if let Some(d) = difficulty {
            query.push_str(" AND difficulty = ?");
            count_query.push_str(" AND difficulty = ?");
            final_params.push(Box::new(d));
        }

        // Count Query Execution
        let mut stmt_count = self.conn.prepare(&count_query)?;
        let total: i32 = stmt_count.query_row(
            rusqlite::params_from_iter(final_params.iter().map(|p| p.as_ref())), 
            |row| row.get(0)
        )?;

        // Add Limit/Offset for Main Query
        query.push_str(" ORDER BY created_at DESC LIMIT ? OFFSET ?");
        final_params.push(Box::new(limit));
        final_params.push(Box::new(offset));

        let mut stmt = self.conn.prepare(&query)?;
        let rows = stmt.query_map(
            rusqlite::params_from_iter(final_params.iter().map(|p| p.as_ref())), 
            |row| Self::map_row(row)
        )?;

        let mut questions = Vec::new();
        for r in rows {
            questions.push(r?);
        }

        Ok((questions, total))
    }

    pub fn get_all_questions(&self) -> Result<Vec<Question>> {
        let mut stmt = self.conn.prepare("SELECT id, text, image_path, image_base64, subject, source_pdf, page_number, difficulty, topic FROM questions ORDER BY created_at DESC")?;
        
        let question_iter = stmt.query_map([], |row| {
            Ok(Question {
                id: row.get(0)?,
                text: row.get(1)?,
                image_path: row.get(2)?,
                image_base64: row.get(3)?,
                subject: row.get(4)?,
                source_pdf: row.get(5)?,
                page_number: row.get(6)?,
                difficulty: row.get(7).unwrap_or(Some(3)), // Default logic if null
                topic: row.get(8).unwrap_or(None),
            })
        })?;

        let mut questions = Vec::new();
        for q in question_iter {
            questions.push(q?);
        }
        Ok(questions)
    }
    
    pub fn get_questions_by_ids(&self, ids: Vec<i32>) -> Result<Vec<Question>> {
        if ids.is_empty() { return Ok(Vec::new()); }
        
        // Dynamically build "id IN (?,?,?)"
        // Since rusqlite 0.29+, we can user rarray with "feature = array" but standard approach:
        let placeholders: Vec<String> = ids.iter().map(|_| "?".to_string()).collect();
        let query = format!(
            "SELECT id, text, image_path, image_base64, subject, source_pdf, page_number, difficulty, topic 
             FROM questions WHERE id IN ({}) ORDER BY created_at DESC", 
            placeholders.join(",")
        );
        
        let mut stmt = self.conn.prepare(&query)?;
        
        // Convert ids to params
        let params: Vec<&dyn rusqlite::ToSql> = ids.iter().map(|id| id as &dyn rusqlite::ToSql).collect();
        
        let rows = stmt.query_map(rusqlite::params_from_iter(params), |row| Self::map_row(row))?;
        
        let mut questions = Vec::new();
        for r in rows {
            questions.push(r?);
        }
        Ok(questions)
    }

    pub fn get_unique_topics(&self) -> Result<Vec<String>> {
        let mut stmt = self.conn.prepare("SELECT DISTINCT topic FROM questions WHERE topic IS NOT NULL AND topic != '' ORDER BY topic ASC")?;
        let rows = stmt.query_map([], |row| row.get(0))?;
        
        let mut topics = Vec::new();
        for r in rows {
            topics.push(r?);
        }
        Ok(topics)
    }

    pub fn get_random_questions(&self, topic: Option<String>, difficulty: Option<i32>, count: i32, student_id: Option<i32>) -> Result<Vec<Question>> {
        let mut sql = String::from("SELECT id, text, image_path, image_base64, subject, source_pdf, page_number, difficulty, topic FROM questions WHERE 1=1");
        let mut params: Vec<Box<dyn rusqlite::ToSql>> = Vec::new();

        if let Some(t) = &topic {
            sql.push_str(" AND topic = ?");
            params.push(Box::new(t.clone()));
        }

        if let Some(d) = difficulty {
            sql.push_str(" AND difficulty = ?");
            params.push(Box::new(d));
        }

        if let Some(sid) = student_id {
            sql.push_str(" AND id NOT IN (SELECT question_id FROM student_solved_questions WHERE student_id = ?)");
            params.push(Box::new(sid));
        }

        sql.push_str(" ORDER BY RANDOM() LIMIT ?");
        params.push(Box::new(count));

        let mut stmt = self.conn.prepare(&sql)?;
        
        let rows = stmt.query_map(
            rusqlite::params_from_iter(params.iter().map(|p| p.as_ref())), 
            |row| Self::map_row(row)
        )?;

        let mut questions = Vec::new();
        for r in rows {
            questions.push(r?);
        }
        Ok(questions)
    }

    fn map_row(row: &rusqlite::Row) -> rusqlite::Result<Question> {
        Ok(Question {
            id: row.get(0)?,
            text: row.get(1)?,
            image_path: row.get(2)?,
            image_base64: row.get(3)?,
            subject: row.get(4)?,
            source_pdf: row.get(5)?,
            page_number: row.get(6)?,
            difficulty: row.get(7).unwrap_or(Some(3)), 
            topic: row.get(8).unwrap_or(None),
        })
    }

    pub fn delete_question(&self, id: i32) -> Result<()> {
        self.conn.execute("DELETE FROM questions WHERE id = ?1", params![id])?;
        Ok(())
    }

    pub fn delete_questions(&self, ids: Vec<i32>) -> Result<()> {
        if ids.is_empty() { return Ok(()); }
        
        let placeholders: Vec<String> = ids.iter().map(|_| "?".to_string()).collect();
        let query = format!("DELETE FROM questions WHERE id IN ({})", placeholders.join(","));
        
        // Use params_from_iter for cleaner query logic with lists
        let params: Vec<&dyn rusqlite::ToSql> = ids.iter().map(|id| id as &dyn rusqlite::ToSql).collect();
        self.conn.execute(&query, &*params)?;
        Ok(())
    }
}
