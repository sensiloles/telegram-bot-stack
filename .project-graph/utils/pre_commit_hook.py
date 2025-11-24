#!/usr/bin/env python3
"""Pre-commit hook to auto-update graphs.

This hook runs before git commit and updates relevant graphs
for any staged Python files.

Installation:
    Add to .pre-commit-config.yaml:

    - repo: local
      hooks:
        - id: update-graphs
          name: Update project graphs
          entry: python3 .project-graph/utils/pre_commit_hook.py
          language: system
          pass_filenames: true
"""

import subprocess
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_update import update_graph_for_file


def main():
    """Main entry point."""
    # Get list of staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        check=True,
    )

    staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

    if not staged_files:
        sys.exit(0)

    print("🔄 Updating project graphs for changed files...\n")

    updated = False
    for file_path in staged_files:
        # Skip graph files themselves
        if ".project-graph/" in file_path:
            continue

        # Skip non-source files
        if not any(
            file_path.endswith(ext)
            for ext in [".py", ".md", ".yml", ".yaml", ".toml", ".sh"]
        ):
            continue

        # Update graph
        if update_graph_for_file(file_path, dry_run=False):
            updated = True

    if updated:
        print("\n✅ Graphs updated! Adding to commit...")
        # Stage updated graph files
        subprocess.run(
            ["git", "add", ".project-graph/"], check=False
        )  # Don't fail if nothing to add

    sys.exit(0)


if __name__ == "__main__":
    main()
