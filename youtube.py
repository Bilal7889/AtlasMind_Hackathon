"""
YouTube transcript fetching using yt-dlp
"""

import re
import subprocess
import json
import os
import tempfile
from typing import Dict


def parse_youtube_url(url: str) -> str:
    """
    Extract video ID from YouTube URL
    
    Args:
        url: YouTube URL or video ID
    
    Returns:
        Video ID if valid, None otherwise
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript_ytdlp(video_url: str) -> Dict:
    """
    Fetch transcript using yt-dlp (more reliable)
    
    Args:
        video_url: YouTube URL or video ID
    
    Returns:
        Dict with success status, video_id, and transcript or error message
    """
    video_id = parse_youtube_url(video_url)
    if not video_id:
        return {"success": False, "error": "Invalid YouTube URL"}
    
    print(f"Fetching transcript: {video_id}")
    
    try:
        # Check if yt-dlp is available
        check_cmd = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if check_cmd.returncode != 0:
            return {"success": False, "error": "yt-dlp not installed or not accessible"}
        
        print(f"Using yt-dlp version: {check_cmd.stdout.strip()}")
        
        # Use temp directory for file operations
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f'temp_{video_id}')
        
        print(f"Output path: {output_path}")
        
        # Use yt-dlp to get subtitles
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--write-auto-sub',
            '--sub-lang', 'en',
            '--sub-format', 'json3',
            '--output', output_path,
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        print("Downloading subtitles...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Debug: Print subprocess output
        if result.stdout:
            print(f"yt-dlp stdout: {result.stdout[:200]}")
        if result.stderr:
            print(f"yt-dlp stderr: {result.stderr[:200]}")
        
        # Read the subtitle file from temp directory
        subtitle_file = f'{output_path}.en.json3'
        
        # Check if file exists
        if not os.path.exists(subtitle_file):
            # Try current directory as fallback
            fallback_file = f'temp_{video_id}.en.json3'
            if os.path.exists(fallback_file):
                subtitle_file = fallback_file
            else:
                print(f"File not found: {subtitle_file}")
                print(f"Also checked: {fallback_file}")
                print(f"Temp directory: {temp_dir}")
                print(f"Temp dir contents: {os.listdir(temp_dir)[:10]}")
                return {"success": False, "error": f"No subtitle file created. Video might not have captions. Check logs."}
        
        try:
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                subtitle_data = json.load(f)
            
            # Extract text from subtitle events
            transcript_parts = []
            for event in subtitle_data.get('events', []):
                if 'segs' in event:
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            transcript_parts.append(seg['utf8'])
            
            full_transcript = ' '.join(transcript_parts).strip()
            
            # Cleanup temp file
            try:
                if os.path.exists(subtitle_file):
                    os.remove(subtitle_file)
                    print(f"Cleaned up: {subtitle_file}")
            except Exception as e:
                print(f"Cleanup warning: {e}")
            
            if full_transcript:
                print(f"Got transcript: {len(full_transcript)} chars")
                return {
                    "success": True,
                    "video_id": video_id,
                    "transcript": full_transcript
                }
            else:
                return {"success": False, "error": "No subtitles found in file"}
                
        except FileNotFoundError:
            return {"success": False, "error": "No subtitle file created. Video might not have captions."}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout. Try again or use a different video."}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}
