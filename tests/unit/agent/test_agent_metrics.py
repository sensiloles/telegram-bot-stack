"""Tests for agent metrics logging."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture
def metrics_file(tmp_path):
    """Provide temporary metrics file."""
    metrics_path = tmp_path / ".cursor" / "agent_metrics.jsonl"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    return metrics_path


@pytest.fixture
def log_agent_action(metrics_file, monkeypatch):
    """Provide log_agent_action module with mocked metrics file."""
    import sys

    sys.path.insert(0, str(Path(__file__).parents[2] / ".github/workflows/scripts"))

    import log_agent_action

    monkeypatch.setattr(log_agent_action, "METRICS_FILE", metrics_file)
    yield log_agent_action


@pytest.fixture
def agent_metrics_dashboard(metrics_file, monkeypatch):
    """Provide agent_metrics_dashboard module with mocked metrics file."""
    import sys

    sys.path.insert(0, str(Path(__file__).parents[2] / ".github/workflows/scripts"))

    import agent_metrics_dashboard

    monkeypatch.setattr(agent_metrics_dashboard, "METRICS_FILE", metrics_file)
    yield agent_metrics_dashboard


def test_log_action_creates_file(log_agent_action):
    """Test that logging an action creates the metrics file."""
    log_agent_action.log_action(
        action="test_action",
        duration_sec=1.5,
        tokens_used=100,
        success=True,
    )

    assert log_agent_action.METRICS_FILE.exists()


def test_log_action_appends_entry(log_agent_action):
    """Test that logging multiple actions appends entries."""
    log_agent_action.log_action("action1", 1.0, 100, True)
    log_agent_action.log_action("action2", 2.0, 200, True)

    lines = log_agent_action.METRICS_FILE.read_text().strip().split("\n")
    assert len(lines) == 2


def test_log_action_with_error(log_agent_action):
    """Test that logging failed action includes error."""
    log_agent_action.log_action(
        action="test_action",
        duration_sec=1.0,
        tokens_used=50,
        success=False,
        error="Test error",
    )

    line = log_agent_action.METRICS_FILE.read_text().strip()
    entry = json.loads(line)

    assert entry["success"] is False
    assert entry["error"] == "Test error"


def test_log_action_with_metadata(log_agent_action):
    """Test that logging action includes metadata."""
    metadata = {"branch": "feature/test", "pr_number": 42}
    log_agent_action.log_action(
        action="test_action",
        duration_sec=1.0,
        tokens_used=100,
        success=True,
        metadata=metadata,
    )

    line = log_agent_action.METRICS_FILE.read_text().strip()
    entry = json.loads(line)

    assert entry["metadata"] == metadata


def test_log_action_entry_structure(log_agent_action):
    """Test that logged entry has correct structure."""
    log_agent_action.log_action(
        action="test_action",
        duration_sec=1.23,
        tokens_used=456,
        success=True,
        context_lines_loaded=100,
    )

    line = log_agent_action.METRICS_FILE.read_text().strip()
    entry = json.loads(line)

    assert "timestamp" in entry
    assert entry["action"] == "test_action"
    assert entry["duration_sec"] == 1.23
    assert entry["tokens_used"] == 456
    assert entry["context_lines_loaded"] == 100
    assert entry["success"] is True


def test_load_metrics_empty_file(agent_metrics_dashboard):
    """Test loading metrics from non-existent file."""
    metrics = agent_metrics_dashboard.load_metrics()
    assert metrics == []


def test_load_metrics_with_data(agent_metrics_dashboard, log_agent_action):
    """Test loading metrics from file with data."""
    # Log some actions
    log_agent_action.log_action("action1", 1.0, 100, True)
    log_agent_action.log_action("action2", 2.0, 200, True)

    metrics = agent_metrics_dashboard.load_metrics(days=7)
    assert len(metrics) == 2


def test_load_metrics_filters_by_date(agent_metrics_dashboard):
    """Test that load_metrics filters old entries."""
    # Create old entry (10 days ago)
    old_time = datetime.utcnow() - timedelta(days=10)
    old_entry = {
        "timestamp": old_time.isoformat(),
        "action": "old_action",
        "duration_sec": 1.0,
        "tokens_used": 100,
        "success": True,
        "context_lines_loaded": 0,
        "error": None,
        "metadata": {},
    }

    # Create recent entry
    recent_entry = old_entry.copy()
    recent_entry["timestamp"] = datetime.utcnow().isoformat()
    recent_entry["action"] = "recent_action"

    agent_metrics_dashboard.METRICS_FILE.write_text(
        json.dumps(old_entry) + "\n" + json.dumps(recent_entry) + "\n"
    )

    metrics = agent_metrics_dashboard.load_metrics(days=7)
    assert len(metrics) == 1
    assert metrics[0]["action"] == "recent_action"


def test_analyze_metrics_empty(agent_metrics_dashboard):
    """Test analyzing empty metrics."""
    analysis = agent_metrics_dashboard.analyze_metrics([])
    assert "error" in analysis


def test_analyze_metrics_with_data(agent_metrics_dashboard):
    """Test analyzing metrics with data."""
    metrics = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "test_action",
            "duration_sec": 1.5,
            "tokens_used": 1000,
            "success": True,
            "context_lines_loaded": 100,
            "error": None,
            "metadata": {},
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "test_action",
            "duration_sec": 2.0,
            "tokens_used": 1500,
            "success": True,
            "context_lines_loaded": 150,
            "error": None,
            "metadata": {},
        },
    ]

    analysis = agent_metrics_dashboard.analyze_metrics(metrics)

    assert "overall" in analysis
    assert "by_action" in analysis
    assert "daily_tokens" in analysis

    overall = analysis["overall"]
    assert overall["total_actions"] == 2
    assert overall["total_tokens"] == 2500
    assert overall["avg_tokens_per_action"] == 1250.0
    assert overall["success_rate"] == 100.0


def test_analyze_metrics_groups_by_action(agent_metrics_dashboard):
    """Test that analysis groups metrics by action."""
    metrics = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "action1",
            "duration_sec": 1.0,
            "tokens_used": 100,
            "success": True,
            "context_lines_loaded": 0,
            "error": None,
            "metadata": {},
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "action2",
            "duration_sec": 2.0,
            "tokens_used": 200,
            "success": True,
            "context_lines_loaded": 0,
            "error": None,
            "metadata": {},
        },
    ]

    analysis = agent_metrics_dashboard.analyze_metrics(metrics)

    assert "action1" in analysis["by_action"]
    assert "action2" in analysis["by_action"]
    assert analysis["by_action"]["action1"]["count"] == 1
    assert analysis["by_action"]["action2"]["count"] == 1


def test_analyze_metrics_calculates_success_rate(agent_metrics_dashboard):
    """Test that analysis calculates success rate correctly."""
    metrics = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "test",
            "duration_sec": 1.0,
            "tokens_used": 100,
            "success": True,
            "context_lines_loaded": 0,
            "error": None,
            "metadata": {},
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "test",
            "duration_sec": 1.0,
            "tokens_used": 100,
            "success": False,
            "context_lines_loaded": 0,
            "error": "Test error",
            "metadata": {},
        },
    ]

    analysis = agent_metrics_dashboard.analyze_metrics(metrics)

    assert analysis["overall"]["success_rate"] == 50.0
    assert analysis["by_action"]["test"]["success_rate"] == 50.0
