"""Create a new bot from template."""

import shutil
import sys
from pathlib import Path

import click


@click.command()
@click.argument("name")
@click.option(
    "--template",
    type=click.Choice(["basic", "counter", "menu", "advanced"]),
    default="basic",
    help="Bot template to use (default: basic)",
)
def new(name: str, template: str) -> None:
    """Create a new bot from a template.

    Available templates:
    - basic: Simple echo bot
    - counter: Bot with state management
    - menu: Bot with interactive menus
    - advanced: Full-featured bot with all best practices

    Example:

        telegram-bot-stack new my-bot --template counter
    """
    project_path = Path.cwd() / name

    # Check if project already exists
    if project_path.exists():
        click.secho(f"❌ Error: Directory '{name}' already exists", fg="red")
        sys.exit(1)

    click.secho(f"\n🚀 Creating bot from template: {template}\n", fg="cyan", bold=True)

    # Get template directory
    cli_dir = Path(__file__).parent.parent
    template_dir = cli_dir / "templates" / template

    if not template_dir.exists():
        click.secho(
            f"❌ Error: Template '{template}' not found at {template_dir}",
            fg="red",
        )
        sys.exit(1)

    try:
        # Copy template
        shutil.copytree(template_dir, project_path)
        click.secho(f"✅ Created project from template: {template}", fg="green")

        # Success message
        click.secho("\n" + "=" * 70, fg="green")
        click.secho("🎉 Success! Your bot project is ready!", fg="green", bold=True)
        click.secho("=" * 70 + "\n", fg="green")

        click.echo("📋 Next steps:\n")
        click.secho(f"  1. cd {name}", fg="cyan")
        click.secho("  2. Read README.md for setup instructions", fg="cyan")
        click.secho('  3. echo "BOT_TOKEN=your_token_here" > .env', fg="cyan")
        click.secho("  4. python bot.py", fg="cyan")

        click.echo(
            "\n💡 Tip: Use 'telegram-bot-stack init' for full dev environment setup\n"
        )

    except Exception as e:
        click.secho(f"\n❌ Error creating project: {e}", fg="red")
        if project_path.exists():
            shutil.rmtree(project_path)
        sys.exit(1)
