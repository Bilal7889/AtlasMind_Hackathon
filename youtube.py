"""
YouTube transcript fetching using the youtube-transcriptor RapidAPI service.
"""

import os
import re
from typing import Dict, Optional

import requests


def parse_youtube_url(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL or return None."""
    url = (url or "").strip()
    patterns = [
        r"(?:v=|\\/)([0-9A-Za-z_-]{11}).*",
        r"(?:embed\\/)([0-9A-Za-z_-]{11})",
        r"^([0-9A-Za-z_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript_ytdlp(video_url: str) -> Dict:
    """
    Fetch transcript via youtube-transcriptor RapidAPI.

    Returns:
        Dict with keys: success (bool), video_id (str), transcript (str) or error (str).
    """
    video_id = parse_youtube_url(video_url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL"}

    api_key = os.getenv("YOUTUBE_TRANSCRIPTOR_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "YOUTUBE_TRANSCRIPTOR_API_KEY not set. Add it to your environment / .env.",
        }

    url = "https://youtube-transcriptor.p.rapidapi.com/transcript"
    headers = {
        "x-rapidapi-host": "youtube-transcriptor.p.rapidapi.com",
        "x-rapidapi-key": api_key,
    }
    params = {"video_id": video_id, "lang": "en"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
    except requests.RequestException as e:
        return {"success": False, "error": f"Request error: {e}"}

    if resp.status_code != 200:
        return {
            "success": False,
            "error": f"API error {resp.status_code}: {resp.text[:200]}",
        }

    try:
        data = resp.json()
    except ValueError:
        return {"success": False, "error": "Failed to parse API response as JSON."}

    items = data.get("transcription") or []
    if not items:
        return {"success": False, "error": "No transcription data returned from API."}

    text = " ".join((item.get("subtitle") or "").strip() for item in items).strip()
    if not text:
        return {"success": False, "error": "Transcription text is empty."}

    return {"success": True, "video_id": video_id, "transcript": text}
