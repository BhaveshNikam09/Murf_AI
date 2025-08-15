# src/tts_service.py
import os
import requests
from logger import logger
from gtts import gTTS

MURF_API_KEY = os.getenv("MURF_API_KEY")
MURF_URL = "https://api.murf.ai/v1/speech/generate"

def synthesize_speech(text: str, voice_id: str = "en-US-charles") -> str:
    """
    Converts text to speech using Murf AI, falls back to gTTS if Murf fails.
    Returns the path to the audio file.
    """
    output_file = "static/output.mp3"

    try:
        logger.info("Attempting TTS with Murf AI")
        
        headers = {
            "accept": "application/json",
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "voiceId": voice_id,
            "text": text,
            "format": "MP3"
        }

        response = requests.post(MURF_URL, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        audio_url = data.get("audioFile")

        if audio_url:
            audio_data = requests.get(audio_url)
            with open(output_file, "wb") as f:
                f.write(audio_data.content)
            logger.info("TTS generated successfully with Murf AI")
            return output_file
        else:
            logger.warning("Murf returned no audio URL, using fallback.")
            return tts_fallback(text, output_file)

    except Exception as e:
        logger.exception(f"Murf AI TTS failed: {e}")
        return tts_fallback(text, output_file)


def tts_fallback(text: str, output_file: str) -> str:
    """
    Fallback TTS using Google gTTS.
    """
    try:
        logger.info("Using gTTS fallback")
        tts = gTTS(text=text, lang="en")
        tts.save(output_file)
        return output_file
    except Exception as e:
        logger.exception(f"gTTS fallback failed: {e}")
        return "static/fallback.mp3"
