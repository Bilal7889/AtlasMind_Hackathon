"""
Data models and state management for AtlasMind.
Separate sessions for Video and PDF so each tab has its own content, notes, and quiz.
"""

from typing import Dict, List

class ContentState:
    """State for one content source (video or PDF): transcript, vector collection."""
    def __init__(self):
        self.transcript = ""
        self.content_id = ""
        self.collection = None

    def reset(self):
        self.transcript = ""
        self.content_id = ""
        self.collection = None

    def is_loaded(self) -> bool:
        return bool(self.transcript and self.content_id)


class QuizState:
    """Quiz progress and results for one content source."""
    def __init__(self):
        self.questions: List[Dict] = []
        self.current_q = 0
        self.score = 0
        self.answers: List[Dict] = []

    def reset(self):
        self.questions = []
        self.current_q = 0
        self.score = 0
        self.answers = []

    def add_answer(self, answer: Dict):
        self.answers.append(answer)
        if answer.get("is_correct"):
            self.score += 1

    def get_progress(self) -> tuple:
        return (self.current_q + 1, len(self.questions))

    def get_percentage(self) -> int:
        if not self.questions:
            return 0
        return int((self.score / len(self.questions)) * 100)


# Separate session per content type: active tab shows its own data
video_session = ContentState()
pdf_session = ContentState()
video_quiz_state = QuizState()
pdf_quiz_state = QuizState()


def get_session(source: str) -> ContentState:
    """source is 'video' or 'pdf'."""
    return video_session if source == "video" else pdf_session


def get_quiz_state(source: str) -> QuizState:
    """source is 'video' or 'pdf'."""
    return video_quiz_state if source == "video" else pdf_quiz_state
