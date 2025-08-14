# 🎤 LLM Voice Bot – 30 Days of AI Voice Agents Challenge

## 📌 Project Overview
The **LLM Voice Bot** is an AI-powered conversational agent that allows users to interact using voice.  
It listens to the user, transcribes their speech to text, generates an intelligent response using an LLM, and speaks the reply back in a natural human-like voice.

This project is part of the **30 Days of AI Voice Agents Challenge**, where the bot evolved from a basic echo bot to a full-fledged conversational AI assistant with:
- Real-time voice input
- Context-aware replies
- Automatic fallback voice generation
- Chat history memory
- A polished UI

---

## 🛠️ Technologies Used
- **[FastAPI](https://fastapi.tiangolo.com/)** – Backend API
- **[AssemblyAI](https://www.assemblyai.com/)** – Speech-to-Text (STT)
- **[Groq LLM](https://groq.com/)** – Large Language Model for generating replies
- **[Murf AI](https://murf.ai/)** – Text-to-Speech (TTS) with natural voices
- **[gTTS](https://pypi.org/project/gTTS/)** – Fallback Text-to-Speech
- **HTML, CSS, JavaScript** – Frontend UI
- **Jinja2** – Templating
- **Python Logging** – Application logs
- **UUID & Pathlib** – File handling

---

## 🏗️ Architecture
```plaintext
User Audio 🎤 → FastAPI Backend → AssemblyAI (STT)  
→ Chat History + Groq LLM (Reply)  
→ Murf AI (TTS) or gTTS Fallback 🎧 → UI Playback
```

---

## ✨ Features
- 🎙 **Voice Input** – Start/stop recording directly from the UI.
- 📝 **Live Transcription** – Accurate speech-to-text conversion using AssemblyAI.
- 🤖 **LLM-Powered Replies** – Context-aware responses with Groq LLM.
- 🔊 **Natural Voice Output** – High-quality Murf AI speech synthesis.
- 🛡 **Fallback Audio** – gTTS-generated audio if Murf AI fails.
- 🗂 **Chat History** – Maintains conversation context for better responses.
- 🎨 **Responsive UI** – Clean design with prominent record button.

---

## 📂 Project Structure
```
.
├── app.py               # FastAPI backend
├── logger.py            # Logger configuration
├── templates/
│   └── index.html       # UI template
├── static/
│   ├── styles.css       # Styling
│   ├── fallback.mp3     # Fallback audio
│   └── <audio_files>.mp3
├── uploads/             # User audio uploads
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## ⚙️ Environment Variables
Before running the project, create a `.env` file with:
```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
MURF_API_KEY=your_murf_api_key
GROQ_API_KEY=your_groq_api_key
```

---

## 🚀 Running the Project

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Run FastAPI server
```bash
uvicorn app:app --reload
```

### 3️⃣ Access the UI
Open your browser and go to:
```
http://127.0.0.1:8000
```

---

## 📸 Screenshots
![UI Screenshot](static/ui_screenshot.png)
![Chat History](static/chat_history_screenshot.png)

---

## 📜 License
This project is for learning purposes under the **30 Days of AI Voice Agents Challenge**.

---

## 🙌 Acknowledgements
- **AssemblyAI** for transcription API
- **Murf AI** for TTS
- **Groq** for LLM access
- **gTTS** for fallback TTS
- All open-source libraries used
