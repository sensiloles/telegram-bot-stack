#!/usr/bin/env python3
"""Check if GitHub automation setup is correct."""

import sys

from common import (
    get_current_branch,
    get_github_client,
    get_github_token,
    get_repository_name,
    print_error,
    print_info,
    print_success,
    print_warning,
)


def check_setup() -> bool:
    """Check setup and return True if everything is OK."""
    all_ok = True

    print_info("Checking GitHub automation setup...\n")

    # 1. Check GitHub token
    print("1. GitHub Token:")
    try:
        token = get_github_token()
        if token:
            print_success(f"Token found (length: {len(token)})")
        else:
            print_error("Token not found")
            all_ok = False
    except SystemExit:
        print_error("Token not configured")
        all_ok = False

    # 2. Check repository name
    print("\n2. Repository:")
    try:
        repo_name = get_repository_name()
        print_success(f"Repository: {repo_name}")
    except SystemExit:
        print_error("Could not determine repository")
        all_ok = False

    # 3. Check GitHub API connection
    print("\n3. GitHub API Connection:")
    try:
        g = get_github_client()
        user = g.get_user()
        print_success(f"Connected as: {user.login}")

        # Check token scopes
        # Note: This requires additional API call and token with proper scopes
        try:
            repo = g.get_repo(repo_name)
            print_success("Repository access: OK")

            # Check permissions
            if repo.permissions.push:
                print_success("Push access: OK")
            else:
                print_warning("No push access (read-only)")
        except Exception as e:
            print_error(f"Repository access failed: {e}")
            all_ok = False

    except Exception as e:
        print_error(f"Connection failed: {e}")
        all_ok = False

    # 4. Check git configuration
    print("\n4. Git Configuration:")
    try:
        branch = get_current_branch()
        if branch:
            print_success(f"Current branch: {branch}")
            if branch == "main":
                print_warning("You are on main branch")
                print_info("Create a feature branch for development")
        else:
            print_warning("Could not determine current branch")
    except Exception as e:
        print_warning(f"Git check failed: {e}")

    # 5. Summary
    print("\n" + "=" * 60)
    if all_ok:
        print_success("Setup check passed! All systems ready.")
        return True
    else:
        print_error("Setup check failed! Fix errors above.")
        print_info("\nQuick fix:")
        print("  1. Generate token: https://github.com/settings/tokens")
        print("  2. Add to .env: GITHUB_TOKEN=ghp_...")
        print("  3. Run this script again")
        return False


def main() -> None:
    """Main entry point."""
    success = check_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
