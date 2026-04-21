import pytest
import sys
from pathlib import Path

# Add the backend directory to the path so we can import app
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.prompt_builder import build_prompt


class TestPromptBuilder:
    """Test suite for the prompt_builder module."""

    def test_build_prompt_task_a(self):
        """Test that task 'a' returns the correct prompt."""
        expected = "Write code to read from a text file"
        result = build_prompt("a")
        assert result == expected

    def test_build_prompt_task_b(self):
        """Test that task 'b' returns the correct prompt."""
        expected = "Read JSON using threads"
        result = build_prompt("b")
        assert result == expected

    def test_build_prompt_task_c(self):
        """Test that task 'c' returns the correct prompt."""
        expected = "Write to text file"
        result = build_prompt("c")
        assert result == expected

    def test_build_prompt_task_d(self):
        """Test that task 'd' returns the correct prompt."""
        expected = "Write JSON with threads"
        result = build_prompt("d")
        assert result == expected

    def test_build_prompt_task_e(self):
        """Test that task 'e' returns the correct prompt."""
        expected = "Create zip file"
        result = build_prompt("e")
        assert result == expected

    def test_build_prompt_task_f(self):
        """Test that task 'f' returns the correct prompt."""
        expected = "Connect to MySQL"
        result = build_prompt("f")
        assert result == expected

    def test_build_prompt_task_g(self):
        """Test that task 'g' returns the correct prompt."""
        expected = "Connect to MongoDB"
        result = build_prompt("g")
        assert result == expected

    def test_build_prompt_task_h(self):
        """Test that task 'h' returns the correct prompt."""
        expected = "Authentication system"
        result = build_prompt("h")
        assert result == expected

    def test_build_prompt_unknown_task(self):
        """Test that unknown task codes return 'Unknown task'."""
        result = build_prompt("z")
        assert result == "Unknown task"

    def test_build_prompt_empty_string(self):
        """Test that empty string returns 'Unknown task'."""
        result = build_prompt("")
        assert result == "Unknown task"

    def test_build_prompt_none_input(self):
        """Test that None input returns 'Unknown task'."""
        result = build_prompt(None)
        assert result == "Unknown task"

    def test_build_prompt_case_sensitive(self):
        """Test that task codes are case-sensitive."""
        # Uppercase should return 'Unknown task'
        result = build_prompt("A")
        assert result == "Unknown task"

    @pytest.mark.parametrize("task_code,expected_prompt", [
        ("a", "Write code to read from a text file"),
        ("b", "Read JSON using threads"),
        ("c", "Write to text file"),
        ("d", "Write JSON with threads"),
        ("e", "Create zip file"),
        ("f", "Connect to MySQL"),
        ("g", "Connect to MongoDB"),
        ("h", "Authentication system"),
    ])
    def test_build_prompt_parametrized(self, task_code, expected_prompt):
        """Parametrized test for all valid task codes."""
        result = build_prompt(task_code)
        assert result == expected_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
