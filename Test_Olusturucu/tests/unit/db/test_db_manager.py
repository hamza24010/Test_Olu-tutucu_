def test_add_question(db_session):
    """Test adding a question to the database."""
    q_id = db_session.add_question(
        text="Test Question 1", 
        image_path="/tmp/img.png",
        category="Math",
        difficulty="Easy"
    )
    assert q_id is not None
    assert q_id > 0

def test_get_questions(db_session):
    """Test retrieving questions."""
    db_session.add_question("Q1", "p1", "Cat1", "Easy")
    db_session.add_question("Q2", "p2", "Cat1", "Hard")
    
    questions = db_session.get_all_questions()
    assert len(questions) == 2
    # Verify order (DESC usually)
    assert questions[0][1] == "Q2"  # Depending on schema index for 'text'

def test_delete_question(db_session):
    """Test deleting a single question."""
    q_id = db_session.add_question("DeleteMe", "p", "C", "D")
    questions_before = db_session.get_all_questions()
    assert len(questions_before) == 1
    
    db_session.delete_question(q_id)
    questions_after = db_session.get_all_questions()
    assert len(questions_after) == 0

def test_delete_all(db_session):
    """Test clearing the table."""
    db_session.add_question("Q1", "p", "C", "D")
    db_session.add_question("Q2", "p", "C", "D")
    
    db_session.delete_all_questions()
    questions = db_session.get_all_questions()
    assert len(questions) == 0
