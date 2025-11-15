"""
Delay Handler
Simulates human-like typing delays
"""

import logging
import random

logger = logging.getLogger(__name__)


class DelayHandler:
    def __init__(self, config: dict):
        self.config = config
        self.delay_config = config["typing_delay"]
    
    def calculate_delay(self, text: str) -> float:
        """
        Calculate typing delay based on text length and configuration
        
        Args:
            text: The message text
        
        Returns:
            Delay in seconds
        """
        # Get configuration
        base_delay = self.delay_config["base_seconds"]
        per_word = self.delay_config["per_word_seconds"]
        max_delay = self.delay_config["max_seconds"]
        randomness = self.delay_config["randomness_factor"]
        
        # Count words
        word_count = len(text.split())
        
        # Calculate base delay
        calculated_delay = base_delay + (word_count * per_word)
        
        # Cap at max delay
        calculated_delay = min(calculated_delay, max_delay)
        
        # Add randomness (±randomness_factor%)
        random_factor = 1 + random.uniform(-randomness, randomness)
        final_delay = calculated_delay * random_factor
        
        logger.debug(f"Calculated delay: {final_delay:.2f}s for {word_count} words")
        
        return max(0.5, final_delay)  # Minimum 0.5 seconds
    
    def get_pause_delay(self) -> float:
        """
        Get a short pause delay (for simulating thinking)
        
        Returns:
            Short delay in seconds
        """
        return random.uniform(0.5, 1.5)
