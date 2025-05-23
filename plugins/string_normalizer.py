"""Example string normalizer plugin for Black.

This plugin demonstrates how to create a plugin that normalizes string literals
in a customizable way.
"""

from typing import Dict, Any, List, Optional

from black.plugins.base import AbstractPlugin, StandardPluginMixin


class StringNormalizerPlugin(AbstractPlugin, StandardPluginMixin):
    """Plugin for normalizing string literals with configurable options."""
    
    PLUGIN_NAME = "string_normalizer"
    PLUGIN_DESCRIPTION = "Normalizes string literals with configurable quote style and docstring format"
    PLUGIN_VERSION = "1.0.0"
    
    def __init__(self):
        # Default configuration
        self.quotes = "double"  # Options: "single", "double", "default" (use Black's default)
        self.docstring_style = "default"  # Options: "default", "google", "numpy", "sphinx"
        self.normalize_f_strings = True
        self.normalize_docstrings = True
        self.normalize_comments = False
        
    @classmethod
    def get_default_options(cls) -> Dict[str, Any]:
        """Get default options for documentation."""
        return {
            "quotes": "double",  # Options: "single", "double", "default" (use Black's default)
            "docstring_style": "default",  # Options: "default", "google", "numpy", "sphinx"
            "normalize_f_strings": True,
            "normalize_docstrings": True,
            "normalize_comments": False,
        }
    
    def apply_plugin(self, line_gen, node, context):
        """Apply string normalization to the node."""
        # Only process string nodes
        if node.type not in ("string", "strings"):
            return line_gen(node)
        
        # Skip docstrings if configured to do so
        if not self.normalize_docstrings and context.get("is_docstring", False):
            return line_gen(node)
        
        # Process the node based on our configuration
        if self._should_process_node(node, context):
            return self._process_string_node(node, line_gen, context)
        
        # Default: let Black handle it
        return line_gen(node)
    
    def _should_process_node(self, node, context):
        """Determine if we should process this string node."""
        # Check if it's an f-string and we're configured to normalize them
        is_f_string = any(child.type == "fstring_start" for child in node.children)
        if is_f_string and not self.normalize_f_strings:
            return False
            
        # If we're using Black's default quote style, don't process
        if self.quotes == "default":
            return False
            
        return True
    
    def _process_string_node(self, node, line_gen, context):
        """Process a string node according to our configuration."""
        # Get the original formatted lines
        original_lines = line_gen(node)
        if not original_lines:
            return original_lines
            
        # Apply our string normalization
        normalized_lines = self._normalize_string_lines(original_lines)
        
        return normalized_lines
    
    def _normalize_string_lines(self, lines):
        """Normalize string lines according to configuration."""
        # This is a simplified implementation for demonstration
        # A real implementation would parse and modify the strings more carefully
        
        if not lines:
            return lines
            
        # For single-line strings, apply quote normalization
        if len(lines) == 1 and self.quotes != "default":
            line = lines[0]
            # Very simple normalization for demonstration
            if self.quotes == "double" and "'" in line and '"' not in line:
                # Convert 'text' to "text"
                if line.startswith("'") and line.endswith("'"):
                    line = '"' + line[1:-1] + '"'
            elif self.quotes == "single" and '"' in line and "'" not in line:
                # Convert "text" to 'text'
                if line.startswith('"') and line.endswith('"'):
                    line = "'" + line[1:-1] + "'"
            return [line]
            
        # For multi-line strings (like docstrings), more complex processing would be needed
        # This is just a placeholder for demonstration
        return lines
