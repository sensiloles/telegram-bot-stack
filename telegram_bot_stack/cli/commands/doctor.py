"""Doctor command for project health diagnostics."""

import sys
from pathlib import Path
from typing import List, Optional

import click

from telegram_bot_stack.cli.utils.health_checks import (
    HealthChecker,
    auto_fix_issues,
    print_health_report,
)


@click.command()
@click.option(
    "--check",
    "categories",
    multiple=True,
    type=click.Choice(
        ["python", "dependencies", "files", "config", "security", "deployment"],
        case_sensitive=False,
    ),
    help="Run specific checks only (can be used multiple times)",
)
@click.option(
    "--fix",
    is_flag=True,
    help="Automatically fix issues where possible",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be fixed without applying changes (use with --fix)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show all checks including passed ones",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Exit with error code if any issues found",
)
def doctor(
    categories: tuple,
    fix: bool,
    dry_run: bool,
    verbose: bool,
    strict: bool,
) -> None:
    """Run health checks on your bot project.

    Diagnoses common issues with dependencies, configuration, security,
    and deployment setup. Can automatically fix many issues.

    \b
    Examples:
        # Run all health checks
        telegram-bot-stack doctor

        # Check specific categories
        telegram-bot-stack doctor --check dependencies --check config

        # Show all checks including passed ones
        telegram-bot-stack doctor --verbose

        # Auto-fix issues
        telegram-bot-stack doctor --fix

        # Preview fixes without applying
        telegram-bot-stack doctor --fix --dry-run

        # Use in CI/CD (exit with error if issues found)
        telegram-bot-stack doctor --strict

    \b
    Check Categories:
        python       - Python version
        dependencies - Package installation
        files        - Required project files
        config       - Bot configuration
        security     - Security best practices
        deployment   - Deployment tools (Docker, SSH)
    """
    click.secho("\n🏥 Running health checks...", fg="cyan", bold=True)

    # Convert tuple to list for easier handling
    check_list: Optional[List[str]] = list(categories) if categories else None

    # Run health checks
    checker = HealthChecker(project_path=Path.cwd())
    report = checker.run_all_checks(categories=check_list)

    # Print report
    print_health_report(report, verbose=verbose)

    # Auto-fix if requested
    if fix:
        click.echo()
        fixed_count = auto_fix_issues(report, dry_run=dry_run)

        if fixed_count > 0 and not dry_run:
            click.secho(
                "\n💡 Tip: Run 'telegram-bot-stack doctor' again to verify fixes",
                fg="cyan",
            )

    # Exit with error if strict mode and there are issues
    if strict and (report.has_errors or len(report.warnings) > 0):
        sys.exit(1)

    # Exit with error if there are critical errors (even without strict)
    if report.has_errors:
        sys.exit(1)
