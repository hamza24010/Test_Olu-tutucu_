use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;
use std::sync::Mutex;
use tauri::Manager;
use tauri::Emitter;

pub mod db;
use db::{Database, Question, Template};

// App State to hold Database connection
struct AppState {
    db: Mutex<Database>,
}

// Sidecar komutu (AI Analiz)
#[tauri::command]
async fn analyze_pdf(app: tauri::AppHandle, state: tauri::State<'_, AppState>, path: String) -> Result<(), String> {
    let api_key = {
        let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
        db.get_setting("gemini_api_key").map_err(|e| e.to_string())?.unwrap_or_default()
    };

    let sidecar_command = app.shell().sidecar("engine").map_err(|e| e.to_string())?;
    
    let (mut rx, _) = sidecar_command
        .args(&[&path])
        .env("GEMINI_API_KEY", &api_key)
        .spawn()
        .map_err(|e| e.to_string())?;

    let app_handle = app.clone();
    
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            if let CommandEvent::Stdout(line) = event {
                let line_str = String::from_utf8_lossy(&line);
                // Emit event to frontend
                if let Err(e) = app_handle.emit("analysis-event", line_str.to_string()) {
                    eprintln!("Failed to emit event: {}", e);
                }
            }
        }
    });

    Ok(())
}

// TEMPLATE: AI Analiz
#[tauri::command]
async fn analyze_template(app: tauri::AppHandle, state: tauri::State<'_, AppState>, path: String) -> Result<String, String> {
    let api_key = {
        let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
        db.get_setting("gemini_api_key").map_err(|e| e.to_string())?.unwrap_or_default()
    };

    let sidecar_command = app.shell().sidecar("engine").map_err(|e| e.to_string())?;
    
    // Command format: engine analyze-template <path>
    let (mut rx, _) = sidecar_command
        .args(&["analyze-template", &path])
        .env("GEMINI_API_KEY", &api_key)
        .spawn()
        .map_err(|e| e.to_string())?;

    let mut output = String::new();
    
    while let Some(event) = rx.recv().await {
        if let CommandEvent::Stdout(line) = event {
            let line_str = String::from_utf8_lossy(&line);
             output.push_str(&line_str);
        }
    }
    Ok(output)
}

#[tauri::command]
async fn save_setting(state: tauri::State<'_, AppState>, key: String, value: String) -> Result<(), String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.set_setting(&key, &value).map_err(|e| e.to_string())
}

#[tauri::command]
async fn get_setting(state: tauri::State<'_, AppState>, key: String) -> Result<Option<String>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.get_setting(&key).map_err(|e| e.to_string())
}



// Save Question Command
#[tauri::command]
async fn save_question(
    state: tauri::State<'_, AppState>,
    text: String,
    image: String,
    base64: String,
    pdf: String,
    page: i32,
    difficulty: Option<i32>,
    topic: Option<String>
) -> Result<i64, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    
    let q = Question {
        id: None,
        text,
        image_path: image,
        image_base64: Some(base64),
        subject: None,
        source_pdf: Some(pdf),
        page_number: Some(page),
        difficulty: difficulty.or(Some(3)),
        topic: topic.or(None),
    };
    
    db.insert_question(&q).map_err(|e| e.to_string())
}

// List Questions Command
#[tauri::command]
async fn list_questions(state: tauri::State<'_, AppState>) -> Result<Vec<Question>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.get_all_questions().map_err(|e| e.to_string())
}

// EXPORT PDF
#[tauri::command]
async fn export_test_pdf(
    app: tauri::AppHandle, 
    state: tauri::State<'_, AppState>,
    image_paths: Vec<String>, 
    output_path: String, 
    template_path: Option<String>,
    margins: Option<String>
) -> Result<String, String> {
    let api_key = {
        let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
        db.get_setting("gemini_api_key").map_err(|e| e.to_string())?.unwrap_or_default()
    };
    
    let sidecar_command = app.shell().sidecar("engine").map_err(|e| e.to_string())?;
    
    // Construct args: ["export", output_path, "--images", img1, img2, ...]
    let mut args = vec!["export".to_string(), output_path];
    args.push("--images".to_string());
    args.extend(image_paths);

    if let Some(tpl) = template_path {
        args.push("--template".to_string());
        args.push(tpl);
    }
    
    if let Some(m) = margins {
        args.push("--margins".to_string());
        args.push(m);
    }

    // Convert to ref slice
    let args_str: Vec<&str> = args.iter().map(|s| s.as_str()).collect();

    let (mut rx, _) = sidecar_command
        .args(&args_str)
        .env("GEMINI_API_KEY", &api_key)
        .spawn()
        .map_err(|e| e.to_string())?;

    let mut output = String::new();
    while let Some(event) = rx.recv().await {
        if let CommandEvent::Stdout(line) = event {
            output.push_str(&String::from_utf8_lossy(&line));
        }
    }
    Ok(output)
}

#[tauri::command]
async fn delete_question(state: tauri::State<'_, AppState>, id: i32) -> Result<(), String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.delete_question(id).map_err(|e| e.to_string())
}

#[tauri::command]
async fn delete_questions(state: tauri::State<'_, AppState>, ids: Vec<i32>) -> Result<(), String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.delete_questions(ids).map_err(|e| e.to_string())
}

// --- TEMPLATE CRUD ---
#[tauri::command]
async fn save_template(state: tauri::State<'_, AppState>, name: String, path: String, preview: String, margins: String) -> Result<i64, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    let t = Template { id: None, name, path, preview_image: Some(preview), margins_json: margins };
    db.save_template(&t).map_err(|e| e.to_string())
}

#[tauri::command]
async fn list_templates(state: tauri::State<'_, AppState>) -> Result<Vec<Template>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.get_templates().map_err(|e| e.to_string())
}

#[tauri::command]
async fn delete_template(state: tauri::State<'_, AppState>, id: i32) -> Result<(), String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.delete_template(id).map_err(|e| e.to_string())
}

#[tauri::command]
async fn update_template(state: tauri::State<'_, AppState>, id: i32, name: String, margins: String) -> Result<(), String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.update_template(id, name, margins).map_err(|e| e.to_string())
}

// --- STUDENT COMMANDS ---

#[tauri::command]
async fn add_student(state: tauri::State<'_, AppState>, name: String) -> Result<i64, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.add_student(name).map_err(|e| e.to_string())
}

#[tauri::command]
async fn list_students(state: tauri::State<'_, AppState>) -> Result<Vec<(i32, String)>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.list_students().map_err(|e| e.to_string())
}

#[tauri::command]
async fn delete_student(state: tauri::State<'_, AppState>, id: i32) -> Result<(), String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.delete_student(id).map_err(|e| e.to_string())
}

#[tauri::command]
async fn mark_test_solved(state: tauri::State<'_, AppState>, student_id: i32, question_ids: Vec<i32>) -> Result<(), String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.mark_test_solved(student_id, question_ids).map_err(|e| e.to_string())
}

// --- ARCHIVE COMMANDS ---

#[tauri::command]
async fn save_test_record(state: tauri::State<'_, AppState>, student_id: Option<i32>, question_ids: Vec<i32>) -> Result<i64, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.save_test(student_id, question_ids).map_err(|e| e.to_string())
}

#[tauri::command]
async fn list_tests(state: tauri::State<'_, AppState>) -> Result<Vec<(i32, String, Option<String>, i32)>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.list_tests().map_err(|e| e.to_string())
}

#[tauri::command]
async fn get_test_questions(state: tauri::State<'_, AppState>, test_id: i32) -> Result<Vec<Question>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.get_test_questions(test_id).map_err(|e| e.to_string())
}

#[tauri::command]
async fn generate_answer_key(app: tauri::AppHandle, state: tauri::State<'_, AppState>, test_id: i32) -> Result<String, String> {
    // 1. Check existing key
    {
        let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
        if let Ok(Some(key)) = db.get_test_answer_key(test_id) {
            return Ok(key);
        }
    }

    // 2. Fetch Questions
    let questions = {
        let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
        db.get_test_questions(test_id).map_err(|e| e.to_string())?
    };

    if questions.is_empty() {
        return Err("Testte soru yok".to_string());
    }

    // 3. Prepare JSON for Python
    #[derive(serde::Serialize)]
    struct SolverQ {
        id: i32,
        text: String,
        image_path: Option<String>
    }

    let solver_data: Vec<SolverQ> = questions.iter().map(|q| SolverQ {
        id: q.id.unwrap_or(0),
        text: q.text.clone(),
        image_path: if q.image_path.is_empty() { None } else { Some(q.image_path.clone()) }
    }).collect();

    let json_str = serde_json::to_string(&solver_data).map_err(|e| e.to_string())?;

    // 4. Run Python Solver
    let api_key = {
        let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
        db.get_setting("gemini_api_key").map_err(|e| e.to_string())?.unwrap_or_default()
    };

    let sidecar_command = app.shell().sidecar("engine").map_err(|e| e.to_string())?;
    
    let output = sidecar_command
        .args(&[
            "solve", 
            "--questions", 
            &json_str
        ])
        .env("GEMINI_API_KEY", &api_key)
        .output()
        .await
        .map_err(|e| format!("Python (Sidecar) hatası: {}", e))?;

    if !output.status.success() {
        let err = String::from_utf8_lossy(&output.stderr);
        return Err(format!("AI Çözüm hatası: {}", err));
    }

    let result_json = String::from_utf8_lossy(&output.stdout).to_string();

    // 5. Save and Return
    {
        let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
        db.save_test_answer_key(test_id, result_json.clone()).map_err(|e| e.to_string())?;
    }

    Ok(result_json)
}

// --- GENERATOR COMMANDS ---

#[tauri::command]
async fn get_topics(state: tauri::State<'_, AppState>) -> Result<Vec<String>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.get_unique_topics().map_err(|e| e.to_string())
}

#[tauri::command]
async fn generate_test(
    state: tauri::State<'_, AppState>,
    topic: Option<String>,
    difficulty: Option<i32>,
    count: i32,
    student_id: Option<i32> // Added
) -> Result<Vec<Question>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.get_random_questions(topic, difficulty, count, student_id).map_err(|e| e.to_string())
}


#[derive(serde::Serialize)]
struct PaginatedResponse {
    questions: Vec<Question>,
    total: i32,
}

#[tauri::command]
async fn list_questions_paginated(
    state: tauri::State<'_, AppState>,
    page: i32,
    limit: i32,
    search: String,
    topic: Option<String>,
    difficulty: Option<i32>
) -> Result<PaginatedResponse, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    let (questions, total) = db.get_questions_paginated(page, limit, search, topic, difficulty)
        .map_err(|e| e.to_string())?;
    
    Ok(PaginatedResponse { questions, total })
}

#[tauri::command]
async fn get_questions_by_ids(state: tauri::State<'_, AppState>, ids: Vec<i32>) -> Result<Vec<Question>, String> {
    let db = state.db.lock().map_err(|_| "Failed to lock DB".to_string())?;
    db.get_questions_by_ids(ids).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init()) 
        .plugin(tauri_plugin_fs::init()) 
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            // Initialize DB in App Data Directory
            let app_handle = app.handle();
            let app_data_dir = app_handle.path().app_data_dir().unwrap();
            
            // Create dir if not exists
            if !app_data_dir.exists() {
                std::fs::create_dir_all(&app_data_dir).unwrap();
            }
            
            let db_path = app_data_dir.join("stitch.db");
            let db = Database::new(db_path.to_str().unwrap()).expect("Failed to init DB");
            db.init().expect("Failed to create tables");
            
            app.manage(AppState {
                db: Mutex::new(db),
            });
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            analyze_pdf,
            save_question,
            list_questions,
            list_questions_paginated,
            delete_question,
            get_questions_by_ids,
            delete_questions,
            export_test_pdf,
            analyze_template,
            save_template,
            list_templates,
            delete_template,
            update_template,
            // Student
            add_student,
            list_students,
            delete_student,
            mark_test_solved,
            // Archive
            save_test_record,
            list_tests,
            get_test_questions,
            generate_answer_key,
            get_setting,
            save_setting,
            // Generator
            get_topics,
            generate_test
        ]) 
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
