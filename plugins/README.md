# Black Plugins

This directory contains example plugins for Black.

## Installing Plugins

To use a plugin, copy it to one of the following locations:

- `./plugins` (in the current directory)
- `~/.black/plugins` (in your home directory)
- `<python-install-path>/share/black/plugins` (system-wide)

## Using Plugins

Plugins can be enabled in several ways:

### Command Line

```bash
# Enable a plugin
black --plugin=import_sorter

# Enable a plugin with options
black --plugin=import_sorter:group_order=stdlib,third_party,first_party,local

# Disable a specific plugin
black --disable-plugin=import_sorter

# Disable all plugins
black --disable-all-plugins

# List available plugins
black --list-plugins
```

### Configuration File

In your `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ["py38"]

[tool.black.plugins]
# Global plugin settings
discovery_paths = ["./plugins", "~/.black/plugins"]
enable_by_default = true
disable_all = false

# Simple enable/disable
import_sorter = true

# Configure with options
[tool.black.plugins.string_normalizer]
enabled = true
options = { quotes = "double", docstring_style = "google" }
version = ">=1.0.0"

# Explicitly disable a plugin
[tool.black.plugins.type_hint_expander]
enabled = false
```

## Creating Plugins

To create a plugin, create a Python file with a class that inherits from `AbstractPlugin`:

```python
from black.plugins.base import AbstractPlugin, StandardPluginMixin

class MyPlugin(AbstractPlugin, StandardPluginMixin):
    PLUGIN_NAME = "my_plugin"
    PLUGIN_DESCRIPTION = "Description of my plugin"
    PLUGIN_VERSION = "1.0.0"
    
    def __init__(self):
        # Default configuration
        self.my_option = "default_value"
    
    @classmethod
    def get_default_options(cls):
        return {
            "my_option": "default_value"
        }
    
    def apply_plugin(self, line_gen, node, context):
        # Your plugin logic here
        # Return None to let Black handle the node
        # Return a list of strings to replace Black's formatting
        return line_gen(node)
```

See the example plugins in this directory for more details.
