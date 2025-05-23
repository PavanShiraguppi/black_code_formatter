"""CLI argument handling for Black plugins.

This module provides functions for adding plugin-related command-line arguments
to Black's argument parser.
"""

from typing import Any


def add_plugin_arguments(parser: Any) -> None:
    """Add plugin-related arguments to an ArgumentParser.
    
    Args:
        parser: The argument parser to add plugin arguments to.
    """
    group = parser.add_argument_group("Plugin Configuration")
    
    group.add_argument(
        "--plugin",
        metavar="NAME[:OPTION1=VALUE1,OPTION2=VALUE2,...]",
        action="append",
        help="Enable plugin with optional configuration parameters. Can be used multiple times."
    )
    
    group.add_argument(
        "--list-plugins",
        action="store_true",
        help="List available plugins with descriptions and default settings."
    )
    
    group.add_argument(
        "--disable-plugin",
        metavar="NAME",
        action="append",
        help="Explicitly disable a specific plugin."
    )
    
    group.add_argument(
        "--disable-all-plugins",
        action="store_true",
        help="Run without any plugins enabled."
    )
    
    group.add_argument(
        "--plugin-config",
        metavar="PATH",
        help="Path to an external plugin configuration file (pyproject.toml format)."
    )
