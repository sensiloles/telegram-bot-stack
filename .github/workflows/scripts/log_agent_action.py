#!/usr/bin/env python3
"""
Log agent actions for performance tracking.

Logs actions to JSONL file for analysis and optimization insights.

Usage:
    # Log an action
    python3 .github/workflows/scripts/log_agent_action.py \
        --action "implement_feature" \
        --duration 120 \
        --tokens 5000 \
        --success

    # Log failed action
    python3 .github/workflows/scripts/log_agent_action.py \
        --action "create_pr" \
        --duration 5 \
        --tokens 800 \
        --error "API rate limit"
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

METRICS_FILE = Path(".cursor/agent_metrics.jsonl")


def _ensure_cursor_dir():
    """Ensure .cursor directory exists."""
    cursor_dir = METRICS_FILE.parent
    cursor_dir.mkdir(exist_ok=True)


def log_action(
    action: str,
    duration_sec: float,
    tokens_used: int,
    success: bool,
    error: Optional[str] = None,
    context_lines_loaded: int = 0,
    metadata: Optional[dict] = None,
):
    """Log an agent action with metrics.

    Args:
        action: Action name (e.g., "implement_feature", "create_pr")
        duration_sec: Duration in seconds
        tokens_used: Number of tokens consumed
        success: Whether action succeeded
        error: Error message if failed
        context_lines_loaded: Number of lines loaded into context
        metadata: Additional metadata (dict)
    """
    _ensure_cursor_dir()

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "duration_sec": round(duration_sec, 2),
        "tokens_used": tokens_used,
        "context_lines_loaded": context_lines_loaded,
        "success": success,
        "error": error,
        "metadata": metadata or {},
    }

    with open(METRICS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Log agent action metrics")
    parser.add_argument(
        "--action",
        required=True,
        help="Action name (e.g., implement_feature, create_pr)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        required=True,
        help="Duration in seconds",
    )
    parser.add_argument(
        "--tokens",
        type=int,
        required=True,
        help="Tokens consumed",
    )
    parser.add_argument(
        "--success",
        action="store_true",
        help="Action succeeded",
    )
    parser.add_argument(
        "--error",
        help="Error message if failed",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=0,
        help="Context lines loaded",
    )
    parser.add_argument(
        "--metadata",
        help="Additional metadata (JSON string)",
    )

    args = parser.parse_args()

    metadata = None
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON metadata: {args.metadata}")

    log_action(
        action=args.action,
        duration_sec=args.duration,
        tokens_used=args.tokens,
        success=args.success,
        error=args.error,
        context_lines_loaded=args.context_lines,
        metadata=metadata,
    )

    print(f"✅ Logged action: {args.action}")


if __name__ == "__main__":
    main()
