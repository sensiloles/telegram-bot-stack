#!/usr/bin/env python3
"""
Analyze repository context and find related files/issues.
"""

import os
import sys
from pathlib import Path

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


def analyze_codebase_context(issue, config):
    """Analyze codebase and find related files."""
    print(f"🔍 Analyzing context for issue #{issue.number}")

    context_config = config.get("context_analysis", {})
    if not context_config.get("enabled", False):
        print("ℹ️ Context analysis is disabled")
        return

    # Extract keywords from issue
    title = (issue.title or "").lower()
    body = (issue.body or "").lower()
    text = f"{title} {body}"

    keywords = extract_keywords(text)

    # Scan configured paths
    scan_paths = context_config.get("analyze_codebase", {}).get("scan_paths", ["src/"])
    related_files = []

    for scan_path in scan_paths:
        if os.path.exists(scan_path):
            for py_file in Path(scan_path).rglob("*.py"):
                if is_file_related(py_file, keywords):
                    related_files.append(str(py_file))

    # Find similar issues
    similar_issues = find_similar_issues(issue, keywords)

    # Build comment
    comment = "🤖 **Cloud Agent - Context Analysis**\n\n"

    if related_files:
        comment += "### 📁 Related Files\n\n"
        comment += "_These files might be relevant to this issue:_\n\n"
        for file in related_files[:10]:  # Limit to 10
            comment += f"- `{file}`\n"

        if len(related_files) > 10:
            remaining_count = len(related_files) - 10
            comment += f"\n_...and {remaining_count} more files_\n"

    if similar_issues:
        comment += "\n### 🔗 Related Issues\n\n"
        comment += "_Similar issues that might be helpful:_\n\n"
        for sim_issue in similar_issues[:5]:  # Limit to 5
            comment += f"- #{sim_issue.number} - {sim_issue.title}\n"

    if not related_files and not similar_issues:
        comment += "ℹ️ No obvious related files or issues found.\n"
        comment += "This might be a new area of the codebase.\n"

    comment += "\n---\n\n"
    comment += (
        "_Detected keywords: " + ", ".join([f"`{kw}`" for kw in keywords[:5]]) + "_"
    )

    # Post comment
    issue.create_comment(comment)
    print("✅ Context analysis added to issue")


def extract_keywords(text):
    """Extract relevant keywords from text."""
    # Remove common words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "was",
        "are",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
    }

    # Extract words
    words = text.lower().split()
    keywords = []

    for word in words:
        # Clean word
        word = "".join(c for c in word if c.isalnum() or c == "_")

        # Filter
        if len(word) > 3 and word not in stop_words:
            keywords.append(word)

    # Return unique keywords
    return list(set(keywords))


def is_file_related(file_path, keywords):
    """Check if file is related to the keywords."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read().lower()

            # Check if any keyword appears in file
            return any(keyword in content for keyword in keywords)
    except Exception:
        return False


def find_similar_issues(current_issue, keywords):
    """Find similar issues based on keywords."""
    repo = current_issue.repository
    similar = []

    try:
        # Get recent closed issues
        issues = repo.get_issues(state="closed", sort="updated", direction="desc")

        for issue in list(issues)[:50]:  # Check last 50 issues
            if issue.number == current_issue.number:
                continue

            issue_text = f"{issue.title} {issue.body or ''}".lower()

            # Count matching keywords
            matches = sum(1 for keyword in keywords if keyword in issue_text)

            if matches >= 2:  # At least 2 matching keywords
                similar.append(issue)

            if len(similar) >= 5:
                break
    except Exception as error:
        print(f"⚠️ Error finding similar issues: {error}")

    return similar


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

    # Analyze context
    analyze_codebase_context(issue, config)


if __name__ == "__main__":
    main()
