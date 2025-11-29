"""Health check utilities for project diagnostics."""

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import click


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    fixable: bool = False
    fix_command: Optional[str] = None


@dataclass
class HealthReport:
    """Complete health check report."""

    checks: List[HealthCheckResult] = field(default_factory=list)

    @property
    def errors(self) -> List[HealthCheckResult]:
        """Get all errors."""
        return [c for c in self.checks if not c.passed and c.severity == "error"]

    @property
    def warnings(self) -> List[HealthCheckResult]:
        """Get all warnings."""
        return [c for c in self.checks if not c.passed and c.severity == "warning"]

    @property
    def passed(self) -> List[HealthCheckResult]:
        """Get all passed checks."""
        return [c for c in self.checks if c.passed]

    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def add(self, result: HealthCheckResult) -> None:
        """Add a check result."""
        self.checks.append(result)


class HealthChecker:
    """Performs various health checks on the project."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize health checker.

        Args:
            project_path: Path to project directory (default: current directory)
        """
        self.project_path = project_path or Path.cwd()
        self.report = HealthReport()

    def check_python_version(self) -> HealthCheckResult:
        """Check Python version is >= 3.9."""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version >= (3, 9):
            return HealthCheckResult(
                name="Python version",
                passed=True,
                message=f"Python {version_str} (>= 3.9 required)",
                severity="info",
            )
        else:
            return HealthCheckResult(
                name="Python version",
                passed=False,
                message=f"Python {version_str} is too old (>= 3.9 required)",
                severity="error",
                fixable=False,
            )

    def check_dependencies(self) -> List[HealthCheckResult]:
        """Check if required packages are installed."""
        results = []

        # Check telegram-bot-stack
        try:
            import telegram_bot_stack

            results.append(
                HealthCheckResult(
                    name="telegram-bot-stack",
                    passed=True,
                    message=f"telegram-bot-stack v{telegram_bot_stack.__version__} installed",
                    severity="info",
                )
            )
        except ImportError:
            results.append(
                HealthCheckResult(
                    name="telegram-bot-stack",
                    passed=False,
                    message="telegram-bot-stack not installed",
                    severity="error",
                    fixable=True,
                    fix_command="pip install telegram-bot-stack",
                )
            )

        # Check python-telegram-bot
        try:
            import telegram

            version = getattr(telegram, "__version__", "unknown")
            results.append(
                HealthCheckResult(
                    name="python-telegram-bot",
                    passed=True,
                    message=f"python-telegram-bot v{version} installed",
                    severity="info",
                )
            )
        except ImportError:
            results.append(
                HealthCheckResult(
                    name="python-telegram-bot",
                    passed=False,
                    message="python-telegram-bot not installed",
                    severity="error",
                    fixable=True,
                    fix_command="pip install python-telegram-bot",
                )
            )

        return results

    def check_project_files(self) -> List[HealthCheckResult]:
        """Check if required project files exist."""
        results = []

        # Check bot.py
        bot_file = self.project_path / "bot.py"
        if bot_file.exists():
            results.append(
                HealthCheckResult(
                    name="bot.py",
                    passed=True,
                    message="bot.py found",
                    severity="info",
                )
            )
        else:
            results.append(
                HealthCheckResult(
                    name="bot.py",
                    passed=False,
                    message="bot.py not found in current directory",
                    severity="error",
                    fixable=False,
                )
            )

        # Check .env file
        env_file = self.project_path / ".env"
        if env_file.exists():
            results.append(
                HealthCheckResult(
                    name=".env file",
                    passed=True,
                    message=".env file found",
                    severity="info",
                )
            )
        else:
            results.append(
                HealthCheckResult(
                    name=".env file",
                    passed=False,
                    message=".env file not found (recommended for secrets)",
                    severity="warning",
                    fixable=True,
                    fix_command="echo 'BOT_TOKEN=your_token_here' > .env",
                )
            )

        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            results.append(
                HealthCheckResult(
                    name="requirements.txt",
                    passed=True,
                    message="requirements.txt found",
                    severity="info",
                )
            )
        else:
            results.append(
                HealthCheckResult(
                    name="requirements.txt",
                    passed=False,
                    message="requirements.txt not found (recommended for dependencies)",
                    severity="warning",
                    fixable=False,
                )
            )

        return results

    def check_configuration(self) -> List[HealthCheckResult]:
        """Check bot configuration."""
        results = []

        # Check BOT_TOKEN
        bot_token = os.getenv("BOT_TOKEN")
        if bot_token:
            # Basic validation of token format
            if ":" in bot_token and len(bot_token) > 40:
                results.append(
                    HealthCheckResult(
                        name="BOT_TOKEN",
                        passed=True,
                        message="BOT_TOKEN is set and looks valid",
                        severity="info",
                    )
                )
            else:
                results.append(
                    HealthCheckResult(
                        name="BOT_TOKEN",
                        passed=False,
                        message="BOT_TOKEN format looks invalid",
                        severity="warning",
                        fixable=False,
                    )
                )
        else:
            results.append(
                HealthCheckResult(
                    name="BOT_TOKEN",
                    passed=False,
                    message="BOT_TOKEN not set in environment",
                    severity="error",
                    fixable=False,
                )
            )

        # Check deployment config if exists
        deploy_config = self.project_path / "deploy.yaml"
        if deploy_config.exists():
            results.append(
                HealthCheckResult(
                    name="deploy.yaml",
                    passed=True,
                    message="deploy.yaml found",
                    severity="info",
                )
            )

        return results

    def check_security(self) -> List[HealthCheckResult]:
        """Check for common security issues."""
        results = []

        # Check if .env is in .gitignore
        gitignore = self.project_path / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if ".env" in content:
                results.append(
                    HealthCheckResult(
                        name=".env in .gitignore",
                        passed=True,
                        message=".env is properly ignored in git",
                        severity="info",
                    )
                )
            else:
                results.append(
                    HealthCheckResult(
                        name=".env in .gitignore",
                        passed=False,
                        message=".env not found in .gitignore (security risk!)",
                        severity="error",
                        fixable=True,
                        fix_command="echo '.env' >> .gitignore",
                    )
                )
        else:
            results.append(
                HealthCheckResult(
                    name=".gitignore",
                    passed=False,
                    message=".gitignore not found",
                    severity="warning",
                    fixable=True,
                    fix_command="echo '.env' > .gitignore",
                )
            )

        # Check for hardcoded tokens in bot.py
        bot_file = self.project_path / "bot.py"
        if bot_file.exists():
            content = bot_file.read_text()
            # Simple pattern matching for tokens
            if (
                "token=" in content.lower()
                and ("'" in content or '"' in content)
                and ":" in content
            ):
                # Check if it's not using os.getenv or similar
                if "os.getenv" not in content and "os.environ" not in content:
                    results.append(
                        HealthCheckResult(
                            name="Hardcoded tokens",
                            passed=False,
                            message="Possible hardcoded token detected in bot.py",
                            severity="error",
                            fixable=False,
                        )
                    )

        return results

    def check_deployment(self) -> List[HealthCheckResult]:
        """Check deployment-related dependencies."""
        results = []

        # Check Docker
        docker_available = shutil.which("docker") is not None
        if docker_available:
            try:
                result = subprocess.run(
                    ["docker", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    results.append(
                        HealthCheckResult(
                            name="Docker",
                            passed=True,
                            message=f"{version}",
                            severity="info",
                        )
                    )
                else:
                    results.append(
                        HealthCheckResult(
                            name="Docker",
                            passed=False,
                            message="Docker installed but not working",
                            severity="warning",
                            fixable=False,
                        )
                    )
            except Exception:
                results.append(
                    HealthCheckResult(
                        name="Docker",
                        passed=False,
                        message="Docker check failed",
                        severity="warning",
                        fixable=False,
                    )
                )
        else:
            results.append(
                HealthCheckResult(
                    name="Docker",
                    passed=False,
                    message="Docker not installed (required for deployment)",
                    severity="warning",
                    fixable=False,
                )
            )

        # Check SSH
        ssh_available = shutil.which("ssh") is not None
        if ssh_available:
            results.append(
                HealthCheckResult(
                    name="SSH",
                    passed=True,
                    message="SSH client available",
                    severity="info",
                )
            )
        else:
            results.append(
                HealthCheckResult(
                    name="SSH",
                    passed=False,
                    message="SSH client not found (required for VPS deployment)",
                    severity="warning",
                    fixable=False,
                )
            )

        return results

    def run_all_checks(self, categories: Optional[List[str]] = None) -> HealthReport:
        """Run all health checks.

        Args:
            categories: List of categories to check (None = all)
                Options: dependencies, config, files, security, deployment

        Returns:
            HealthReport with all results
        """
        all_categories = {
            "python": self.check_python_version,
            "dependencies": self.check_dependencies,
            "files": self.check_project_files,
            "config": self.check_configuration,
            "security": self.check_security,
            "deployment": self.check_deployment,
        }

        if categories:
            checks_to_run = {k: v for k, v in all_categories.items() if k in categories}
        else:
            checks_to_run = all_categories

        for _, check_func in checks_to_run.items():
            result = check_func()
            if isinstance(result, list):
                for r in result:
                    self.report.add(r)
            else:
                # Ensure result is HealthCheckResult
                if isinstance(result, HealthCheckResult):
                    self.report.add(result)

        return self.report


def print_health_report(report: HealthReport, verbose: bool = False) -> None:
    """Print health report to console.

    Args:
        report: HealthReport to print
        verbose: Show all checks including passed ones
    """
    click.echo()

    # Group by category
    categories: Dict[str, List[HealthCheckResult]] = {}
    for check in report.checks:
        # Extract category from check name
        category = "General"
        if "Docker" in check.name or "SSH" in check.name:
            category = "Deployment"
        elif "BOT_TOKEN" in check.name or "deploy.yaml" in check.name:
            category = "Configuration"
        elif ".env" in check.name or "token" in check.message.lower():
            category = "Security"
        elif ".py" in check.name or "requirements" in check.name:
            category = "Files"
        elif "telegram-bot" in check.name or "Python" in check.name:
            category = "Dependencies"

        if category not in categories:
            categories[category] = []
        categories[category].append(check)

    # Print by category
    for category, checks in categories.items():
        errors = [c for c in checks if not c.passed and c.severity == "error"]
        warnings = [c for c in checks if not c.passed and c.severity == "warning"]
        passed = [c for c in checks if c.passed]

        # Determine category status
        if errors:
            status = "❌"
            color = "red"
        elif warnings:
            status = "⚠️"
            color = "yellow"
        else:
            status = "✅"
            color = "green"

        click.secho(f"\n{status} {category}", fg=color, bold=True)

        # Show all checks if verbose, otherwise only issues
        if verbose:
            for check in checks:
                if check.passed:
                    click.secho(f"   ✓ {check.message}", fg="green")
                elif check.severity == "error":
                    click.secho(f"   ✗ {check.message}", fg="red")
                else:
                    click.secho(f"   ⚠ {check.message}", fg="yellow")
        else:
            # Show errors and warnings
            for check in errors:
                click.secho(f"   ✗ {check.message}", fg="red")
                if check.fix_command:
                    click.secho(f"      Fix: {check.fix_command}", fg="blue", dim=True)

            for check in warnings:
                click.secho(f"   ⚠ {check.message}", fg="yellow")
                if check.fix_command:
                    click.secho(f"      Fix: {check.fix_command}", fg="blue", dim=True)

            # Show count of passed checks
            if passed:
                click.secho(f"   ✓ {len(passed)} check(s) passed", fg="green", dim=True)

    # Summary
    click.echo("\n" + "=" * 70)

    total_errors = len(report.errors)
    total_warnings = len(report.warnings)
    total_passed = len(report.passed)

    if total_errors == 0 and total_warnings == 0:
        click.secho(
            f"\n✅ All {total_passed} checks passed! Your project is healthy.",
            fg="green",
            bold=True,
        )
    else:
        if total_errors > 0:
            click.secho(
                f"\n❌ Found {total_errors} error(s)",
                fg="red",
                bold=True,
            )

        if total_warnings > 0:
            click.secho(
                f"⚠️  Found {total_warnings} warning(s)",
                fg="yellow",
                bold=True,
            )

        if total_passed > 0:
            click.secho(
                f"✅ {total_passed} check(s) passed",
                fg="green",
            )

    click.echo("=" * 70 + "\n")


def auto_fix_issues(report: HealthReport, dry_run: bool = False) -> int:
    """Attempt to auto-fix fixable issues.

    Args:
        report: HealthReport with issues to fix
        dry_run: If True, only show what would be fixed

    Returns:
        Number of issues fixed
    """
    fixable = [c for c in report.checks if not c.passed and c.fixable and c.fix_command]

    if not fixable:
        click.secho("No auto-fixable issues found.", fg="yellow")
        return 0

    click.secho(f"\n🔧 Found {len(fixable)} fixable issue(s):", fg="cyan", bold=True)

    fixed = 0
    for check in fixable:
        click.echo(f"\n  • {check.message}")
        click.secho(f"    Command: {check.fix_command}", fg="blue")

        if dry_run:
            click.secho("    [DRY RUN - not executed]", fg="yellow", dim=True)
            continue

        if not check.fix_command:
            continue

        try:
            # Execute fix command
            subprocess.run(check.fix_command, shell=True, check=True)
            click.secho("    ✅ Fixed", fg="green")
            fixed += 1
        except subprocess.CalledProcessError as e:
            click.secho(f"    ❌ Failed: {e}", fg="red")

    if dry_run:
        click.echo(f"\n{len(fixable)} issue(s) would be fixed (use --fix to apply)")
    else:
        click.secho(
            f"\n✅ Fixed {fixed}/{len(fixable)} issue(s)",
            fg="green",
            bold=True,
        )

    return fixed
