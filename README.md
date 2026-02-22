---
title: AtlasMind
emoji: 🧠
colorFrom: gray
colorTo: green
sdk: gradio
sdk_version: "5.16.1"
app_file: app.py
pinned: false
python_version: "3.11"
---

# AtlasMind

Paste a YouTube video link or upload a PDF — get AI-generated notes, summary, and quiz.

## Setup

**Required:** Add `GROQ_API_KEY` in your Space **Settings → Variables and secrets** (create a secret, name it `GROQ_API_KEY`, value = your Groq API key from [console.groq.com](https://console.groq.com)).

Without this, the Process button will show a configuration error.

---

## Deploy elsewhere (YouTube + PDF both work)

Hugging Face Spaces can block YouTube/yt-dlp. For a single place where **both video and PDF work** with minimal setup:

### Option A: Railway (recommended, free tier)

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. **New Project** → **Deploy from GitHub repo** → select your AtlasMind repo.
3. Add variable: `GROQ_API_KEY` = your Groq API key.
4. Railway will detect Python and run `python app.py`. The app uses `PORT` automatically.
5. Open the generated URL. YouTube and PDF should both work.

### Option B: Render

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. **New** → **Web Service** → connect your AtlasMind repo.
3. **Environment**: add `GROQ_API_KEY`.
4. Build command: `pip install -r requirements.txt` (or leave default).
5. Start command: `python app.py` (or use the `Procfile`: `web: python app.py`).
6. Deploy. Use the given URL.

Both use the same code; no YouTube blocking.
