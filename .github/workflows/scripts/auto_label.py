#!/usr/bin/env python3
"""
Automatically label issues based on content analysis.
"""

import os
import sys

import yaml
from github import Github  # noqa: E402 - installed in CI environment


def load_config():
    """Load Cloud Agent configuration."""
    config_path = ".github/cloud-agent-config.yml"

    if not os.path.exists(config_path):
        print(f"⚠️ Config file not found: {config_path}")
        return None

    with open(config_path) as f:
        return yaml.safe_load(f)


def analyze_and_label(issue, config):
    """Analyze issue and apply appropriate labels."""
    title = (issue.title or "").lower()
    body = (issue.body or "").lower()
    text = f"{title} {body}"

    labels_to_add = []

    # Get labeling config
    auto_labeling = config.get("issue_creation", {}).get("auto_labeling", {})
    if not auto_labeling.get("enabled", False):
        print("ℹ️ Auto-labeling is disabled")
        return

    label_categories = auto_labeling.get("labels", {})

    # Check each label category
    for _category_name, category_labels in label_categories.items():
        for label_config in category_labels:
            label_name = label_config.get("name")
            keywords = label_config.get("keywords", [])

            # Check if any keyword matches
            if any(keyword.lower() in text for keyword in keywords):
                labels_to_add.append(label_name)
                break  # Only add one label per category

    # Apply labels
    if labels_to_add:
        current_labels = [label.name for label in issue.labels]
        new_labels = list(set(current_labels + labels_to_add))

        issue.edit(labels=new_labels)

        comment = "🤖 **Cloud Agent Auto-Labeling**\n\n"
        comment += f"Applied labels: {', '.join([f'`{label}`' for label in labels_to_add])}\n\n"
        comment += "_Use `/label <name>` to add more labels manually_"

        issue.create_comment(comment)

        print(f"✅ Added labels: {', '.join(labels_to_add)}")
    else:
        print("ℹ️ No matching labels found")


def main():
    """Main execution."""
    github_token = os.getenv("GITHUB_TOKEN")
    issue_number = os.getenv("ISSUE_NUMBER")

    if not github_token:
        print("❌ GITHUB_TOKEN not set")
        sys.exit(1)

    if not issue_number:
        print("❌ ISSUE_NUMBER not set")
        sys.exit(1)

    # Load configuration
    config = load_config()
    if not config:
        sys.exit(1)

    # Get GitHub objects
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    issue = repo.get_issue(int(issue_number))

    print(f"🔍 Analyzing issue #{issue_number}: {issue.title}")

    # Analyze and label
    analyze_and_label(issue, config)


if __name__ == "__main__":
    main()
