"""Configuration for the Criteria Selection functionality."""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class CriteriaConfig:
    SUPPORTED_EXTENSIONS: List[str] = field(default_factory=lambda: ['.txt', '.md', '.json'])
    DEFAULT_DESCRIPTION: str = "No description available"
    PLACEHOLDER_TEXT: str = "Select a criteria set to view details..."
    NO_FOLDER_TEXT: str = "No folder selected"
    
    # Default settings structure
    DEFAULT_SETTINGS: Dict = field(default_factory=lambda: {
        "last_type": "",
        "last_set": {
            "name": "",
            "description": "",
            "category": "",
            "file_path": "",
            "file_type": ""
        }
    }) 