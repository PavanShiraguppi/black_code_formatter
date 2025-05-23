"""Base classes for Black plugins.

This module provides the base classes for creating Black plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AbstractPlugin(ABC):
    """Base class for all plugins."""
    
    # Plugin metadata - should be overridden by subclasses
    PLUGIN_NAME = ""
    PLUGIN_DESCRIPTION = ""
    PLUGIN_VERSION = "0.1.0"
    
    @abstractmethod
    def apply_plugin(self, line_gen, node, context) -> Any:
        """Apply the plugin to the formatting process.
        
        Args:
            line_gen: The line generator function
            node: The AST node being processed
            context: The formatting context
            
        Returns:
            The result of the plugin application, which may be:
            - None: to indicate the plugin didn't modify anything
            - A list of strings: the modified lines
            - Any other value that the formatter expects
        """
        pass
    
    def configure(self, options: Dict[str, Any]) -> None:
        """Configure the plugin with the provided options."""
        for key, value in options.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_default_options(cls) -> Dict[str, Any]:
        """Get the default options for this plugin."""
        return {}


class StandardPluginMixin:
    """Common utilities for plugins."""
    
    def validate_options(self, options: Dict[str, Any]) -> Dict[str, str]:
        """Validate the plugin options and return any errors."""
        errors = {}
        for key, value in options.items():
            if not hasattr(self, key):
                errors[key] = f"Unknown option: {key}"
        return errors
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about this plugin."""
        return {
            "name": self.PLUGIN_NAME,
            "description": self.PLUGIN_DESCRIPTION,
            "version": self.PLUGIN_VERSION,
            "options": self.get_default_options()
        }
