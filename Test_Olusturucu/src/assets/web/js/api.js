// api.js - API Wrapper for FastAPI Backend

const API_BASE = "/api";

async function fetchQuestions() {
    try {
        const response = await fetch(`${API_BASE}/questions`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return [];
    }
}

async function deleteQuestion(id) {
    try {
        const response = await fetch(`${API_BASE}/questions/${id}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        return result.status === 'success';
    } catch (error) {
        console.error('Delete error:', error);
        return false;
    }
}

async function uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload-pdf`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Upload failed');
        return await response.json();
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

async function generateTest(title, questionIds) {
    try {
        const response = await fetch(`${API_BASE}/generate-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title, question_ids: questionIds })
        });
        if (!response.ok) throw new Error('Generation failed');
        return await response.json();
    } catch (error) {
        console.error('Generation error:', error);
        throw error;
    }
}

function navigateTo(page) {
    // In FastAPI, pages are served at root routes like /question_bank.html
    window.location.href = "/" + page;
}
