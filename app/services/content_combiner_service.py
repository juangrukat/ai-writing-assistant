from typing import Optional
from app.config.content_combiner_config import CONTENT_COMBINER_CONFIG

class ContentCombinerService:
    """Service for combining and validating content sections."""
    
    def __init__(self):
        self._writing_prompt: Optional[str] = None
        self.config = CONTENT_COMBINER_CONFIG

    def set_writing_prompt(self, prompt: Optional[str]) -> None:
        self._writing_prompt = prompt

    def get_writing_prompt(self) -> Optional[str]:
        return self._writing_prompt
    
    def combine_content(self, submission: str, criteria: str) -> str:
        combined = ""
        
        # Add prompt if available
        if self._writing_prompt:
            prompt_section = (
                f"{self.config['sections']['prompt']['prefix']}"
                f"{self._writing_prompt}"
                f"{self.config['sections']['prompt']['suffix']}"
            )
            combined += prompt_section
        
        submission_section = (
            f"{self.config['sections']['submission']['prefix']}"
            f"{submission}"
            f"{self.config['sections']['submission']['suffix']}"
        )
        combined += submission_section
        
        criteria_section = (
            f"{self.config['sections']['criteria']['prefix']}"
            f"{criteria}"
            f"{self.config['sections']['criteria']['suffix']}"
        )
        combined += criteria_section
        
        return combined
