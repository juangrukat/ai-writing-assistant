import os
import json
from datetime import datetime
from typing import List, Optional
from app.models.chat import ChatMessage, ChatSession, Role
import uuid

class ChatStorageService:
    """Service for storing and retrieving chat messages."""

    def __init__(self):
        self.base_dir = os.path.expanduser('~/.aiwritingassistant/chats')
        os.makedirs(self.base_dir, exist_ok=True)

    def create_session(self) -> ChatSession:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            id=session_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._save_session(session)
        return session

    def add_message(self, session_id: str, role: Role, content: str):
        session = self._load_session(session_id)
        if session:
            message = ChatMessage(
                id=str(uuid.uuid4()),
                role=role,
                content=content,
                timestamp=datetime.now(),
                session_id=session_id
            )
            session.messages.append(message)
            session.updated_at = datetime.now()
            self._save_session(session)
        else:
            raise ValueError(f"Session not found: {session_id}")

    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        session = self._load_session(session_id)
        return session.messages if session else []

    def get_last_session(self) -> Optional[ChatSession]:
        sessions = [f for f in os.listdir(self.base_dir) if f.endswith('.json')]
        if not sessions:
            return None
        latest_session = max(
            sessions,
            key=lambda x: os.path.getmtime(os.path.join(self.base_dir, x))
        )
        return self._load_session(latest_session.replace('.json', ''))

    def _save_session(self, session: ChatSession):
        file_path = os.path.join(self.base_dir, f"{session.id}.json")
        with open(file_path, 'w') as f:
            json.dump({
                'id': session.id,
                'messages': [
                    {
                        'id': msg.id,
                        'role': msg.role.value,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat(),
                        'session_id': msg.session_id
                    }
                    for msg in session.messages
                ],
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            }, f, indent=2)

    def _load_session(self, session_id: str) -> Optional[ChatSession]:
        file_path = os.path.join(self.base_dir, f"{session_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return ChatSession(
                    id=data['id'],
                    messages=[
                        ChatMessage(
                            id=msg['id'],
                            role=Role(msg['role']),
                            content=msg['content'],
                            timestamp=datetime.fromisoformat(msg['timestamp']),
                            session_id=msg['session_id']
                        )
                        for msg in data['messages']
                    ],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at'])
                )
        return None

    def remove_session(self, session_id: str) -> bool:
        try:
            file_path = os.path.join(self.base_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                for file in os.listdir(self.base_dir):
                    if file.startswith(session_id):
                        try:
                            os.remove(os.path.join(self.base_dir, file))
                        except Exception as e:
                            print(f"Error removing associated file {file}: {str(e)}")
                return True
            return False
        except Exception as e:
            print(f"Error removing session: {str(e)}")
            return False

    def clear_all_sessions(self) -> bool:
        try:
            for file in os.listdir(self.base_dir):
                if file.endswith('.json'):
                    try:
                        os.remove(os.path.join(self.base_dir, file))
                    except Exception as e:
                        print(f"Error removing file {file}: {str(e)}")
            return True
        except Exception as e:
            print(f"Error clearing all sessions: {str(e)}")
            return False
