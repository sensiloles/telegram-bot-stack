"""IDE configuration utilities."""

import json
from pathlib import Path

import click


def create_vscode_settings(project_path: Path, python_version: str = "3.9") -> None:
    """Create VS Code settings for the project.

    Args:
        project_path: Path to the project directory
        python_version: Python version for the project
    """
    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # settings.json
    settings = {
        "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
        "python.linting.enabled": True,
        "python.linting.ruffEnabled": True,
        "python.formatting.provider": "none",
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll": "explicit",
                "source.organizeImports": "explicit",
            },
        },
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
        "python.testing.pytestArgs": ["tests"],
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            "**/.pytest_cache": True,
            "**/.mypy_cache": True,
            "**/.ruff_cache": True,
        },
    }

    settings_file = vscode_dir / "settings.json"
    settings_file.write_text(json.dumps(settings, indent=2))

    # extensions.json (recommended extensions)
    extensions = {
        "recommendations": [
            "charliermarsh.ruff",
            "ms-python.python",
            "ms-python.vscode-pylance",
        ]
    }

    extensions_file = vscode_dir / "extensions.json"
    extensions_file.write_text(json.dumps(extensions, indent=2))

    click.secho("  ✅ Created VS Code configuration", fg="green")


def create_pycharm_settings(project_path: Path) -> None:
    """Create PyCharm/IntelliJ IDEA settings for the project.

    Args:
        project_path: Path to the project directory
    """
    idea_dir = project_path / ".idea"
    idea_dir.mkdir(exist_ok=True)

    # misc.xml (Python interpreter)
    misc_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Python (venv)" project-jdk-type="Python SDK" />
</project>
"""

    (idea_dir / "misc.xml").write_text(misc_xml)

    # inspectionProfiles/profiles_settings.xml
    profiles_dir = idea_dir / "inspectionProfiles"
    profiles_dir.mkdir(exist_ok=True)

    profiles_xml = """<component name="InspectionProjectProfileManager">
  <settings>
    <option name="USE_PROJECT_PROFILE" value="false" />
    <version value="1.0" />
  </settings>
</component>
"""

    (profiles_dir / "profiles_settings.xml").write_text(profiles_xml)

    click.secho("  ✅ Created PyCharm configuration", fg="green")
