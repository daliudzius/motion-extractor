"""
Configuration management for motion extraction.
"""

import json
from pathlib import Path
from typing import Any, Dict


class Config:
    """
    Manages application configuration settings.
    
    Loads settings from JSON files and provides type-safe access
    to configuration parameters.
    """
    
    # Default configuration values
    DEFAULTS = {
        "motion": {
            "delay_frames": 5,
            "delay_seconds": None,
            "blend_alpha": 0.5,
            "fps": 30
        },
        "camera": {
            "source": 0,
            "width": 640,
            "height": 480
        },
        "display": {
            "show_preview": True,
            "window_name": "Motion Extraction"
        }
    }
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        Initialize configuration.
        
        Args:
            config_path (str): Path to configuration JSON file
        """
        self.config_path = Path(config_path)
        self.settings = self.DEFAULTS.copy()
        self.load()
    
    def load(self) -> None:
        """
        Load configuration from file.
        
        If file doesn't exist, uses defaults and creates the file.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_settings = json.load(f)
                    # Deep merge user settings with defaults
                    self._merge_settings(user_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default settings")
        else:
            # Create default config file
            self.save()
    
    def _merge_settings(self, user_settings: Dict[str, Any]) -> None:
        """
        Merge user settings with defaults.
        
        Args:
            user_settings (dict): User-provided configuration values
        """
        for section, values in user_settings.items():
            if section in self.settings:
                self.settings[section].update(values)
    
    def save(self) -> None:
        """Save current settings to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section (str): Configuration section (e.g., 'motion', 'camera')
            key (str): Setting key within the section
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self.settings.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Setting key
            value (Any): Value to set
        """
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
