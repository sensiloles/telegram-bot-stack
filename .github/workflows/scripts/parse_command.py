#!/usr/bin/env python3
"""
Parse slash commands from issue comments.
"""

import json
import os
import sys
from typing import Dict, Optional


def parse_slash_command(comment_body: str) -> tuple[Optional[str], Dict[str, str]]:
    """
    Parse slash command from comment body.

    Supported commands:
    - /breakdown - Break issue into subtasks
    - /estimate - Estimate complexity
    - /accept - Generate acceptance criteria
    - /relate - Find related context
    - /label <labels> - Add labels
    - /assign @user - Assign to user
    """
    lines = comment_body.strip().split("\n")
    if not lines or not lines[0].startswith("/"):
        return None, {}

    command_line = lines[0].strip()
    parts = command_line.split(maxsplit=1)

    command = parts[0][1:]  # Remove leading /
    args = {}

    if len(parts) > 1:
        args["raw"] = parts[1]

        # Parse specific arguments based on command
        if command == "label":
            args["labels"] = [label.strip() for label in parts[1].split(",")]
        elif command == "assign":
            args["assignee"] = parts[1].strip("@")
        elif command == "priority":
            args["priority"] = parts[1].strip()

    # Include additional context from comment
    if len(lines) > 1:
        args["context"] = "\n".join(lines[1:]).strip()

    return command, args


def main():
    """Main execution."""
    comment_body = os.getenv("COMMENT_BODY", "")

    if not comment_body:
        print("No comment body provided")
        sys.exit(0)

    command, args = parse_slash_command(comment_body)

    if not command:
        print("No valid slash command found")
        sys.exit(0)

    # Output for GitHub Actions
    print(f"::set-output name=command::{command}")
    print(f"::set-output name=args::{json.dumps(args)}")

    print(f"✅ Parsed command: /{command}")
    print(f"Arguments: {args}")


if __name__ == "__main__":
    main()
