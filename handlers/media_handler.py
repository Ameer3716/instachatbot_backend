"""
Media Handler
Handles keyword-based media triggers (images and audio)
"""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class MediaHandler:
    def __init__(self, config: dict):
        self.config = config
        self.keyword_triggers = config["media_triggers"]
    
    def check_triggers(self, message_text: str) -> Optional[Dict]:
        """
        Check if message contains any keyword triggers
        
        Args:
            message_text: User's message text
        
        Returns:
            Dict with media type and path if triggered, None otherwise
        """
        message_lower = message_text.lower()
        
        # Check each trigger
        for trigger in self.keyword_triggers:
            keywords = trigger["keywords"]
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    logger.info(f"Keyword '{keyword}' triggered: {trigger['type']}")
                    return {
                        "type": trigger["type"],
                        "path": trigger["path"],
                        "name": trigger["name"]
                    }
        
        return None
    
    def add_trigger(self, keywords: list, media_type: str, path: str, name: str):
        """
        Add a new media trigger
        
        Args:
            keywords: List of trigger keywords
            media_type: 'image' or 'audio'
            path: Path/URL to media file
            name: Descriptive name
        """
        new_trigger = {
            "keywords": keywords,
            "type": media_type,
            "path": path,
            "name": name
        }
        
        self.keyword_triggers.append(new_trigger)
        logger.info(f"Added new trigger: {name}")
    
    def remove_trigger(self, name: str) -> bool:
        """
        Remove a trigger by name
        
        Args:
            name: Name of the trigger to remove
        
        Returns:
            True if removed, False if not found
        """
        original_length = len(self.keyword_triggers)
        self.keyword_triggers = [
            t for t in self.keyword_triggers if t["name"] != name
        ]
        
        removed = len(self.keyword_triggers) < original_length
        if removed:
            logger.info(f"Removed trigger: {name}")
        
        return removed
