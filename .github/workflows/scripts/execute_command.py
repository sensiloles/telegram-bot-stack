#!/usr/bin/env python3
"""
Execute Cloud Agent commands.
"""

import json
import os
import sys

from github import Github  # noqa: E402 - installed in CI environment


def execute_breakdown(issue, repo):
    """Break issue into subtasks."""
    print(f"🔄 Breaking down issue #{issue.number}")

    # This would call the subtask generation script
    os.system("python .github/workflows/scripts/generate_subtasks.py")


def execute_estimate(issue, repo):
    """Estimate issue complexity."""
    print(f"📊 Estimating complexity for issue #{issue.number}")

    # Simple estimation based on description length and keywords
    body = issue.body or ""
    title = issue.title or ""

    complexity_indicators = {
        "simple": ["fix typo", "update doc", "small change"],
        "medium": ["add feature", "implement", "create"],
        "complex": ["refactor", "redesign", "migrate", "integrate"],
        "epic": ["system", "architecture", "complete rewrite"],
    }

    text = (title + " " + body).lower()

    for complexity, keywords in complexity_indicators.items():
        if any(keyword in text for keyword in keywords):
            comment = f"📊 **Estimated Complexity**: `{complexity.upper()}`\n\n"

            if complexity == "simple":
                comment += "⏱️ Estimated time: 1-3 hours"
            elif complexity == "medium":
                comment += "⏱️ Estimated time: 4-8 hours"
            elif complexity == "complex":
                comment += "⏱️ Estimated time: 1-3 days"
            else:
                comment += "⏱️ Estimated time: 1+ weeks"

            issue.create_comment(comment)
            return

    default_comment = (
        "📊 **Estimated Complexity**: `MEDIUM` (default)\n\n⏱️ Estimated time: 4-8 hours"
    )
    issue.create_comment(default_comment)


def execute_accept(issue, repo):
    """Generate acceptance criteria."""
    print(f"✅ Generating acceptance criteria for issue #{issue.number}")

    os.system("python .github/workflows/scripts/add_acceptance_criteria.py")


def execute_relate(issue, repo):
    """Find related context."""
    print(f"🔗 Finding related context for issue #{issue.number}")

    os.system("python .github/workflows/scripts/analyze_context.py")


def execute_label(issue, repo, labels):
    """Add labels to issue."""
    print(f"🏷️ Adding labels to issue #{issue.number}: {labels}")

    current_labels = [label.name for label in issue.labels]
    new_labels = current_labels + labels

    issue.edit(labels=new_labels)
    issue.create_comment(
        f"🏷️ Added labels: {', '.join([f'`{label}`' for label in labels])}"
    )


def execute_assign(issue, repo, assignee):
    """Assign issue to user."""
    print(f"👤 Assigning issue #{issue.number} to {assignee}")

    try:
        issue.add_to_assignees(assignee)
        issue.create_comment(f"👤 Assigned to @{assignee}")
    except Exception as error:
        issue.create_comment(f"❌ Failed to assign to @{assignee}: {str(error)}")


def main():
    """Main execution."""
    github_token = os.getenv("GITHUB_TOKEN")
    command = os.getenv("COMMAND", "")
    args_json = os.getenv("ARGS", "{}")

    if not github_token:
        print("❌ GITHUB_TOKEN not set")
        sys.exit(1)

    if not command:
        print("ℹ️ No command to execute")
        sys.exit(0)

    args = json.loads(args_json)

    # Get GitHub context
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

    # Get issue from event context
    event_path = os.getenv("GITHUB_EVENT_PATH")
    with open(event_path) as f:
        event = json.load(f)

    issue_number = event.get("issue", {}).get("number")
    if not issue_number:
        print("❌ No issue number found in event")
        sys.exit(1)

    issue = repo.get_issue(issue_number)

    # Execute command
    if command == "breakdown":
        execute_breakdown(issue, repo)
    elif command == "estimate":
        execute_estimate(issue, repo)
    elif command == "accept":
        execute_accept(issue, repo)
    elif command == "relate":
        execute_relate(issue, repo)
    elif command == "label" and "labels" in args:
        execute_label(issue, repo, args["labels"])
    elif command == "assign" and "assignee" in args:
        execute_assign(issue, repo, args["assignee"])
    else:
        issue.create_comment(f"❌ Unknown command: `/{command}`")
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

    print("✅ Command executed successfully")


if __name__ == "__main__":
    main()
