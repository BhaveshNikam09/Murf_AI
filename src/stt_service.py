import requests
import os
from logger import logger

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
ASSEMBLYAI_URL = "https://api.assemblyai.com/v2/transcript"

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio using AssemblyAI and returns the text.
    """
    try:
        logger.info(f"Starting transcription for: {file_path}")

        if not ASSEMBLYAI_API_KEY:
            logger.error("AssemblyAI API key is missing.")
            return "AssemblyAI API key not set."

        headers = {"authorization": ASSEMBLYAI_API_KEY}

        # Upload audio
        upload_url = "https://api.assemblyai.com/v2/upload"
        with open(file_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f)
        if upload_res.status_code != 200:
            logger.error(f"Upload failed: {upload_res.status_code} {upload_res.text}")
            return "Audio upload failed."

        audio_url = upload_res.json().get("upload_url")
        if not audio_url:
            logger.error(f"No audio URL returned: {upload_res.text}")
            return "Audio upload failed."

        # Request transcription
        json_data = {"audio_url": audio_url}
        transcript_res = requests.post(ASSEMBLYAI_URL, headers=headers, json=json_data)
        if transcript_res.status_code != 200:
            logger.error(f"Transcription request failed: {transcript_res.status_code} {transcript_res.text}")
            return "Transcription request failed."

        transcript_id = transcript_res.json().get("id")
        if not transcript_id:
            logger.error(f"No transcript ID returned: {transcript_res.text}")
            return "Transcription request failed."

        # Poll until complete
        while True:
            poll_res = requests.get(f"{ASSEMBLYAI_URL}/{transcript_id}", headers=headers)
            if poll_res.status_code != 200:
                logger.error(f"Polling failed: {poll_res.status_code} {poll_res.text}")
                return "Polling failed."

            status = poll_res.json().get("status")
            if status == "completed":
                text = poll_res.json().get("text", "")
                logger.info("Transcription completed successfully")
                return text
            elif status == "error":
                logger.error(f"Transcription failed: {poll_res.json()}")
                return "Transcription failed."
    except Exception as e:
        logger.exception(f"Error during transcription: {e}")
        return "Error transcribing audio."
