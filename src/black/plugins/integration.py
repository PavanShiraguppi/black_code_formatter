"""Integration of the plugin system with Black's formatting pipeline.

This module provides functions to integrate the plugin system with Black's
formatting pipeline.
"""

import sys
from typing import Any, Dict, List, Optional, Callable
from blib2to3.pytree import Node

from black.linegen import LineGenerator
from black.nodes import Visitor
from black.mode import Mode

from black.plugins.registry import PluginRegistry


class PluginLineGenerator(Visitor[List[str]]):
    """Line generator that applies plugins to the formatting process."""

    def __init__(
        self,
        base_line_gen: LineGenerator,
        mode: Mode,
        context: Dict[str, Any] = None
    ) -> None:
        """Initialize the plugin line generator.

        Args:
            base_line_gen: The base line generator to use
            mode: The formatting mode
            context: The formatting context
        """
        self.base_line_gen = base_line_gen
        self.mode = mode
        self.context = context or {}
        self.registry = PluginRegistry()

    def visit(self, node: Node) -> List[str]:
        """Visit a node and apply plugins to it."""
        # Create a line generator function for this node
        def line_gen(node: Node) -> List[str]:
            lines = []
            for line in self.base_line_gen.visit(node):
                lines.append(line)
            return lines

        # Apply plugins to the node
        result = self._apply_plugins(line_gen, node)
        if result is not None:
            return result

        # If no plugin handled the node, use the base line generator
        return line_gen(node)

    def _apply_plugins(self, line_gen: Callable, node: Node) -> Optional[List[str]]:
        """Apply all enabled plugins to a node.

        Args:
            line_gen: The line generator function
            node: The node to apply plugins to

        Returns:
            The result of applying plugins, or None if no plugin handled the node
        """
        plugins = self.registry.get_all_enabled_plugins()
        if not plugins:
            return None

        # Apply plugins in order
        for plugin in plugins:
            try:
                result = plugin.apply_plugin(line_gen, node, self.context)
                if result is not None:
                    return result
            except Exception as e:
                # Log the error but continue with other plugins
                print(f"Error applying plugin {plugin.PLUGIN_NAME}: {e}", file=sys.stderr)

        return None


def create_plugin_line_generator(
    base_line_gen: LineGenerator,
    mode: Mode,
    context: Dict[str, Any] = None
) -> PluginLineGenerator:
    """Create a plugin line generator.

    Args:
        base_line_gen: The base line generator to use
        mode: The formatting mode
        context: The formatting context

    Returns:
        A plugin line generator
    """
    return PluginLineGenerator(base_line_gen, mode, context)


def initialize_plugins(config_path: Optional[str] = None, cli_args: Any = None) -> None:
    """Initialize the plugin system.

    Args:
        config_path: Path to a configuration file
        cli_args: Command-line arguments
    """
    from black.plugins import ConfigurationManager

    # Initialize configuration
    config_manager = ConfigurationManager()
    if config_path:
        config_manager.load_from_pyproject(config_path)
    else:
        config_manager.load_from_pyproject()

    # Update configuration with CLI arguments if provided
    if cli_args:
        config_manager.update_from_cli(cli_args)

    # Configure plugins
    registry = PluginRegistry()
    registry.configure_plugins(config_manager.plugins_config)
