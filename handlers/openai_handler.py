"""
OpenAI Handler
Manages NLP responses using OpenAI GPT models
"""

from openai import AsyncOpenAI
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class OpenAIHandler:
    def __init__(self, config: dict):
        self.config = config
        self.client = AsyncOpenAI(api_key=config["openai"]["api_key"])
        self.model = config["openai"]["model"]
        self.system_prompt = config["openai"]["system_prompt"]
        self.max_tokens = config["openai"]["max_tokens"]
        self.temperature = config["openai"]["temperature"]
    
    async def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate a natural language response using OpenAI
        
        Args:
            user_message: The user's message
            conversation_history: Recent conversation context
        
        Returns:
            AI-generated response text
        """
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history (last N messages for context)
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            # Extract response text
            ai_message = response.choices[0].message.content.strip()
            
            logger.info(f"Generated response: {ai_message[:50]}...")
            return ai_message
        
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            # Fallback response
            return "I'm sorry, I'm having trouble processing that right now. Could you try again?"
