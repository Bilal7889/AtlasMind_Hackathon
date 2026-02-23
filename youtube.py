"""
YouTube transcript fetching using yt-dlp (library: CLI or Python API).
Uses Python API when possible to avoid subprocess; falls back to CLI for compatibility.
"""

import json
import os
import re
import subprocess
import tempfile
from typing import Dict, Optional

def parse_youtube_url(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL or return None."""
    url = (url or "").strip()
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


def _transcript_from_json3(data: dict) -> str:
    """Extract plain text from json3 subtitle data."""
    parts = []
    for event in data.get("events", []):
        for seg in event.get("segs", []):
            text = seg.get("utf8", "").strip()
            if text:
                parts.append(text)
    return " ".join(parts).strip()


def _fetch_via_python_api(video_id: str) -> Optional[Dict]:
    """Use yt-dlp Python API to get transcript. Returns result dict or None on failure."""
    try:
        import yt_dlp
    except ImportError:
        return None

    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "json3",
        "quiet": True,
        "no_warnings": True,
    }
    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    opts["outtmpl"] = os.path.join(tmp_dir, "%(id)s.%(ext)s")

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        # Look for the generated subtitle file
        for f in os.listdir(tmp_dir):
            if f.endswith(".en.json3"):
                path = os.path.join(tmp_dir, f)
                with open(path, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                text = _transcript_from_json3(data)
                try:
                    os.remove(path)
                except OSError:
                    pass
                if os.path.exists(tmp_dir):
                    try:
                        os.rmdir(tmp_dir)
                    except OSError:
                        pass
                if text:
                    return {"success": True, "video_id": video_id, "transcript": text}
                break
    except Exception:
        pass
    if os.path.exists(tmp_dir):
        try:
            for f in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, f))
            os.rmdir(tmp_dir)
        except OSError:
            pass
    return None


def _fetch_via_cli(video_url: str, video_id: str) -> Dict:
    """Use yt-dlp CLI (subprocess) to get transcript."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=5, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return {"success": False, "error": "yt-dlp CLI not available. Install with: pip install yt-dlp"}

    tmp_dir = tempfile.gettempdir()
    out_path = os.path.join(tmp_dir, f"atlasmind_{video_id}")

    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-auto-sub",
        "--sub-lang", "en",
        "--sub-format", "json3",
        "--output", out_path,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout fetching transcript. Try again or another video."}

    sub_file = f"{out_path}.en.json3"
    if not os.path.exists(sub_file):
        return {"success": False, "error": "No captions found for this video."}

    try:
        with open(sub_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        text = _transcript_from_json3(data)
        try:
            os.remove(sub_file)
        except OSError:
            pass
        if text:
            return {"success": True, "video_id": video_id, "transcript": text}
        return {"success": False, "error": "Transcript was empty."}
    except (json.JSONDecodeError, OSError) as e:
        if os.path.exists(sub_file):
            try:
                os.remove(sub_file)
            except OSError:
                pass
        return {"success": False, "error": str(e)}


def fetch_transcript_ytdlp(video_url: str) -> Dict:
    """
    Fetch transcript using yt-dlp. Tries Python API first, then CLI.
    Returns dict with success, video_id, transcript or error.
    """
    video_id = parse_youtube_url(video_url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL"}

    print(f"Fetching transcript: {video_id}")

    # Prefer Python API (no subprocess)
    result = _fetch_via_python_api(video_id)
    if result is not None:
        print(f"Got transcript: {len(result['transcript'])} chars")
        return result

    # Fallback to CLI
    result = _fetch_via_cli(video_url, video_id)
    if result.get("success"):
        print(f"Got transcript: {len(result['transcript'])} chars")
    return result
