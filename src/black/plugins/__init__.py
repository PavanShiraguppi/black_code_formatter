"""Plugin system for Black.

This module provides a plugin system for Black, allowing users to extend Black's
functionality with custom plugins.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Type
import tomli
import os
import importlib
import sys
from pathlib import Path
from enum import Enum, auto
from abc import ABC, abstractmethod


class PluginState(Enum):
    """Enum representing the state of a plugin."""
    ENABLED = auto()
    DISABLED = auto()
    DEFAULT = auto()  # Use project default


@dataclass
class PluginConfig:
    """Configuration for a single plugin."""
    name: str
    state: PluginState = PluginState.DEFAULT
    options: Dict[str, Any] = field(default_factory=dict)
    version_requirement: Optional[str] = None


@dataclass
class PluginsConfig:
    """Configuration for all plugins."""
    plugin_configs: Dict[str, PluginConfig] = field(default_factory=dict)
    discovery_paths: List[str] = field(default_factory=list)
    disable_all: bool = False
    enable_by_default: bool = True


class ConfigurationManager:
    """Manages loading and merging configurations from CLI and pyproject.toml."""
    
    def __init__(self):
        self.plugins_config = PluginsConfig()
        
    def load_from_pyproject(self, path: Optional[str] = None) -> None:
        """Load plugin configuration from pyproject.toml."""
        if path is None:
            # Find pyproject.toml by walking up directories
            current_dir = Path.cwd()
            while current_dir != current_dir.parent:
                pyproject_path = current_dir / "pyproject.toml"
                if pyproject_path.exists():
                    path = str(pyproject_path)
                    break
                current_dir = current_dir.parent
        
        if not path or not Path(path).exists():
            return
            
        try:
            with open(path, "rb") as f:
                pyproject_data = tomli.load(f)
                
            # Extract plugin configuration
            black_config = pyproject_data.get("tool", {}).get("black", {})
            plugins_config = black_config.get("plugins", {})
            
            # Global plugin settings
            if "discovery_paths" in plugins_config:
                self.plugins_config.discovery_paths = plugins_config["discovery_paths"]
            
            if "disable_all" in plugins_config:
                self.plugins_config.disable_all = plugins_config["disable_all"]
                
            if "enable_by_default" in plugins_config:
                self.plugins_config.enable_by_default = plugins_config["enable_by_default"]
            
            # Individual plugin configurations
            for plugin_name, config in plugins_config.items():
                if plugin_name in ("discovery_paths", "disable_all", "enable_by_default"):
                    continue
                    
                plugin_config = PluginConfig(name=plugin_name)
                
                if isinstance(config, dict):
                    if "enabled" in config:
                        plugin_config.state = (
                            PluginState.ENABLED if config["enabled"] 
                            else PluginState.DISABLED
                        )
                    if "options" in config and isinstance(config["options"], dict):
                        plugin_config.options = config["options"]
                    if "version" in config:
                        plugin_config.version_requirement = config["version"]
                elif isinstance(config, bool):
                    # Simple enable/disable
                    plugin_config.state = (
                        PluginState.ENABLED if config 
                        else PluginState.DISABLED
                    )
                
                self.plugins_config.plugin_configs[plugin_name] = plugin_config
                
        except (tomli.TOMLDecodeError, OSError) as e:
            print(f"Error loading pyproject.toml: {e}", file=sys.stderr)
    
    def update_from_cli(self, cli_args):
        """Update plugin configuration with CLI arguments."""
        # Handle global plugin settings
        if hasattr(cli_args, "disable_all_plugins") and cli_args.disable_all_plugins:
            self.plugins_config.disable_all = True
            
        if hasattr(cli_args, "plugin_config") and cli_args.plugin_config:
            self.load_from_pyproject(cli_args.plugin_config)
            
        # Handle individual plugin settings
        if hasattr(cli_args, "plugin") and cli_args.plugin:
            for plugin_spec in cli_args.plugin:
                # Parse plugin specification (name:option1=value1,option2=value2)
                parts = plugin_spec.split(":", 1)
                plugin_name = parts[0].strip()
                
                # Create or get plugin config
                if plugin_name not in self.plugins_config.plugin_configs:
                    self.plugins_config.plugin_configs[plugin_name] = PluginConfig(name=plugin_name)
                
                plugin_config = self.plugins_config.plugin_configs[plugin_name]
                plugin_config.state = PluginState.ENABLED
                
                # Parse options if provided
                if len(parts) > 1 and parts[1]:
                    option_pairs = parts[1].split(",")
                    for pair in option_pairs:
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # Try to convert value to appropriate type
                            if value.lower() == "true":
                                value = True
                            elif value.lower() == "false":
                                value = False
                            elif value.isdigit():
                                value = int(value)
                            elif value.replace(".", "", 1).isdigit() and value.count(".") <= 1:
                                value = float(value)
                            plugin_config.options[key] = value
        
        # Handle disabled plugins
        if hasattr(cli_args, "disable_plugin") and cli_args.disable_plugin:
            for plugin_name in cli_args.disable_plugin:
                if plugin_name not in self.plugins_config.plugin_configs:
                    self.plugins_config.plugin_configs[plugin_name] = PluginConfig(name=plugin_name)
                self.plugins_config.plugin_configs[plugin_name].state = PluginState.DISABLED
