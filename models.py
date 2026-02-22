"""
Data models and state management for AtlasMind
"""

from typing import Dict, List, Optional

class VideoState:
    """Manages current content (video or PDF) for RAG/quiz/notes."""
    def __init__(self):
        self.transcript = ""
        self.video_id = ""   # content_id: YouTube video ID or pdf_<hash>
        self.collection = None
        self.source_type = ""  # "video" | "pdf"

    def reset(self):
        """Reset content state"""
        self.transcript = ""
        self.video_id = ""
        self.collection = None
        self.source_type = ""

    def is_loaded(self) -> bool:
        """Check if content is currently loaded (video or PDF)"""
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


# Global state instances
current_video = VideoState()
quiz_state = QuizState()
