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
    import sys

    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Determine Python version for site-packages path
    # Use actual Python version if available, otherwise use python_version parameter
    py_major_minor = (
        python_version
        if python_version
        else f"{sys.version_info.major}.{sys.version_info.minor}"
    )

    # Build extraPaths for Pylance
    extra_paths = [
        f"${{workspaceFolder}}/venv/lib/python{py_major_minor}/site-packages"
    ]

    # Try to find telegram-bot-stack source path (for editable installs)
    try:
        # Check if telegram-bot-stack is installed in editable mode
        site_packages = (
            project_path / "venv" / "lib" / f"python{py_major_minor}" / "site-packages"
        )
        pth_files = list(site_packages.glob("__editable__*telegram_bot_stack*.pth"))

        if pth_files:
            # Found editable install, try to find the source directory
            # Look for telegram-bot-stack in common locations
            possible_paths = [
                project_path.parent / "telegram-bot-stack",  # Sibling directory
                project_path.parent.parent / "telegram-bot-stack",  # Parent's sibling
                Path.cwd().parent
                / "telegram-bot-stack",  # Current working directory's sibling
            ]

            for possible_path in possible_paths:
                if (
                    possible_path.exists()
                    and (possible_path / "telegram_bot_stack").exists()
                ):
                    # Normalize path to avoid ../ in settings
                    extra_paths.append(str(possible_path.resolve()))
                    break
    except Exception:
        # If detection fails, just use site-packages
        pass

    # settings.json (based on telegram-bot-stack working configuration)
    settings = {
        # Python interpreter
        "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
        # Ruff configuration
        "ruff.enable": True,
        "ruff.importStrategy": "fromEnvironment",
        "ruff.path": ["${workspaceFolder}/venv/bin/ruff"],
        # Python analysis (Pylance)
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.diagnosticMode": "workspace",
        "python.analysis.autoImportCompletions": True,
        "python.analysis.useLibraryCodeForTypes": True,
        "python.analysis.extraPaths": extra_paths,
        "python.analysis.diagnosticSeverityOverrides": {
            "reportMissingImports": "warning",
            "reportMissingTypeStubs": "none",
            "reportGeneralTypeIssues": "none",
        },
        # Disable old linting (use ruff instead)
        "python.linting.enabled": False,
        "python.linting.pylintEnabled": False,
        "python.linting.flake8Enabled": False,
        "python.formatting.provider": "none",
        # Editor settings
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.organizeImports.ruff": "explicit",
            "source.fixAll.ruff": "explicit",
        },
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports.ruff": "explicit",
                "source.fixAll.ruff": "explicit",
            },
        },
        # Testing
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
        "python.testing.pytestArgs": ["tests"],
        # File exclusions
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            "**/.pytest_cache": True,
            "**/.mypy_cache": True,
            "**/.ruff_cache": True,
            "**/*.egg-info": True,
        },
        "files.insertFinalNewline": True,
    }

    settings_file = vscode_dir / "settings.json"
    settings_file.write_text(json.dumps(settings, indent=2))

    # extensions.json (recommended extensions)
    extensions = {
        "recommendations": [
            "charliermarsh.ruff",
            "ms-python.python",
            "ms-python.vscode-pylance",
            "redhat.vscode-yaml",
        ]
    }

    extensions_file = vscode_dir / "extensions.json"
    extensions_file.write_text(json.dumps(extensions, indent=2))

    # Create pyrightconfig.json for better Pylance support with editable installs
    pyright_config = {
        "venvPath": ".",
        "venv": "venv",
        "extraPaths": extra_paths,
        "reportMissingImports": "warning",
        "reportMissingTypeStubs": False,
        "pythonVersion": py_major_minor,
        "pythonPlatform": "Darwin" if sys.platform == "darwin" else "Linux",
    }

    pyright_file = project_path / "pyrightconfig.json"
    pyright_file.write_text(json.dumps(pyright_config, indent=2))

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
