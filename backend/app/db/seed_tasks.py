"""
Task model schema and seeding functions for the SF Comparative Analysis database.
Defines the Task database model and provides methods to populate the database with benchmark tasks.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Create declarative base for SQLAlchemy models
Base = declarative_base()


class Task(Base):
    """
    Task model representing a coding task in the benchmark suite.
    
    Attributes:
        task_id: Unique identifier for the task (e.g., 'a', 'b', 'c', etc.)
        title: Display title of the task
        description: Long-form description of what the task requires
        prompt: The exact prompt given to the AI models
        language: Programming language for the task
        expected_output: Path or reference to expected output
        rubric: JSON object containing evaluation criteria and scoring
        difficulty_level: Difficulty rating (e.g., 'easy', 'medium', 'hard')
        is_active: Whether this task is currently used in evaluations
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified
    """
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(1), unique=True, nullable=False, index=True)  # 'a', 'b', 'c', etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    expected_output = Column(Text, nullable=True)
    rubric = Column(JSON, nullable=True)
    difficulty_level = Column(String(20), default="medium")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Task(task_id='{self.task_id}', title='{self.title}')>"


class TaskPydantic:
    """Pydantic-like schema for Task validation (for FastAPI routes)."""
    
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        prompt: str,
        language: str = "python",
        expected_output: str = None,
        rubric: dict = None,
        difficulty_level: str = "medium",
        is_active: bool = True,
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.prompt = prompt
        self.language = language
        self.expected_output = expected_output
        self.rubric = rubric or {}
        self.difficulty_level = difficulty_level
        self.is_active = is_active


# Default seed data for tasks
DEFAULT_TASKS = {
    "a": {
        "title": "Read from Text File",
        "description": "Write code to read from a text file",
        "prompt": "Write code to read from a text file",
        "difficulty_level": "easy",
        "language": "python",
    },
    "b": {
        "title": "Read JSON using Threads",
        "description": "Read JSON using threads",
        "prompt": "Read JSON using threads",
        "difficulty_level": "medium",
        "language": "python",
    },
    "c": {
        "title": "Write to Text File",
        "description": "Write to text file",
        "prompt": "Write to text file",
        "difficulty_level": "easy",
        "language": "python",
    },
    "d": {
        "title": "Write JSON with Threads",
        "description": "Write JSON with threads",
        "prompt": "Write JSON with threads",
        "difficulty_level": "medium",
        "language": "python",
    },
    "e": {
        "title": "Create Zip File",
        "description": "Create zip file",
        "prompt": "Create zip file",
        "difficulty_level": "medium",
        "language": "python",
    },
    "f": {
        "title": "Connect to MySQL",
        "description": "Connect to MySQL",
        "prompt": "Connect to MySQL",
        "difficulty_level": "medium",
        "language": "python",
    },
    "g": {
        "title": "Connect to MongoDB",
        "description": "Connect to MongoDB",
        "prompt": "Connect to MongoDB",
        "difficulty_level": "medium",
        "language": "python",
    },
    "h": {
        "title": "Authentication System",
        "description": "Authentication system",
        "prompt": "Authentication system",
        "difficulty_level": "hard",
        "language": "python",
    },
}


def load_task_rubric(task_id: str) -> dict:
    """
    Load task rubric from benchmarks folder if it exists.
    
    Args:
        task_id: Task identifier (e.g., 'a', 'b', 'c')
        
    Returns:
        Dictionary containing rubric data, or empty dict if not found
    """
    rubric_path = Path(__file__).parent.parent.parent / "benchmarks" / f"tasks_{task_id}" / "expected_output" / "rubric.json"
    
    if rubric_path.exists():
        try:
            with open(rubric_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load rubric for task {task_id}: {str(e)}")
    
    return {}


def load_task_prompt(task_id: str) -> str:
    """
    Load task prompt from benchmarks folder if it exists.
    
    Args:
        task_id: Task identifier (e.g., 'a', 'b', 'c')
        
    Returns:
        Prompt text, or default prompt if not found
    """
    prompt_path = Path(__file__).parent.parent.parent / "benchmarks" / f"tasks_{task_id}" / "prompt.md"
    
    if prompt_path.exists():
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load prompt for task {task_id}: {str(e)}")
    
    return DEFAULT_TASKS.get(task_id, {}).get("prompt", "")


def seed_tasks(session: Session, override: bool = False) -> list:
    """
    Populate the database with default tasks from benchmark suite.
    
    Args:
        session: SQLAlchemy database session
        override: If True, delete existing tasks before seeding
        
    Returns:
        List of created Task objects
    """
    if override:
        session.query(Task).delete()
        session.commit()
        logger.info("Cleared existing tasks")
    
    created_tasks = []
    
    for task_id, task_data in DEFAULT_TASKS.items():
        # Check if task already exists
        existing = session.query(Task).filter(Task.task_id == task_id).first()
        if existing:
            logger.info(f"Task {task_id} already exists, skipping")
            continue
        
        # Load rubric and prompt from files if available
        rubric = load_task_rubric(task_id)
        prompt = load_task_prompt(task_id)
        
        # Create task
        task = Task(
            task_id=task_id,
            title=task_data.get("title", f"Task {task_id}"),
            description=task_data.get("description", ""),
            prompt=prompt or task_data.get("prompt", ""),
            language=task_data.get("language", "python"),
            rubric=rubric or None,
            difficulty_level=task_data.get("difficulty_level", "medium"),
            is_active=True,
        )
        
        session.add(task)
        created_tasks.append(task)
        logger.info(f"Created task: {task_id} - {task.title}")
    
    session.commit()
    logger.info(f"Successfully seeded {len(created_tasks)} tasks")
    
    return created_tasks


def get_task(session: Session, task_id: str) -> Task:
    """
    Retrieve a specific task by ID.
    
    Args:
        session: SQLAlchemy database session
        task_id: Task identifier
        
    Returns:
        Task object or None if not found
    """
    return session.query(Task).filter(Task.task_id == task_id).first()


def get_all_tasks(session: Session, active_only: bool = True) -> list:
    """
    Retrieve all tasks from the database.
    
    Args:
        session: SQLAlchemy database session
        active_only: If True, only return active tasks
        
    Returns:
        List of Task objects
    """
    query = session.query(Task)
    
    if active_only:
        query = query.filter(Task.is_active == True)
    
    return query.all()


def update_task(session: Session, task_id: str, **kwargs) -> Task:
    """
    Update a task with new values.
    
    Args:
        session: SQLAlchemy database session
        task_id: Task identifier
        **kwargs: Fields to update (e.g., title="New Title", rubric={...})
        
    Returns:
        Updated Task object
    """
    task = get_task(session, task_id)
    
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)
    
    task.updated_at = datetime.utcnow()
    session.commit()
    logger.info(f"Updated task {task_id}")
    
    return task


if __name__ == "__main__":
    # Example usage for direct seeding
    from database import DatabaseManager
    
    db = DatabaseManager()
    db.create_all_tables()
    
    with db.session_scope() as session:
        seed_tasks(session)
