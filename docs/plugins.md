# Black Plugins

Black now supports a plugin system that allows you to extend its functionality with custom plugins.

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

# Use a specific plugin configuration file
black --plugin-config=path/to/pyproject.toml
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

## Installing Plugins

Plugins are discovered from the following locations:

1. `./plugins` (in the current directory)
2. `~/.black/plugins` (in your home directory)
3. `<python-install-path>/share/black/plugins` (system-wide)

You can also specify custom discovery paths in your configuration:

```toml
[tool.black.plugins]
discovery_paths = ["./my_plugins", "/path/to/plugins"]
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

### Plugin Interface

Plugins must implement the following interface:

- `PLUGIN_NAME`: A unique name for the plugin
- `PLUGIN_DESCRIPTION`: A description of what the plugin does
- `PLUGIN_VERSION`: The version of the plugin
- `apply_plugin(line_gen, node, context)`: The main method that applies the plugin to a node

The `apply_plugin` method takes the following arguments:

- `line_gen`: A function that generates formatted lines for a node
- `node`: The AST node being processed
- `context`: A dictionary with context information

The method should return one of the following:

- `None`: Let Black handle the node
- A list of strings: Replace Black's formatting with these lines

### Plugin Configuration

Plugins can be configured with options in the `pyproject.toml` file:

```toml
[tool.black.plugins.my_plugin]
enabled = true
options = { my_option = "custom_value" }
```

These options are passed to the plugin's `configure` method.

## Example Plugins

Black comes with several example plugins:

- `import_sorter`: Sorts imports with customizable grouping and ordering
- `string_normalizer`: Normalizes string literals with configurable quote style

You can find these plugins in the `plugins` directory of the Black repository.

## Plugin Development Tips

- Use the `StandardPluginMixin` for common utilities
- Implement `get_default_options` to document your plugin's options
- Keep your plugins focused on a single task
- Test your plugins thoroughly
- Document your plugins with docstrings and examples
