"""
Data models and state management for AtlasMind
"""

from typing import Dict, List, Optional

class VideoState:
    """Manages current video information"""
    def __init__(self):
        self.transcript = ""
        self.video_id = ""
        self.collection = None
    
    def reset(self):
        """Reset video state"""
        self.transcript = ""
        self.video_id = ""
        self.collection = None
    
    def is_loaded(self) -> bool:
        """Check if a video is currently loaded"""
        return bool(self.transcript and self.video_id)


class QuizState:
    """Manages quiz progress and results"""
    def __init__(self):
        self.questions: List[Dict] = []
        self.current_q = 0
        self.score = 0
        self.answers: List[Dict] = []
    
    def reset(self):
        """Reset quiz state"""
        self.questions = []
        self.current_q = 0
        self.score = 0
        self.answers = []
    
    def add_answer(self, answer: Dict):
        """Record an answer"""
        self.answers.append(answer)
        if answer["is_correct"]:
            self.score += 1
    
    def get_progress(self) -> tuple:
        """Get current quiz progress (current, total)"""
        return (self.current_q + 1, len(self.questions))
    
    def get_percentage(self) -> int:
        """Get final score as percentage"""
        if not self.questions:
            return 0
        return int((self.score / len(self.questions)) * 100)


# Global state instances - Dual storage for video and PDF
video_state = VideoState()
pdf_state = VideoState()
quiz_state = QuizState()

# Active source tracking
active_source_type = "video"  # Can be "video" or "pdf"

def get_active_state() -> VideoState:
    """Get the currently active content state (video or PDF)"""
    return video_state if active_source_type == "video" else pdf_state

def set_active_source(source_type: str):
    """Set which content source is active"""
    global active_source_type
    if source_type in ["video", "pdf"]:
        active_source_type = source_type
        print(f"Active source switched to: {source_type}")

# For backward compatibility
current_video = get_active_state()
