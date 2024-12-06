import keyring

class SecureStorageService:
    """Service for securely storing sensitive data like API keys."""

    SERVICE_NAME = "AIWritingAssistant"

    @classmethod
    def save_secret(cls, key: str, value: str) -> bool:
        try:
            keyring.set_password(cls.SERVICE_NAME, key, value)
            return True
        except Exception as e:
            print(f"Error saving secret: {str(e)}")
            return False

    @classmethod
    def get_secret(cls, key: str) -> str:
        try:
            return keyring.get_password(cls.SERVICE_NAME, key)
        except Exception as e:
            print(f"Error getting secret: {str(e)}")
            return ""
