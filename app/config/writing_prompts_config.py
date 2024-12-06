from dataclasses import dataclass, field
from typing import List

@dataclass
class WritingPromptsConfig:
    DEFAULT_FOLDERS: List[str] = field(default_factory=list)
    SUPPORTED_FILE_EXTENSIONS: List[str] = field(default_factory=lambda: ['.txt', '.md'])
    MAX_PROMPT_LENGTH: int = 5000
    PROMPT_DISPLAY_PLACEHOLDER: str = "Click on 'Get New Prompt' to start..."
    NO_FOLDER_TEXT: str = "No folder selected"
    MARKDOWN_EXTRAS: List[str] = field(default_factory=lambda: [
        'fenced-code-blocks',
        'tables',
        'break-on-newline',
        'header-ids'
    ])
