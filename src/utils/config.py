"""
Configuration management for Endfield Market Tracker
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from appdirs import user_config_dir

@dataclass
class AppConfig:
    """Application configuration"""
    # Screen settings
    monitor_index: int = 0
    capture_fps: int = 10
    game_resolution: tuple = (1920, 1080)
    
    # OCR settings
    ocr_confidence_threshold: float = 0.8
    use_gpu: bool = True
    
    # UI settings
    theme: str = "dark"
    window_width: int = 1400
    window_height: int = 900
    
    # ROI settings (calibrated regions for OCR)
    rois: Dict = None
    
    def __post_init__(self):
        if self.rois is None:
            from src.utils.constants import DEFAULT_ROIS
            self.rois = DEFAULT_ROIS.copy()

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_dir = user_config_dir("EndfieldMarketTracker", "EndfieldMarketTracker")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self.load_config()
    
    def load_config(self) -> AppConfig:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Convert tuple back from list
                if 'game_resolution' in data and isinstance(data['game_resolution'], list):
                    data['game_resolution'] = tuple(data['game_resolution'])
                
                return AppConfig(**data)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return AppConfig()
        
        return AppConfig()
    
    def save_config(self):
        """Save configuration to file"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        try:
            data = asdict(self.config)
            
            # Convert tuple to list for JSON serialization
            if isinstance(data.get('game_resolution'), tuple):
                data['game_resolution'] = list(data['game_resolution'])
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_roi(self, key: str, x: int, y: int, width: int, height: int):
        """Update a region of interest"""
        self.config.rois[key] = {
            'x': x, 'y': y, 'w': width, 'h': height
        }
        self.save_config()
    
    def get_roi(self, key: str) -> Optional[Dict]:
        """Get a region of interest"""
        return self.config.rois.get(key)

# Global config instance
_config_manager = None

def get_config() -> AppConfig:
    """Get the global configuration"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.config

def save_config():
    """Save the global configuration"""
    global _config_manager
    if _config_manager:
        _config_manager.save_config()