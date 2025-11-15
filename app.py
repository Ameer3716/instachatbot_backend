"""
Instagram Chatbot Backend
FastAPI application for handling Instagram messages with NLP
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import asyncio
from typing import Dict, List
import logging
from datetime import datetime
import os

from handlers.instagram_handler import InstagramHandler
from handlers.openai_handler import OpenAIHandler
from handlers.session_manager import SessionManager
from handlers.media_handler import MediaHandler
from handlers.delay_handler import DelayHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Instagram Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
# Try to load config.json, fallback to environment variables
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    # Production: use environment variables only
    config = {
        "instagram": {
            "access_token": os.getenv('INSTAGRAM_ACCESS_TOKEN', 'dummy'),
            "api_version": "v21.0",
            "page_id": os.getenv('INSTAGRAM_PAGE_ID', 'dummy')
        },
        "openai": {
            "api_key": os.getenv('OPENAI_API_KEY', ''),
            "model": "gpt-4o-mini",
            "system_prompt": "You are a friendly and helpful assistant for an Instagram account. You communicate naturally like a real human being. Be conversational, warm, and engaging. Keep responses concise but meaningful. Use casual language and emojis when appropriate. Always maintain a helpful and positive tone.",
            "max_tokens": 150,
            "temperature": 0.8
        },
        "webhook": {
            "verify_token": os.getenv('WEBHOOK_VERIFY_TOKEN', 'dummy')
        },
        "typing_delay": {
            "base_seconds": 1.0,
            "per_word_seconds": 0.15,
            "max_seconds": 5.0,
            "randomness_factor": 0.3
        },
        "media_triggers": [],
        "session": {
            "timeout_minutes": 30,
            "max_messages_per_session": 20
        }
    }

# Override with environment variables if present (for config.json fallback)
if os.getenv('OPENAI_API_KEY'):
    config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
if os.getenv('INSTAGRAM_ACCESS_TOKEN'):
    config['instagram']['access_token'] = os.getenv('INSTAGRAM_ACCESS_TOKEN')
if os.getenv('INSTAGRAM_PAGE_ID'):
    config['instagram']['page_id'] = os.getenv('INSTAGRAM_PAGE_ID')
if os.getenv('WEBHOOK_VERIFY_TOKEN'):
    config['webhook']['verify_token'] = os.getenv('WEBHOOK_VERIFY_TOKEN')

# Initialize handlers
instagram_handler = InstagramHandler(config)
openai_handler = OpenAIHandler(config)
session_manager = SessionManager()
media_handler = MediaHandler(config)
delay_handler = DelayHandler(config)

# Task queue for handling concurrent messages
message_tasks: Dict[str, asyncio.Task] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Instagram Chatbot",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint for Instagram
    Instagram sends a GET request with hub.mode, hub.verify_token, and hub.challenge
    """
    params = request.query_params
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    if mode == "subscribe" and token == config["webhook"]["verify_token"]:
        logger.info("Webhook verified successfully")
        return int(challenge)
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Main webhook endpoint to receive Instagram messages
    Processes incoming messages asynchronously
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook: {json.dumps(body, indent=2)}")
        
        # Process webhook in background to respond quickly
        asyncio.create_task(process_webhook(body))
        
        return JSONResponse({"status": "received"}, status_code=200)
    
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return JSONResponse({"status": "error"}, status_code=200)


async def process_webhook(data: dict):
    """
    Process Instagram webhook data
    Handles multiple concurrent messages efficiently
    """
    try:
        if data.get("object") != "instagram":
            return
        
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                # Extract message details
                sender_id = messaging_event.get("sender", {}).get("id")
                recipient_id = messaging_event.get("recipient", {}).get("id")
                
                if "message" in messaging_event:
                    message_data = messaging_event["message"]
                    message_text = message_data.get("text", "")
                    
                    # Create task for this user if not already processing
                    task_key = f"{sender_id}_{datetime.now().timestamp()}"
                    
                    # Handle message asynchronously
                    task = asyncio.create_task(
                        handle_user_message(sender_id, recipient_id, message_text)
                    )
                    message_tasks[task_key] = task
                    
                    # Clean up completed tasks
                    cleanup_tasks()
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")


async def handle_user_message(sender_id: str, recipient_id: str, message_text: str):
    """
    Handle individual user message with NLP and media triggers
    """
    try:
        logger.info(f"Processing message from {sender_id}: {message_text}")
        
        # Update user session
        session_manager.add_message(sender_id, "user", message_text)
        
        # Check for keyword triggers (media responses)
        media_response = media_handler.check_triggers(message_text)
        
        if media_response:
            # Send media (image or audio)
            await send_media_response(sender_id, media_response)
        
        # Generate NLP response
        conversation_history = session_manager.get_context(sender_id)
        ai_response = await openai_handler.generate_response(
            message_text, 
            conversation_history
        )
        
        # Send response with human-like delay
        await send_text_with_delay(sender_id, ai_response)
        
        # Update session with bot response
        session_manager.add_message(sender_id, "assistant", ai_response)
    
    except Exception as e:
        logger.error(f"Error handling message from {sender_id}: {str(e)}")


async def send_text_with_delay(recipient_id: str, text: str):
    """
    Send text message with human-like typing delay
    Simulates realistic typing behavior
    """
    try:
        # Calculate typing delay based on message length
        typing_delay = delay_handler.calculate_delay(text)
        
        # Send typing indicator
        await instagram_handler.send_typing_indicator(recipient_id, "on")
        
        # Wait for human-like delay
        await asyncio.sleep(typing_delay)
        
        # Send actual message
        await instagram_handler.send_text_message(recipient_id, text)
        
        # Turn off typing indicator
        await instagram_handler.send_typing_indicator(recipient_id, "off")
        
        logger.info(f"Sent message to {recipient_id} with {typing_delay}s delay")
    
    except Exception as e:
        logger.error(f"Error sending text message: {str(e)}")


async def send_media_response(recipient_id: str, media_data: dict):
    """
    Send media (image or audio) to user
    """
    try:
        media_type = media_data["type"]
        media_path = media_data["path"]
        
        if media_type == "image":
            await instagram_handler.send_image(recipient_id, media_path)
            logger.info(f"Sent image to {recipient_id}")
        
        elif media_type == "audio":
            await instagram_handler.send_audio(recipient_id, media_path)
            logger.info(f"Sent audio to {recipient_id}")
    
    except Exception as e:
        logger.error(f"Error sending media: {str(e)}")


def cleanup_tasks():
    """Remove completed tasks from the task dictionary"""
    completed = [key for key, task in message_tasks.items() if task.done()]
    for key in completed:
        del message_tasks[key]


@app.get("/stats")
async def get_stats():
    """Get chatbot statistics"""
    return {
        "active_sessions": session_manager.get_active_count(),
        "active_tasks": len(message_tasks),
        "total_conversations": session_manager.get_total_count()
    }


@app.post("/test/send")
async def test_send_message(request: Request):
    """Test endpoint to send a message (for development)"""
    data = await request.json()
    recipient_id = data.get("recipient_id")
    message = data.get("message")
    
    await send_text_with_delay(recipient_id, message)
    return {"status": "sent"}


@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Standalone chat endpoint for testing without Instagram
    MVP: NLP responses + typing delays + media triggers
    """
    try:
        data = await request.json()
        user_id = data.get("user_id", "test_user")
        message_text = data.get("message", "").strip()
        
        if not message_text:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info(f"Chat request from {user_id}: {message_text}")
        
        # Update user session
        session_manager.add_message(user_id, "user", message_text)
        
        # Calculate typing delay
        conversation_history = session_manager.get_context(user_id)
        ai_response = await openai_handler.generate_response(
            message_text, 
            conversation_history
        )
        
        typing_delay = delay_handler.calculate_delay(ai_response)
        
        # Update session with bot response
        session_manager.add_message(user_id, "assistant", ai_response)
        
        # Don't sleep here - let frontend handle the typing delay for better UX
        
        # Prepare response
        response_data = {
            "response": ai_response,
            "typing_delay": typing_delay,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Responding to {user_id} after {typing_delay}s delay")
        
        return JSONResponse(response_data, status_code=200)
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
