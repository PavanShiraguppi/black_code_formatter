# Configuration Profiles

Black now supports configuration profiles, which allow you to save and reuse formatting configurations across different projects or environments.

## Using Profiles

Profiles can be used in several ways:

### Command Line

```bash
# Use a predefined profile
black --profile=pycharm

# List available profiles
black --list-profiles

# Save current configuration as a profile
black --save-profile=my_custom_profile

# Export a profile to a file
black --export-profile=google profile.toml
```

### Built-in Profiles

Black comes with several built-in profiles:

- **default**: Black's default settings (line length 88, double quotes, etc.)
- **pycharm**: Compatible with PyCharm defaults (line length 120, single quotes)
- **vscode**: Compatible with VS Code defaults (line length 100)
- **google**: Following Google Python Style Guide (line length 80, single quotes)
- **compact**: Compact formatting with shorter line length (line length 79)

## Creating Custom Profiles

You can create custom profiles in two ways:

### Using the Command Line

```bash
# Set your formatting options
black --line-length=100 --skip-string-normalization --save-profile=my_profile
```

This will prompt you for a description and save the profile.

### Creating Profile Files Manually

You can create profile files manually in TOML format:

```toml
[profile]
name = "my_profile"
description = "My custom formatting profile"
version = "1.0"
parent = "default"  # Optional parent profile

[profile.settings]
line_length = 100
skip_string_normalization = true
```

Save this file in one of the following locations:

- `~/.black/profiles/my_profile.toml` (user-specific)
- `<black-installation-dir>/profiles/my_profile.toml` (system-wide)
- `<project-dir>/.black/profiles/my_profile.toml` (project-specific)

## Profile Inheritance

Profiles can inherit settings from other profiles using the `parent` field. This allows you to create profiles that are variations of existing ones.

For example, the `pycharm` profile inherits from the `default` profile and only overrides specific settings:

```toml
[profile]
name = "pycharm"
description = "Profile compatible with PyCharm defaults"
parent = "default"

[profile.settings]
line_length = 120
skip_string_normalization = true
```

## Profile Settings

Profiles can include any of Black's formatting options:

- `line_length`: Maximum line length
- `target_version`: Python versions to target (list of strings like "py38")
- `skip_string_normalization`: Whether to skip string normalization
- `skip_magic_trailing_comma`: Whether to skip magic trailing commas
- `preview`: Whether to enable preview features
- `unstable`: Whether to enable unstable features

## Technical Details

### Profile Resolution

When you specify a profile, Black looks for it in the following locations:

1. Built-in profiles
2. System-wide profiles (`<black-installation-dir>/profiles/`)
3. User profiles (`~/.black/profiles/`)
4. Project profiles (`./.black/profiles/`)

Later locations override earlier ones, so you can override built-in profiles with your own versions.

### Profile Format

Profiles are stored in TOML format with the following structure:

```toml
[profile]
name = "profile_name"
description = "Profile description"
version = "1.0"
parent = "optional_parent_profile"

[profile.settings]
# Black formatting options
line_length = 88
skip_string_normalization = false
```

### Command Line Precedence

Command line options always take precedence over profile settings. This allows you to use a profile as a base configuration and override specific options as needed.
