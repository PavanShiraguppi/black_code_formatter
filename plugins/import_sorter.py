"""Example import sorter plugin for Black.

This plugin demonstrates how to create a plugin that sorts imports in a customizable way.
"""

from typing import Dict, Any, List, Set, Optional
import re

from black.plugins.base import AbstractPlugin, StandardPluginMixin


class ImportSorterPlugin(AbstractPlugin, StandardPluginMixin):
    """Plugin for custom import sorting with configurable grouping and ordering."""
    
    PLUGIN_NAME = "import_sorter"
    PLUGIN_DESCRIPTION = "Sorts imports with customizable grouping and ordering rules"
    PLUGIN_VERSION = "1.0.0"
    
    def __init__(self):
        # Default configuration
        self.group_order = ["stdlib", "third_party", "first_party", "local"]
        self.stdlib_prefixes = set()  # Empty means use Python's standard library detection
        self.third_party_prefixes = set()  # Empty means detect from installed packages
        self.first_party_prefixes = set()  # Project-specific modules
        self.local_prefixes = set(["."])  # Relative imports
        self.sort_case_insensitive = True
        self.sort_by_package_then_name = True
        self.separate_groups_with_blank_line = True
        self.separate_from_imports = True
        self.line_length = 88  # Default to match Black's default
        
    def configure(self, options: Dict[str, Any]) -> None:
        """Configure the plugin with the provided options."""
        super().configure(options)
        
        # Handle special cases for sets
        for prefix_type in ["stdlib_prefixes", "third_party_prefixes", 
                           "first_party_prefixes", "local_prefixes"]:
            if prefix_type in options:
                value = options[prefix_type]
                if isinstance(value, list):
                    setattr(self, prefix_type, set(value))
                elif isinstance(value, str):
                    setattr(self, prefix_type, set(value.split(",")))
        
        # Handle other list settings
        if "group_order" in options and isinstance(options["group_order"], str):
            self.group_order = options["group_order"].split(",")

    @classmethod
    def get_default_options(cls) -> Dict[str, Any]:
        """Get default options for documentation."""
        return {
            "group_order": "stdlib,third_party,first_party,local",
            "stdlib_prefixes": "",
            "third_party_prefixes": "",
            "first_party_prefixes": "",
            "local_prefixes": ".",
            "sort_case_insensitive": True,
            "sort_by_package_then_name": True,
            "separate_groups_with_blank_line": True,
            "separate_from_imports": True,
            "line_length": 88
        }
    
    def apply_plugin(self, line_gen, node, context):
        """Apply import sorting to the node."""
        # Only process import statements and module-level nodes
        if node.type not in ("import_stmt", "import_from_stmt", "file_input"):
            return line_gen(node)
        
        # For the file_input node, we collect and sort all imports
        if node.type == "file_input":
            result = self._process_module_imports(node, line_gen, context)
            if result:
                return result
            # If no imports to sort, just continue normal processing
            return line_gen(node)
        
        # For individual import nodes, if they're being handled by module-level processing,
        # we return None to skip them (they'll be processed later)
        if context.get("import_sorting_in_progress"):
            return None
            
        # For standalone import nodes not caught by module processing
        return line_gen(node)
    
    # Implementation details would go here - see the full implementation in the examples directory
