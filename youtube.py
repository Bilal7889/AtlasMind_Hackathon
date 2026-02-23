"""
YouTube transcript fetching using youtube-transcript-api (works on Hugging Face, no subprocess).
"""

import re
from typing import Dict, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
    HAS_API = True
except ImportError:
    HAS_API = False


def parse_youtube_url(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL or return None."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript(video_url: str) -> Dict:
    """
    Fetch transcript using youtube-transcript-api (no external CLI; works on Hugging Face).

    Returns:
        Dict with success, video_id, transcript or error.
    """
    if not HAS_API:
        return {"success": False, "error": "youtube-transcript-api not installed. pip install youtube-transcript-api"}

    video_id = parse_youtube_url(video_url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL"}

    print(f"Fetching transcript: {video_id}")

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled:
        return {"success": False, "error": "Transcripts are disabled for this video."}
    except NoTranscriptFound:
        return {"success": False, "error": "No transcript found for this video."}
    except VideoUnavailable:
        return {"success": False, "error": "Video is unavailable or private."}
    except Exception as e:
        return {"success": False, "error": str(e)}

    if not transcript_list:
        return {"success": False, "error": "No transcript content returned."}

    full_transcript = " ".join(entry.get("text", "") for entry in transcript_list).strip()
    if not full_transcript:
        return {"success": False, "error": "Transcript is empty."}

    print(f"Got transcript: {len(full_transcript)} chars")
    return {
        "success": True,
        "video_id": video_id,
        "transcript": full_transcript,
    }


def fetch_transcript_ytdlp(video_url: str) -> Dict:
    """Alias for fetch_transcript (kept for backward compatibility with rag.py)."""
    return fetch_transcript(video_url)
