from app.services.chat_storage_service import ChatStorageService
from app.services.openai_service import OpenAIService
from app.services.settings_manager import SettingsManager
from app.models.chat import Role
from app.config.chat_config import CHAT_CONFIG

class AIAssistantService:
    """Service class for AI Assistant interactions."""

    def __init__(self, settings_manager: SettingsManager):
        """Initialize the AI Assistant service."""
        self.settings_manager = settings_manager
        self.chat_storage = ChatStorageService()
        self.openai_service = OpenAIService(settings_manager)
        self._initialize_openai()
        self._load_chat_settings()

    def _initialize_openai(self):
        """Initialize the OpenAI API with stored API key."""
        api_key = self.settings_manager.get("openai.api_key")
        if api_key:
            self.openai_service.initialize(api_key)

    def is_initialized(self) -> bool:
        """Check if the service is properly initialized with an API key."""
        return self.openai_service.is_initialized()

    def _load_chat_settings(self):
        """Load chat-related settings with defaults."""
        self.welcome_message = self.settings_manager.get(
            "chat.welcome_message",
            CHAT_CONFIG["default_settings"]["welcome_message"]
        )
        self.display_welcome = self.settings_manager.get(
            "chat.display_welcome",
            CHAT_CONFIG["default_settings"]["display_welcome"]
        )

    def initialize_chat(self) -> str:
        """Initialize or load existing chat session."""
        last_session = self.chat_storage.get_last_session()
        if last_session:
            return last_session.id
        
        session = self.chat_storage.create_session()
        session_id = session.id
        
        # Only add welcome message if enabled
        if self.display_welcome:
            message = {
                "role": Role.ASSISTANT,
                "content": self.welcome_message
            }
            
            self.chat_storage.add_message(
                session_id=session_id,
                role=message["role"],
                content=message["content"]
            )
        
        return session_id

    def get_chat_messages(self, session_id: str):
        """Get messages from a chat session."""
        return self.chat_storage.get_session_messages(session_id)

    def send_message(self, message: str, session_id: str) -> str:
        """Send a message and get AI response."""
        if not self.is_initialized():
            raise ValueError("OpenAI API key not set")

        # Save user message
        self.chat_storage.add_message(session_id, Role.USER, message)

        # Get chat history
        messages = self.chat_storage.get_session_messages(session_id)
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            role = msg.role.value
            # For unsupported models, convert system to assistant
            if role == "system":
                model = self.settings_manager.get("openai.model", "gpt-3.5-turbo")
                if model not in ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]:
                    role = "assistant"
            formatted_messages.append({"role": role, "content": msg.content})

        try:
            model = self.settings_manager.get("openai.model", "gpt-3.5-turbo")
            response = self.openai_service.get_chat_completion(
                messages=formatted_messages,
                model=model
            )
            
            if response:
                self.chat_storage.add_message(session_id, Role.ASSISTANT, response)
                return response
        except Exception as e:
            print(f"Error getting chat completion: {str(e)}")
            return "I'm sorry, I couldn't process your request."

        return "I'm sorry, I couldn't process your request."

    def remove_session(self, session_id: str) -> bool:
        """Remove a chat session."""
        try:
            return self.chat_storage.remove_session(session_id)
        except Exception as e:
            print(f"Error removing session: {str(e)}")
            return False

    def clear_all_sessions(self) -> bool:
        """Clear all chat sessions."""
        try:
            return self.chat_storage.clear_all_sessions()
        except Exception as e:
            print(f"Error clearing all sessions: {str(e)}")
            return False
