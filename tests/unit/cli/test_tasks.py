"""
Tests for scripts/tasks.py cross-platform task runner.

These tests ensure the task runner works correctly on all platforms.
"""

import subprocess
import sys
from pathlib import Path

import pytest


# Test helper functions
def test_import_tasks():
    """Test that scripts/tasks.py can be imported."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    assert spec is not None
    tasks = importlib.util.module_from_spec(spec)
    assert tasks is not None


def test_run_help_command():
    """Test that scripts/tasks.py help command works."""
    result = subprocess.run(
        [sys.executable, "scripts/tasks.py", "help"],
        cwd=Path(__file__).parent.parent.parent.parent,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "telegram-bot-stack - Development Commands" in result.stdout
    assert "Testing Commands:" in result.stdout
    assert "Coverage Commands:" in result.stdout
    assert "Development Commands:" in result.stdout


def test_run_invalid_command():
    """Test that scripts/tasks.py fails gracefully with invalid command."""
    result = subprocess.run(
        [sys.executable, "scripts/tasks.py", "invalid-command"],
        cwd=Path(__file__).parent.parent.parent.parent,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "invalid choice" in result.stderr.lower()


def test_all_tasks_have_help_entries():
    """Test that all tasks are documented in help."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    tasks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks)  # type: ignore

    # Get all task names from TASKS dict
    task_names = list(tasks.TASKS.keys())

    # Run help command and capture output
    result = subprocess.run(
        [sys.executable, "scripts/tasks.py", "help"],
        cwd=Path(__file__).parent.parent.parent.parent,
        capture_output=True,
        text=True,
    )

    help_text = result.stdout.lower()

    # Critical tasks that must be documented
    critical_tasks = [
        "test",
        "test-fast",
        "lint",
        "format",
        "clean",
        "dev",
        "coverage",
    ]

    for task in critical_tasks:
        # Check if task is mentioned in help (handles hyphens)
        assert (
            task.replace("-", " ") in help_text or task.replace("-", "-") in help_text
        ), f"Task '{task}' not documented in help"


def test_color_class_disable():
    """Test Colors.disable() method works."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    tasks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks)  # type: ignore

    Colors = tasks.Colors

    # Store original values
    original_green = Colors.GREEN

    # Disable colors
    Colors.disable()

    # Colors should be empty strings (or original if ANSICON is set)
    # We just test that the method runs without error
    assert isinstance(Colors.GREEN, str)

    # Restore (if they were changed)
    if original_green:
        Colors.GREEN = original_green


def test_run_function_basic():
    """Test the run() helper function."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    tasks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks)  # type: ignore

    # Test successful command
    result = tasks.run([sys.executable, "--version"], check=False)
    assert isinstance(result, subprocess.CompletedProcess)
    assert result.returncode == 0


def test_run_function_with_error():
    """Test run() function with failing command."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    tasks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks)  # type: ignore

    # Test command that fails
    result = tasks.run([sys.executable, "-c", "import sys; sys.exit(1)"], check=False)
    assert result.returncode == 1


def test_print_functions():
    """Test print helper functions don't crash."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    tasks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks)  # type: ignore

    # These should not raise exceptions
    tasks.print_header("Test Header")
    tasks.print_section("🧪", "Test Section")
    tasks.print_success("Success message")
    tasks.print_warning("Warning message")
    tasks.print_info("Info message")


def test_tasks_dict_completeness():
    """Test that TASKS dict contains all expected commands."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    tasks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks)  # type: ignore

    expected_tasks = [
        "help",
        "test",
        "test-fast",
        "test-unit",
        "test-integration",
        "lint",
        "format",
        "clean",
        "install",
        "dev",
        "coverage",
    ]

    for task in expected_tasks:
        assert task in tasks.TASKS, f"Task '{task}' missing from TASKS dict"


def test_make_bat_exists():
    """Test that make.bat wrapper exists for Windows."""
    make_bat = Path(__file__).parent.parent.parent.parent / "make.bat"
    assert make_bat.exists(), "make.bat not found"

    content = make_bat.read_text()
    assert (
        "scripts" in content.lower() and "tasks.py" in content
    ), "make.bat doesn't call scripts/tasks.py"


@pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test (shebang)")
def test_tasks_py_executable():
    """Test that scripts/tasks.py has proper shebang for Unix."""
    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    first_line = tasks_path.read_text().split("\n")[0]
    assert first_line.startswith(
        "#!/usr/bin/env python"
    ), "scripts/tasks.py missing shebang"


def test_main_function_exists():
    """Test that main() function exists and can be called."""
    import importlib.util

    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    spec = importlib.util.spec_from_file_location("tasks", tasks_path)
    tasks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks)  # type: ignore

    assert hasattr(tasks, "main"), "main() function not found"
    assert callable(tasks.main), "main is not callable"


def test_documentation_updated():
    """Test that documentation mentions cross-platform support."""
    readme = Path(__file__).parent.parent.parent.parent / "README.md"
    contributing = Path(__file__).parent.parent.parent.parent / "CONTRIBUTING.md"

    readme_content = readme.read_text()
    contributing_content = contributing.read_text()

    # README should mention Platform Support
    assert (
        "Platform Support" in readme_content
        or "cross-platform" in readme_content.lower()
    )

    # README should show scripts/tasks.py usage
    assert "scripts/tasks.py" in readme_content or "python tasks.py" in readme_content

    # CONTRIBUTING should show both approaches
    assert (
        "scripts/tasks.py" in contributing_content
        or "python tasks.py" in contributing_content
    )
    assert "make" in contributing_content.lower()


def test_no_hardcoded_python_version():
    """Test that scripts/tasks.py uses sys.executable, not hardcoded python."""
    tasks_path = Path(__file__).parent.parent.parent.parent / "scripts" / "tasks.py"
    content = tasks_path.read_text()

    # Check that we use sys.executable for subprocess calls
    assert "sys.executable" in content, "scripts/tasks.py should use sys.executable"

    # Check that we don't use hardcoded python3 or python
    # (except in shebang, comments, or help text)
    lines = content.split("\n")
    code_lines = [
        line
        for line in lines
        if not line.strip().startswith("#")
        and not line.strip().startswith('"""')
        and not line.strip().startswith("print")
    ]

    for line in code_lines:
        # Allow ["python3", ...] in comments/help but not in subprocess calls
        if "subprocess" in line or "run([" in line:
            assert (
                '"python3"' not in line and '"python"' not in line
            ), f"Hardcoded python in: {line}"
