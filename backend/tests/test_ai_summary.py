import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AIService

@pytest.mark.asyncio
async def test_ai_summary_no_todos():
    ai_service = AIService()
    summary = await ai_service.generate_summary([])
    assert summary == "No tasks to summarize."

@pytest.mark.asyncio
async def test_ai_summary_with_todos():
    from main import Todo
    
    # Mock todos
    todos = [
        Todo(
            id=1,
            title="Test Todo 1",
            description="Test Description 1",
            completed=False,
            created_at="2023-01-01T00:00:00",
            due_date=None
        ),
        Todo(
            id=2,
            title="Test Todo 2",
            description="Test Description 2",
            completed=True,
            created_at="2023-01-01T00:00:00",
            due_date=None
        )
    ]
    
    ai_service = AIService()
    ai_service.provider = "fallback"  # Force fallback mode
    
    # Test with fallback
    summary = await ai_service.generate_summary(todos)
    assert "2 tasks" in summary
    assert "1 completed" in summary
    assert "1 pending" in summary

@pytest.mark.asyncio
async def test_ai_summary_with_openai():
    from main import Todo
    
    # Create a mock OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test AI summary"
    mock_client.chat.completions.create.return_value = mock_response
    
    ai_service = AIService()
    ai_service.provider = "openai"
    ai_service.client = mock_client
    
    todos = [
        Todo(
            id=1,
            title="Test Todo",
            description="Test Description",
            completed=False,
            created_at="2023-01-01T00:00:00",
            due_date=None
        )
    ]
    
    summary = await ai_service.generate_summary(todos)
    assert summary == "Test AI summary"
    mock_client.chat.completions.create.assert_called_once()