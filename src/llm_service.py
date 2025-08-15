import os
import requests
from logger import logger

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_llm_reply(chat_history: list) -> str:
    """
    Sends chat history to Groq LLM and returns the model's reply.
    """
    try:
        logger.info("Sending chat history to LLM")

        if not GROQ_API_KEY:
            logger.error("Groq API key is missing.")
            return "Groq API key not set."

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        messages.extend(chat_history)

        payload = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.7
        }

        response = requests.post(GROQ_URL, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(f"Groq request failed: {response.status_code} {response.text}")
            return "LLM request failed."

        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content")
        if not reply:
            logger.error(f"No reply in Groq response: {response.text}")
            return "LLM did not return a reply."

        logger.info("LLM reply generated successfully")
        return reply

    except Exception as e:
        logger.exception(f"Error while getting LLM reply: {e}")
        return "I'm having trouble connecting to the AI service right now."
