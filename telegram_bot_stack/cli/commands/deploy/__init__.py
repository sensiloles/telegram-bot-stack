"""Deployment commands module - refactored into smaller modules."""

# Import deploy group first to avoid circular imports
# Import command modules
from telegram_bot_stack.cli.commands.deploy import monitoring, operations, secrets
from telegram_bot_stack.cli.commands.deploy.deploy import deploy

# Register subcommands from other modules
deploy.add_command(operations.up, "up")
deploy.add_command(operations.update, "update")
deploy.add_command(operations.down, "down")
deploy.add_command(operations.rollback, "rollback")
deploy.add_command(operations.history, "history")
deploy.add_command(monitoring.status, "status")
deploy.add_command(monitoring.logs, "logs")
deploy.add_command(monitoring.health, "health")
deploy.add_command(secrets.secrets, "secrets")

__all__ = ["deploy"]
