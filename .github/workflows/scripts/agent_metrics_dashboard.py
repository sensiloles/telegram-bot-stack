#!/usr/bin/env python3
"""
Generate agent performance dashboard from metrics.

Analyzes agent_metrics.jsonl and produces performance insights.

Usage:
    # Show dashboard
    python3 .github/workflows/scripts/agent_metrics_dashboard.py

    # Show metrics for last N days
    python3 .github/workflows/scripts/agent_metrics_dashboard.py --days 7

    # Export to JSON
    python3 .github/workflows/scripts/agent_metrics_dashboard.py --json
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

METRICS_FILE = Path(".cursor/agent_metrics.jsonl")


def load_metrics(days: int = 7) -> list[dict]:
    """Load metrics from JSONL file, filtered by date.

    Args:
        days: Number of days to include (default: 7)

    Returns:
        List of metric entries
    """
    if not METRICS_FILE.exists():
        return []

    cutoff = datetime.utcnow() - timedelta(days=days)
    metrics = []

    for line in METRICS_FILE.read_text().splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if timestamp >= cutoff:
                metrics.append(entry)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue

    return metrics


def analyze_metrics(metrics: list[dict]) -> dict[str, Any]:
    """Analyze metrics and generate statistics.

    Args:
        metrics: List of metric entries

    Returns:
        Dictionary with analysis results
    """
    if not metrics:
        return {"error": "No metrics data available"}

    # Group by action
    actions = defaultdict(list)
    for entry in metrics:
        actions[entry["action"]].append(entry)

    # Calculate statistics per action
    action_stats = {}
    for action, entries in sorted(actions.items()):
        tokens = [e["tokens_used"] for e in entries]
        durations = [e["duration_sec"] for e in entries]
        successes = [e["success"] for e in entries]

        action_stats[action] = {
            "count": len(entries),
            "avg_tokens": round(sum(tokens) / len(tokens), 1),
            "total_tokens": sum(tokens),
            "avg_duration": round(sum(durations) / len(durations), 2),
            "success_rate": round(sum(successes) / len(successes) * 100, 1),
            "total_duration": round(sum(durations), 2),
        }

    # Overall statistics
    all_tokens = [e["tokens_used"] for e in metrics]
    all_durations = [e["duration_sec"] for e in metrics]
    all_successes = [e["success"] for e in metrics]

    overall = {
        "total_actions": len(metrics),
        "total_tokens": sum(all_tokens),
        "avg_tokens_per_action": round(sum(all_tokens) / len(all_tokens), 1),
        "total_duration": round(sum(all_durations), 2),
        "avg_duration": round(sum(all_durations) / len(all_durations), 2),
        "success_rate": round(sum(all_successes) / len(all_successes) * 100, 1),
    }

    # Token trends (by day)
    daily_tokens = defaultdict(int)
    for entry in metrics:
        date = datetime.fromisoformat(entry["timestamp"]).date().isoformat()
        daily_tokens[date] += entry["tokens_used"]

    return {
        "overall": overall,
        "by_action": action_stats,
        "daily_tokens": dict(sorted(daily_tokens.items())),
    }


def print_dashboard(analysis: dict):
    """Print dashboard to console.

    Args:
        analysis: Analysis results from analyze_metrics()
    """
    if "error" in analysis:
        print(f"❌ {analysis['error']}")
        return

    print("=" * 80)
    print("🤖 AGENT PERFORMANCE DASHBOARD")
    print("=" * 80)
    print()

    # Overall stats
    overall = analysis["overall"]
    print("📊 OVERALL STATISTICS")
    print("-" * 80)
    print(f"  Total Actions:        {overall['total_actions']}")
    print(f"  Total Tokens Used:    {overall['total_tokens']:,}")
    print(f"  Avg Tokens/Action:    {overall['avg_tokens_per_action']:.1f}")
    print(f"  Total Duration:       {overall['total_duration']:.1f}s")
    print(f"  Avg Duration:         {overall['avg_duration']:.2f}s")
    print(f"  Success Rate:         {overall['success_rate']:.1f}%")
    print()

    # Per-action stats
    print("📈 BY ACTION")
    print("-" * 80)
    print(
        f"{'Action':<25} {'Count':>8} {'Avg Tokens':>12} {'Avg Time':>10} {'Success':>10}"
    )
    print("-" * 80)

    for action, stats in sorted(
        analysis["by_action"].items(), key=lambda x: x[1]["total_tokens"], reverse=True
    ):
        print(
            f"{action:<25} {stats['count']:>8} "
            f"{stats['avg_tokens']:>12.1f} {stats['avg_duration']:>9.2f}s "
            f"{stats['success_rate']:>9.1f}%"
        )
    print()

    # Daily trends
    print("📅 DAILY TOKEN USAGE")
    print("-" * 80)
    for date, tokens in analysis["daily_tokens"].items():
        print(f"  {date}: {tokens:>8,} tokens")
    print()
    print("=" * 80)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate agent performance dashboard")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted dashboard",
    )

    args = parser.parse_args()

    metrics = load_metrics(days=args.days)
    analysis = analyze_metrics(metrics)

    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print_dashboard(analysis)


if __name__ == "__main__":
    main()
