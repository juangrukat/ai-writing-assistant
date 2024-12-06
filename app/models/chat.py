from dataclasses import dataclass
from datetime import datetime
from typing import List
from enum import Enum

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ChatMessage:
    id: str
    role: Role
    content: str
    timestamp: datetime
    session_id: str

@dataclass
class ChatSession:
    id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
