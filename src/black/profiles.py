"""Configuration profiles for Black.

This module provides functionality for managing and switching between different
formatting profiles in Black.
"""

import os
import json
import tomli
import tomli_w
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Union
from dataclasses import dataclass, field, asdict


@dataclass
class ConfigurationProfile:
    """Base profile interface for Black configurations."""
    
    name: str
    description: str
    version: str = "1.0"
    settings: Dict[str, Any] = field(default_factory=dict)
    parent: Optional[str] = None
    
    def get_effective_configuration(self, profiles_registry=None) -> Dict[str, Any]:
        """Return effective configuration including inherited settings."""
        if self.parent and profiles_registry:
            parent_profile = profiles_registry.get_profile(self.parent)
            if parent_profile:
                config = parent_profile.get_effective_configuration(profiles_registry)
                config.update(self.settings)
                return config
        return self.settings.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "settings": self.settings,
            "parent": self.parent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigurationProfile':
        """Create profile from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            settings=data.get("settings", {}),
            parent=data.get("parent")
        )


class ProfileRegistry:
    """Registry for managing configuration profiles."""
    
    def __init__(self):
        self.profiles: Dict[str, ConfigurationProfile] = {}
        self.system_profiles_dir = Path(os.path.dirname(__file__)) / "profiles"
        self.user_profiles_dir = Path.home() / ".black" / "profiles"
        self.project_profiles_dir = None
        
        # Ensure user profiles directory exists
        self.user_profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Load built-in profiles
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load profiles from all locations."""
        # Load system profiles
        if self.system_profiles_dir.exists():
            self._load_profiles_from_dir(self.system_profiles_dir)
        
        # Load user profiles
        if self.user_profiles_dir.exists():
            self._load_profiles_from_dir(self.user_profiles_dir)
        
        # Load project profiles if set
        if self.project_profiles_dir and self.project_profiles_dir.exists():
            self._load_profiles_from_dir(self.project_profiles_dir)
    
    def _load_profiles_from_dir(self, directory: Path) -> None:
        """Load profiles from a directory."""
        for file_path in directory.glob("*.toml"):
            try:
                with open(file_path, "rb") as f:
                    data = tomli.load(f)
                
                if "profile" in data:
                    profile_data = data["profile"]
                    profile = ConfigurationProfile.from_dict(profile_data)
                    self.profiles[profile.name] = profile
            except Exception as e:
                print(f"Error loading profile from {file_path}: {e}")
    
    def set_project_profiles_dir(self, directory: Union[str, Path]) -> None:
        """Set and load profiles from a project-specific directory."""
        self.project_profiles_dir = Path(directory)
        if self.project_profiles_dir.exists():
            self._load_profiles_from_dir(self.project_profiles_dir)
    
    def get_profile(self, name: str) -> Optional[ConfigurationProfile]:
        """Get a profile by name."""
        return self.profiles.get(name)
    
    def add_profile(self, profile: ConfigurationProfile) -> None:
        """Add a profile to the registry."""
        self.profiles[profile.name] = profile
    
    def save_profile(self, profile: ConfigurationProfile, location: str = "user") -> Path:
        """Save a profile to the specified location."""
        if location == "system":
            target_dir = self.system_profiles_dir
        elif location == "project" and self.project_profiles_dir:
            target_dir = self.project_profiles_dir
        else:
            target_dir = self.user_profiles_dir
        
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"{profile.name}.toml"
        
        with open(file_path, "wb") as f:
            tomli_w.dump({"profile": profile.to_dict()}, f)
        
        return file_path
    
    def list_profiles(self) -> List[ConfigurationProfile]:
        """List all available profiles."""
        return list(self.profiles.values())
    
    def export_profile(self, name: str, file_path: Union[str, Path]) -> bool:
        """Export a profile to a file."""
        profile = self.get_profile(name)
        if not profile:
            return False
        
        file_path = Path(file_path)
        with open(file_path, "wb") as f:
            tomli_w.dump({"profile": profile.to_dict()}, f)
        
        return True


# Built-in profiles
BUILTIN_PROFILES = {
    "default": ConfigurationProfile(
        name="default",
        description="Black's default settings",
        settings={
            "line_length": 88,
            "target_version": ["py38"],
            "skip_string_normalization": False,
            "skip_magic_trailing_comma": False,
        }
    ),
    "pycharm": ConfigurationProfile(
        name="pycharm",
        description="Profile compatible with PyCharm defaults",
        settings={
            "line_length": 120,
            "skip_string_normalization": True,
        },
        parent="default"
    ),
    "vscode": ConfigurationProfile(
        name="vscode",
        description="Profile compatible with VS Code defaults",
        settings={
            "line_length": 100,
        },
        parent="default"
    ),
    "google": ConfigurationProfile(
        name="google",
        description="Profile following Google Python Style Guide",
        settings={
            "line_length": 80,
            "target_version": ["py38"],
            "skip_string_normalization": True,
        }
    ),
    "compact": ConfigurationProfile(
        name="compact",
        description="Compact formatting with shorter line length",
        settings={
            "line_length": 79,
            "skip_magic_trailing_comma": True,
        },
        parent="default"
    ),
}


# Global registry instance
_registry = None


def get_registry() -> ProfileRegistry:
    """Get the global profile registry instance."""
    global _registry
    if _registry is None:
        _registry = ProfileRegistry()
        # Add built-in profiles
        for profile in BUILTIN_PROFILES.values():
            _registry.add_profile(profile)
    return _registry


def available_profiles() -> List[str]:
    """Get list of available profile names."""
    return [profile.name for profile in get_registry().list_profiles()]


def load_profile(name: str) -> Optional[Dict[str, Any]]:
    """Load a profile by name and return its effective configuration."""
    registry = get_registry()
    profile = registry.get_profile(name)
    if profile:
        return profile.get_effective_configuration(registry)
    return None


def save_profile(name: str, description: str, settings: Dict[str, Any], 
                parent: Optional[str] = None, location: str = "user") -> bool:
    """Save a new profile with the given settings."""
    registry = get_registry()
    profile = ConfigurationProfile(
        name=name,
        description=description,
        settings=settings,
        parent=parent
    )
    registry.add_profile(profile)
    registry.save_profile(profile, location)
    return True


def list_profiles() -> List[Dict[str, Any]]:
    """List all available profiles with their details."""
    registry = get_registry()
    return [
        {
            "name": p.name,
            "description": p.description,
            "parent": p.parent,
            "settings_count": len(p.settings)
        }
        for p in registry.list_profiles()
    ]


def export_profile(name: str, file_path: str) -> bool:
    """Export a profile to a file."""
    registry = get_registry()
    return registry.export_profile(name, file_path)
