"""Schema for plugin configuration.

This module provides the JSON schema for plugin configuration in pyproject.toml.
"""

PLUGIN_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "oneOf": [
            {"type": "boolean"},
            {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "options": {"type": "object"},
                    "version": {"type": "string"}
                },
                "additionalProperties": False
            }
        ]
    },
    "properties": {
        "discovery_paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of paths to search for plugins."
        },
        "disable_all": {
            "type": "boolean",
            "description": "Disable all plugins.",
            "default": False
        },
        "enable_by_default": {
            "type": "boolean",
            "description": "Enable plugins by default if not explicitly configured.",
            "default": True
        }
    }
}
