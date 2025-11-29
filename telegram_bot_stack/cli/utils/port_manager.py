"""Port management utilities for multi-bot deployments."""

from typing import List, Optional, Set

from fabric import Connection
from rich.console import Console

console = Console()


def get_used_ports(conn: Connection) -> Set[int]:
    """Get all ports currently in use on the VPS.

    Args:
        conn: Fabric Connection object

    Returns:
        Set of port numbers currently in use
    """
    try:
        # Get all listening ports (TCP and UDP)
        result = conn.run(
            "ss -tuln | awk 'NR>1 {print $5}' | sed 's/.*://' | sort -u",
            hide=True,
            warn=True,
            pty=False,
            in_stream=False,
        )

        if not result or not result.stdout:
            return set()

        ports = set()
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and line.isdigit():
                ports.add(int(line))

        return ports

    except Exception as e:
        console.print(f"[yellow]⚠️  Warning: Could not check used ports: {e}[/yellow]")
        return set()


def find_available_port(
    conn: Connection, start_port: int = 8080, end_port: int = 9000
) -> Optional[int]:
    """Find an available port in the specified range.

    Args:
        conn: Fabric Connection object
        start_port: Starting port number (default: 8080)
        end_port: Ending port number (default: 9000)

    Returns:
        First available port number, or None if no ports available
    """
    used_ports = get_used_ports(conn)

    for port in range(start_port, end_port + 1):
        if port not in used_ports:
            return port

    return None


def check_port_available(conn: Connection, port: int) -> bool:
    """Check if a specific port is available.

    Args:
        conn: Fabric Connection object
        port: Port number to check

    Returns:
        True if port is available, False if in use
    """
    used_ports = get_used_ports(conn)
    return port not in used_ports


def get_bot_ports(conn: Connection, bot_name: str) -> List[int]:
    """Get ports used by a specific bot.

    Args:
        conn: Fabric Connection object
        bot_name: Name of the bot

    Returns:
        List of port numbers used by the bot
    """
    try:
        # Get ports from docker-compose.yml if it exists
        result = conn.run(
            f"grep -E 'ports:|expose:' /opt/{bot_name}/docker-compose.yml 2>/dev/null || true",
            hide=True,
            warn=True,
            pty=False,
            in_stream=False,
        )

        if not result or not result.stdout:
            return []

        ports = []
        for line in result.stdout.strip().split("\n"):
            # Parse port mappings like "- 8080:8080" or "- 8080"
            line = line.strip()
            if line.startswith("-"):
                port_spec = line.split("-", 1)[1].strip().strip("\"'")
                # Handle "host:container" or just "port"
                if ":" in port_spec:
                    host_port = port_spec.split(":")[0]
                    if host_port.isdigit():
                        ports.append(int(host_port))
                elif port_spec.isdigit():
                    ports.append(int(port_spec))

        return ports

    except Exception as e:
        console.print(f"[yellow]⚠️  Warning: Could not check bot ports: {e}[/yellow]")
        return []


def detect_port_conflicts(
    conn: Connection, new_bot_ports: List[int], exclude_bot: Optional[str] = None
) -> List[int]:
    """Detect port conflicts with existing bots.

    Args:
        conn: Fabric Connection object
        new_bot_ports: Ports that the new bot wants to use
        exclude_bot: Bot name to exclude from conflict detection (e.g., current bot for updates)

    Returns:
        List of conflicting port numbers
    """
    if not new_bot_ports:
        return []

    used_ports = get_used_ports(conn)

    # If excluding a bot, remove its ports from the used set
    if exclude_bot:
        bot_ports = get_bot_ports(conn, exclude_bot)
        used_ports = used_ports - set(bot_ports)

    conflicts = [port for port in new_bot_ports if port in used_ports]
    return conflicts


def suggest_alternative_ports(
    conn: Connection, requested_ports: List[int]
) -> List[int]:
    """Suggest alternative ports for conflicting ports.

    Args:
        conn: Fabric Connection object
        requested_ports: List of requested port numbers

    Returns:
        List of suggested alternative port numbers (same length as input)
    """
    used_ports = get_used_ports(conn)
    suggestions = []

    for port in requested_ports:
        if port not in used_ports:
            suggestions.append(port)
        else:
            # Find next available port in range
            alternative = find_available_port(
                conn, start_port=port, end_port=port + 1000
            )
            if alternative:
                suggestions.append(alternative)
            else:
                # Fallback to wider range
                alternative = find_available_port(conn, start_port=8080, end_port=9999)
                suggestions.append(alternative if alternative else port + 1000)

    return suggestions
