"""Plugin registry for Black.

This module provides the plugin registry for Black, which manages the discovery,
loading, and configuration of plugins.
"""

import os
import sys
import importlib
from typing import Dict, List, Optional, Any, Type

from black.plugins import PluginsConfig, PluginConfig, PluginState


class PluginRegistry:
    """Registry for managing available and enabled plugins."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.available_plugins = {}
            cls._instance.enabled_plugins = {}
            cls._instance.plugin_classes = {}
        return cls._instance
    
    def discover_plugins(self, paths: Optional[List[str]] = None) -> None:
        """Discover available plugins from specified paths."""
        if not paths:
            # Default discovery paths
            paths = [
                "./plugins",
                os.path.expanduser("~/.black/plugins"),
                os.path.join(sys.prefix, "share", "black", "plugins"),
            ]
        
        # Add paths to Python module search path temporarily
        original_path = sys.path.copy()
        for path in paths:
            if path not in sys.path and os.path.exists(path):
                sys.path.insert(0, path)
        
        try:
            # Look for plugin modules in each path
            for path in paths:
                if not os.path.exists(path):
                    continue
                
                # Find Python files that might be plugins
                for item in os.listdir(path):
                    if item.endswith(".py") and not item.startswith("_"):
                        module_name = item[:-3]  # Remove .py extension
                        try:
                            # Try to import the module
                            module = importlib.import_module(module_name)
                            
                            # Look for plugin classes in the module
                            for attr_name in dir(module):
                                attr = getattr(module, attr_name)
                                if (
                                    isinstance(attr, type) and 
                                    attr_name not in ("AbstractPlugin", "StandardPluginMixin") and
                                    hasattr(attr, "PLUGIN_NAME") and
                                    hasattr(attr, "apply_plugin")
                                ):
                                    plugin_name = getattr(attr, "PLUGIN_NAME")
                                    self.plugin_classes[plugin_name] = attr
                        except ImportError as e:
                            print(f"Failed to import potential plugin {module_name}: {e}", file=sys.stderr)
        finally:
            # Restore original Python module search path
            sys.path = original_path
    
    def configure_plugins(self, config: PluginsConfig) -> None:
        """Configure plugins based on the provided configuration."""
        self.enabled_plugins.clear()
        
        if config.disable_all:
            return
        
        # Discover plugins if needed
        if not self.plugin_classes and config.discovery_paths:
            self.discover_plugins(config.discovery_paths)
        elif not self.plugin_classes:
            self.discover_plugins()
        
        # Initialize enabled plugins
        for name, plugin_class in self.plugin_classes.items():
            plugin_config = config.plugin_configs.get(name, PluginConfig(name=name))
            
            # Determine if plugin should be enabled
            if plugin_config.state == PluginState.ENABLED:
                enabled = True
            elif plugin_config.state == PluginState.DISABLED:
                enabled = False
            else:  # DEFAULT
                enabled = config.enable_by_default
            
            if enabled:
                try:
                    # Initialize plugin with its configuration
                    plugin_instance = plugin_class()
                    plugin_instance.configure(plugin_config.options)
                    self.enabled_plugins[name] = plugin_instance
                except Exception as e:
                    print(f"Failed to initialize plugin {name}: {e}", file=sys.stderr)
    
    def get_plugin(self, name: str):
        """Get an enabled plugin by name."""
        return self.enabled_plugins.get(name)
    
    def get_all_enabled_plugins(self):
        """Get all enabled plugins."""
        return list(self.enabled_plugins.values())
