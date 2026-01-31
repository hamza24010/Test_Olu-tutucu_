import pytest
from unittest.mock import MagicMock

def test_question_processing_flow(db_session, mock_gemini_service):
    """
    Tests the integration of:
    - PDF Analysis (simulated)
    - Gemini Service (mocked)
    - Question Cropping (mocked)
    - Database Storage (real in-memory)
    """
    
    # Setup Mocks
    mock_pdf_processor = MagicMock()
    mock_pdf_processor.convert_pdf_to_images.return_value = ["fake_page_1.png"]
    mock_pdf_processor.crop_question.return_value = "/tmp/assets/q_1.png"
    
    # Execution (Simulation of Controller Logic)
    pdf_path = "dummy.pdf"
    
    # 1. Convert
    images = mock_pdf_processor.convert_pdf_to_images(pdf_path)
    assert len(images) == 1
    
    # 2. Analyze
    # mock_gemini_service fixture returns 2 questions
    questions_data = mock_gemini_service.analyze_chunk(images)
    assert len(questions_data) == 2
    
    # 3. Process & Save
    saved_ids = []
    for q_data in questions_data:
        # Simulate index logic
        p_idx = q_data.get('page_index', 0)
        img_to_crop = images[0] # simplified
        
        # Crop
        out_path = mock_pdf_processor.crop_question(img_to_crop, q_data['coordinates'], "out.png")
        
        # Save to DB
        if out_path:
            q_id = db_session.add_question(
                text=q_data['text'],
                image_path=out_path,
                category="General",
                difficulty="Medium"
            )
            saved_ids.append(q_id)
            
    # Assertions
    assert len(saved_ids) == 2
    
    # Verify DB state
    db_questions = db_session.get_all_questions()
    assert len(db_questions) == 2
    
    # Check data integrity
    # DBManager fetches (id, text, image_path, cat, diff, created_at)
    # Ordered by created_at DESC
    
    # Since mocked Geminis have "Mock Question Text 1" and "Mock Question Text 2"
    texts = [q[1] for q in db_questions]
    assert "Mock Question Text 1" in texts
    assert "Mock Question Text 2" in texts
