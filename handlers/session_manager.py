"""
Session Manager
Handles user conversation sessions and context
"""

import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize session manager
        
        Args:
            session_timeout_minutes: Time before session expires
        """
        self.sessions: Dict[str, List[Dict]] = defaultdict(list)
        self.last_activity: Dict[str, datetime] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def add_message(self, user_id: str, role: str, content: str):
        """
        Add a message to user's session
        
        Args:
            user_id: Instagram user ID
            role: 'user' or 'assistant'
            content: Message content
        """
        # Clean old sessions
        self._cleanup_old_sessions()
        
        # Add message
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sessions[user_id].append(message)
        self.last_activity[user_id] = datetime.now()
        
        # Keep only last 20 messages per user to save memory
        if len(self.sessions[user_id]) > 20:
            self.sessions[user_id] = self.sessions[user_id][-20:]
        
        logger.debug(f"Added message for user {user_id}: {role}")
    
    def get_context(self, user_id: str, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation context for a user
        
        Args:
            user_id: Instagram user ID
            max_messages: Maximum number of messages to return
        
        Returns:
            List of recent messages (for OpenAI context)
        """
        messages = self.sessions.get(user_id, [])
        
        # Return only role and content (remove timestamp)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages[-max_messages:]
        ]
    
    def clear_session(self, user_id: str):
        """Clear a user's session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
        if user_id in self.last_activity:
            del self.last_activity[user_id]
        
        logger.info(f"Cleared session for user {user_id}")
    
    def _cleanup_old_sessions(self):
        """Remove expired sessions to free memory"""
        now = datetime.now()
        expired_users = [
            user_id for user_id, last_time in self.last_activity.items()
            if now - last_time > self.session_timeout
        ]
        
        for user_id in expired_users:
            self.clear_session(user_id)
            logger.info(f"Expired session for user {user_id}")
    
    def get_active_count(self) -> int:
        """Get number of active sessions"""
        self._cleanup_old_sessions()
        return len(self.sessions)
    
    def get_total_count(self) -> int:
        """Get total number of conversations ever handled"""
        return len(self.sessions) + len(self.last_activity)
