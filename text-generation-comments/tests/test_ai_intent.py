import pytest
from app.services.comment_rephraser import CommentRephraser
from app.models.rephrase_schemas import ReviewStatus

@pytest.fixture
def rephraser():
    return CommentRephraser()

def test_prompt_intent_submit(rephraser):
    """Verify SUBMIT intent generates approval-focused prompts."""
    prompt = rephraser._build_prompt(
        input_text="looks good",
        status=ReviewStatus.SUBMIT,
        expanded_text="looks good"
    )
    assert "Use positive, confirming language" in prompt
    assert "Indicate approval or acceptance" in prompt
    assert "STATUS: SUBMIT" in prompt

def test_prompt_intent_revise(rephraser):
    """Verify REVISE intent generates correction-focused prompts."""
    prompt = rephraser._build_prompt(
        input_text="wrong dims",
        status=ReviewStatus.REVISE,
        expanded_text="wrong dimensions"
    )
    assert "Use constructive, helpful language" in prompt
    assert "Focus on what needs to be changed" in prompt
    assert "STATUS: REVISE" in prompt

def test_prompt_intent_comment(rephraser):
    """Verify COMMENT intent generates neutral prompts."""
    prompt = rephraser._build_prompt(
        input_text="check this",
        status=ReviewStatus.COMMENT,
        expanded_text="check this"
    )
    assert "Use neutral, informative language" in prompt
    assert "Ask clarifying questions if needed" in prompt
    assert "STATUS: COMMENT" in prompt

def test_thread_context_inclusion(rephraser):
    """Verify thread history is correctly included in the prompt."""
    history = [
        {"user_name": "Alice", "role": "Architect", "text": "Please fix the column.", "status": "revise"},
        {"user_name": "Bob", "role": "Engineer", "text": "Which column?", "status": "comment"}
    ]
    prompt = rephraser._build_prompt(
        input_text="grid A1",
        status=ReviewStatus.COMMENT,
        expanded_text="grid A1",
        thread_history=history
    )
    
    assert "--- CONVERSATION THREAD" in prompt
    assert 'Alice: "Please fix the column."' in prompt
    assert 'Bob: "Which column?"' in prompt
    assert "You are writing a REPLY" in prompt
