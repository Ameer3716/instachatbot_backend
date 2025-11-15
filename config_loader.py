"""
Environment-based configuration loader
Use this if you want to load from environment variables instead of config.json
"""

import os
from typing import Dict

def load_config() -> Dict:
    """
    Load configuration from environment variables
    Fallback to config.json if env vars not set
    """
    
    config = {
        "instagram": {
            "access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
            "api_version": os.getenv("INSTAGRAM_API_VERSION", "v21.0"),
            "page_id": os.getenv("INSTAGRAM_PAGE_ID", "")
        },
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "system_prompt": os.getenv(
                "OPENAI_SYSTEM_PROMPT",
                "You are a friendly and helpful assistant for an Instagram account."
            ),
            "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "150")),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.8"))
        },
        "webhook": {
            "verify_token": os.getenv("WEBHOOK_VERIFY_TOKEN", "")
        },
        "typing_delay": {
            "base_seconds": float(os.getenv("TYPING_BASE_SECONDS", "1.0")),
            "per_word_seconds": float(os.getenv("TYPING_PER_WORD_SECONDS", "0.15")),
            "max_seconds": float(os.getenv("TYPING_MAX_SECONDS", "5.0")),
            "randomness_factor": float(os.getenv("TYPING_RANDOMNESS", "0.3"))
        },
        "session": {
            "timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "30")),
            "max_messages_per_session": int(os.getenv("SESSION_MAX_MESSAGES", "20"))
        }
    }
    
    # Load media triggers from JSON file or environment
    # For simplicity, media triggers should be in config.json
    
    return config


def validate_config(config: Dict) -> bool:
    """
    Validate that required configuration values are present
    """
    required_fields = [
        ("instagram", "access_token"),
        ("openai", "api_key"),
        ("webhook", "verify_token")
    ]
    
    for section, field in required_fields:
        if not config.get(section, {}).get(field):
            print(f"ERROR: Missing required config: {section}.{field}")
            return False
    
    return True
