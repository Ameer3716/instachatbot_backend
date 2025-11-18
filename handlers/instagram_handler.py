"""
Instagram API Handler
Manages communication with Instagram Graph API
"""

import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InstagramHandler:
    def __init__(self, config: dict):
        self.config = config
        self.access_token = config["instagram"]["access_token"]
        self.api_version = config["instagram"]["api_version"]
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.page_id = config["instagram"].get("page_id", "")
    
    async def get_user_info(self, user_id: str) -> dict:
        """
        Fetch Instagram user information
        Returns: {name, username, profile_pic, follower_count}
        """
        url = f"{self.base_url}/{user_id}"
        params = {
            "fields": "name,username,profile_pic,follower_count",
            "access_token": self.access_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Retrieved user info for {user_id}")
                        return data
                    else:
                        logger.error(f"Failed to get user info: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error fetching user info: {str(e)}")
            return {}
    
    async def send_text_message(self, recipient_id: str, text: str) -> bool:
        """
        Send a text message to a user
        """
        url = f"{self.base_url}/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        logger.info(f"Message sent successfully to {recipient_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send message: {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def send_image(self, recipient_id: str, image_url: str) -> bool:
        """
        Send an image to a user
        """
        url = f"{self.base_url}/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {"url": image_url}
                }
            }
        }
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        logger.info(f"Image sent successfully to {recipient_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send image: {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"Error sending image: {str(e)}")
            return False
    
    async def send_audio(self, recipient_id: str, audio_url: str) -> bool:
        """
        Send an audio file to a user
        """
        url = f"{self.base_url}/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "audio",
                    "payload": {"url": audio_url}
                }
            }
        }
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        logger.info(f"Audio sent successfully to {recipient_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send audio: {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"Error sending audio: {str(e)}")
            return False
    
    async def send_typing_indicator(self, recipient_id: str, action: str) -> bool:
        """
        Send typing indicator (on/off)
        """
        url = f"{self.base_url}/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": f"typing_{action}"
        }
        
        params = {"access_token": self.access_token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.error(f"Error sending typing indicator: {str(e)}")
            return False
