CHAT_CONFIG = {
    "default_settings": {
        "welcome_message": "I am a helpful AI writing assistant. How can I help you today?",
        "system_role": "assistant",
        "display_welcome": True
    },
    "message_types": {
        "welcome": {
            "formal": "Welcome. I am your AI writing assistant. How may I assist you today?",
            "casual": "Hi! I'm here to help with your writing. What would you like to work on?",
            "minimal": "Ready to assist.",
            "custom": None  # Will be populated from user settings
        }
    }
}
