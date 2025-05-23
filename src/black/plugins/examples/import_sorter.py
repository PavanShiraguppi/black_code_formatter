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

    def _process_module_imports(self, node, line_gen, context):
        """Process all imports in a module."""
        # Extract all imports from the module
        imports = self._extract_imports(node)
        if not imports:
            return None

        # Mark that we're sorting imports to prevent double-processing
        context["import_sorting_in_progress"] = True

        # Sort imports according to our rules
        sorted_imports = self._sort_imports(imports)

        # Generate the formatted lines for the sorted imports
        import_lines = []
        current_group = None

        for import_node, group in sorted_imports:
            # Add blank line between groups if configured
            if self.separate_groups_with_blank_line and current_group is not None and current_group != group:
                import_lines.append("")

            # Generate formatted lines for this import
            import_formatted = line_gen(import_node)
            if import_formatted:
                import_lines.extend(import_formatted)

            current_group = group

        # Generate lines for everything else in the module
        non_import_nodes = [child for child in node.children
                           if child.type not in ("import_stmt", "import_from_stmt")]

        other_lines = []
        for child_node in non_import_nodes:
            child_lines = line_gen(child_node)
            if child_lines:
                other_lines.extend(child_lines)

        # Combine with a blank line between imports and code if there are both
        if import_lines and other_lines and other_lines[0].strip():
            result_lines = import_lines + [""] + other_lines
        else:
            result_lines = import_lines + other_lines

        # Clean up context
        context.pop("import_sorting_in_progress", None)

        return result_lines

    def _extract_imports(self, node):
        """Extract all import statements from a module node."""
        imports = []
        for child in node.children:
            if child.type in ("import_stmt", "import_from_stmt"):
                imports.append(child)
        return imports

    def _determine_import_group(self, import_node):
        """Determine which group an import belongs to."""
        # Extract the module name from the import
        module_name = self._get_module_name(import_node)

        # Check each group in order
        if any(module_name.startswith(prefix) for prefix in self.local_prefixes):
            return "local"

        if self.first_party_prefixes:
            if any(module_name.startswith(prefix) for prefix in self.first_party_prefixes):
                return "first_party"

        if self.third_party_prefixes:
            if any(module_name.startswith(prefix) for prefix in self.third_party_prefixes):
                return "third_party"

        if self.stdlib_prefixes:
            if any(module_name.startswith(prefix) for prefix in self.stdlib_prefixes):
                return "stdlib"
        else:
            # Use a simple heuristic for standard library modules if no custom prefixes
            if self._is_stdlib_module(module_name):
                return "stdlib"

        # Default to third-party if we can't determine
        return "third_party"

    def _get_module_name(self, import_node):
        """Extract the module name from an import node."""
        if import_node.type == "import_stmt":
            # Regular import statement: import module.name
            for child in import_node.children:
                if child.type == "dotted_name":
                    return child.get_code()
        elif import_node.type == "import_from_stmt":
            # From import: from module.name import ...
            for child in import_node.children:
                if child.type == "dotted_name":
                    return child.get_code()
                elif child.type == "dot" and child.value == ".":
                    return "."  # Relative import
        return ""

    def _is_stdlib_module(self, module_name):
        """Determine if a module is part of the Python standard library."""
        # Simple heuristic: standard library modules don't have dots
        # (except a few, but this is good enough for a demo)
        if "." in module_name and not any(module_name.startswith(p) for p in ("xml.", "http.", "html.", "email.")):
            return False

        # List of common standard library modules (not comprehensive)
        stdlib_modules = {
            "sys", "os", "re", "math", "time", "datetime", "collections", "itertools",
            "functools", "random", "socket", "json", "csv", "argparse", "logging",
            "pathlib", "typing", "abc", "io", "tempfile", "shutil", "unittest"
        }

        # Check if the top-level module is in our known stdlib list
        top_module = module_name.split(".")[0]
        return top_module in stdlib_modules

    def _sort_imports(self, imports):
        """Sort imports according to the configured rules."""
        # Group imports
        grouped_imports = {}
        for imp in imports:
            group = self._determine_import_group(imp)
            if group not in grouped_imports:
                grouped_imports[group] = []
            grouped_imports[group].append((imp, group))

        # Sort within each group
        for group, imports_in_group in grouped_imports.items():
            imports_in_group.sort(
                key=lambda x: self._get_sort_key(x[0], self.sort_case_insensitive,
                                                self.sort_by_package_then_name)
            )

        # Combine according to group order
        result = []
        for group in self.group_order:
            if group in grouped_imports:
                result.extend(grouped_imports[group])

        # Add any groups that weren't explicitly ordered
        for group, imports_in_group in grouped_imports.items():
            if group not in self.group_order:
                result.extend(imports_in_group)

        return result

    def _get_sort_key(self, import_node, case_insensitive=True, by_package_first=True):
        """Get a sort key for an import node."""
        module_name = self._get_module_name(import_node)

        if case_insensitive:
            module_name = module_name.lower()

        if by_package_first and "." in module_name:
            # Sort by package, then by full module name for ties
            parts = module_name.split(".")
            return (parts[0], module_name)

        return module_name
