from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from pathlib import Path
import os
import time
import uuid
from logger import logger  # custom logger
from gtts import gTTS  # for fallback audio

# Load environment variables
load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

STATIC_FOLDER = Path("static")
STATIC_FOLDER.mkdir(exist_ok=True)

# API Keys
MURF_API_URL = "https://api.murf.ai/v1/speech/generate"
MURF_API_KEY = os.getenv("MURF_API_KEY")

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
ASSEMBLYAI_TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Store chat history in memory
chat_history = []

class TTSRequest(BaseModel):
    text: str
    voiceId: str

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    logger.info("Serving homepage")
    return templates.TemplateResponse("index.html", {"request": request})

def transcribe_with_assemblyai(file_path: Path) -> str:
    try:
        logger.info(f"Starting transcription for: {file_path}")
        with open(file_path, "rb") as f:
            upload_res = requests.post(
                ASSEMBLYAI_UPLOAD_URL,
                headers={"authorization": ASSEMBLYAI_API_KEY},
                data=f
            )
        upload_res.raise_for_status()
        upload_url = upload_res.json().get("upload_url")

        transcript_req = requests.post(
            ASSEMBLYAI_TRANSCRIPT_URL,
            headers={"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"},
            json={"audio_url": upload_url}
        )
        transcript_req.raise_for_status()
        transcript_id = transcript_req.json().get("id")

        while True:
            poll_res = requests.get(
                f"{ASSEMBLYAI_TRANSCRIPT_URL}/{transcript_id}",
                headers={"authorization": ASSEMBLYAI_API_KEY}
            ).json()
            if poll_res["status"] == "completed":
                logger.info("Transcription completed successfully")
                return poll_res["text"]
            elif poll_res["status"] == "error":
                raise Exception(f"AssemblyAI Error: {poll_res.get('error')}")
            time.sleep(2)
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return None

def generate_fallback_audio():
    """Generate a fallback audio file locally if Murf fails."""
    fallback_path = STATIC_FOLDER / "fallback.mp3"
    if not fallback_path.exists():  # Only create once
        tts = gTTS("I'm having trouble connecting right now.", lang="en")
        tts.save(fallback_path)
        logger.info(f"Fallback audio generated at {fallback_path}")
    return f"/static/{fallback_path.name}"

@app.post("/llm/query")
async def llm_query(file: UploadFile = File(...), voiceId: str = Form("en-US-charles")):
    global chat_history
    try:
        # Save uploaded audio
        file_path = UPLOAD_FOLDER / f"{uuid.uuid4()}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Audio uploaded: {file_path}")

        # Transcription
        transcript_text = transcribe_with_assemblyai(file_path)
        if not transcript_text:
            return {
                "transcript": "[Error: Could not transcribe]",
                "llm_reply": "I'm having trouble connecting right now.",
                "murf_audio_url": generate_fallback_audio(),
                "history": chat_history
            }

        # LLM reply
        try:
            llm_res = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": transcript_text}], "max_tokens": 500}
            )
            llm_res.raise_for_status()
            llm_reply = llm_res.json()["choices"][0]["message"]["content"].strip()
            logger.info("LLM reply generated successfully")
        except Exception as e:
            logger.error(f"LLM API failed: {e}")
            llm_reply = "I'm having trouble connecting right now."

        chat_history.append({"user": transcript_text, "bot": llm_reply})

        # Murf TTS
        try:
            murf_res = requests.post(
                MURF_API_URL,
                headers={"Content-Type": "application/json", "api-key": MURF_API_KEY},
                json={"text": llm_reply, "voiceId": voiceId}
            )
            logger.info(f"Murf API raw response: {murf_res.text}")
            murf_res.raise_for_status()
            murf_audio_url = murf_res.json().get("audioUrl")

            if murf_audio_url:
                try:
                    audio_data = requests.get(murf_audio_url).content
                    local_audio_path = STATIC_FOLDER / f"{uuid.uuid4()}.mp3"
                    with open(local_audio_path, "wb") as f:
                        f.write(audio_data)
                    murf_audio_url = f"/static/{local_audio_path.name}"
                    logger.info(f"Murf audio saved locally: {local_audio_path}")
                except Exception as e:
                    logger.error(f"Failed to download Murf audio: {e}")
                    murf_audio_url = generate_fallback_audio()
            else:
                logger.warning("Murf returned no audio URL, using fallback.")
                murf_audio_url = generate_fallback_audio()

        except Exception as e:
            logger.error(f"Murf TTS failed: {e}")
            murf_audio_url = generate_fallback_audio()

        return {
            "transcript": transcript_text,
            "llm_reply": llm_reply,
            "murf_audio_url": murf_audio_url,
            "history": chat_history
        }
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        return {
            "transcript": "[Error: Could not process request]",
            "llm_reply": "I'm having trouble connecting right now.",
            "murf_audio_url": generate_fallback_audio(),
            "history": chat_history
        }
