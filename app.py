import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Always load .env from the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

from src.stt_service import transcribe_audio
from src.llm_service import get_llm_reply
from src.tts_service import synthesize_speech
from logger import logger

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, ".", "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Serving homepage")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), voice: str = "en-US-charles"):
    try:
        logger.info(f"Audio uploaded: {file.filename}")

        # Save uploaded file
        uploads_dir = os.path.join(BASE_DIR, "..", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Speech-to-text
        transcription = transcribe_audio(file_path)
        if not transcription:
            logger.warning("Transcription failed")
            return JSONResponse({"error": "Error transcribing audio", "fallback": True})

        # LLM reply
        reply_text = get_llm_reply(transcription)
        if not reply_text:
            logger.warning("LLM reply failed")
            return JSONResponse({"error": "Error generating AI reply", "fallback": True})

        # Text-to-speech
        audio_url = synthesize_speech(reply_text, voice)
        if not audio_url:
            logger.warning("TTS failed, using fallback")
            audio_url = "/static/fallback.mp3"

        logger.info("Processing complete")
        return {"transcription": transcription, "reply": reply_text, "audio_url": audio_url}

    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return JSONResponse({"error": "Unexpected server error", "fallback": True})
