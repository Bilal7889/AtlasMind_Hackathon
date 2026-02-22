"""
Quiz generation and management for AtlasMind
"""

from typing import Dict, Tuple
import gradio as gr
from models import current_video, quiz_state
from llm import ask_groq
from config import QUIZ_CONTEXT_LENGTH


def generate_quiz_data(num_questions: int = 5) -> Dict:
    """
    Generate structured quiz data from video
    
    Args:
        num_questions: Number of questions to generate
    
    Returns:
        Dict with success status and error message or question count
    """
    if not current_video.transcript:
        return {"success": False, "error": "Please process a video or PDF first!"}
    
    print(f"\nGenerating {num_questions} quiz questions...")
    
    prompt = f"""Create {num_questions} multiple choice questions based on this content (lecture or document).

Format EXACTLY like this (use ### as separator):

QUESTION: [clear question text]
A: [option A text]
B: [option B text]
C: [option C text]
D: [option D text]
CORRECT: [A/B/C/D]
EXPLANATION: [2-3 sentence explanation of why this answer is correct]
###
QUESTION: [next question]
...

Transcript: {current_video.transcript[:QUIZ_CONTEXT_LENGTH]}"""
    
    response = ask_groq(prompt)
    
    # Parse the response
    questions = []
    quiz_blocks = response.split('###')
    
    for block in quiz_blocks:
        if 'QUESTION:' in block:
            try:
                lines = block.strip().split('\n')
                q_data = {}
                
                for line in lines:
                    if line.startswith('QUESTION:'):
                        q_data['question'] = line.replace('QUESTION:', '').strip()
                    elif line.startswith('A:'):
                        q_data['A'] = line.replace('A:', '').strip()
                    elif line.startswith('B:'):
                        q_data['B'] = line.replace('B:', '').strip()
                    elif line.startswith('C:'):
                        q_data['C'] = line.replace('C:', '').strip()
                    elif line.startswith('D:'):
                        q_data['D'] = line.replace('D:', '').strip()
                    elif line.startswith('CORRECT:'):
                        q_data['correct'] = line.replace('CORRECT:', '').strip().upper()[0]
                    elif line.startswith('EXPLANATION:'):
                        q_data['explanation'] = line.replace('EXPLANATION:', '').strip()
                
                if 'question' in q_data and 'correct' in q_data:
                    questions.append(q_data)
            except:
                continue
    
    if questions:
        quiz_state.reset()
        quiz_state.questions = questions
        print(f"Generated {len(questions)} questions!\n")
        return {"success": True, "count": len(questions)}
    else:
        return {"success": False, "error": "Failed to parse quiz questions"}


def start_quiz(num_questions: int) -> tuple:
    """
    Initialize quiz and show first question
    
    Args:
        num_questions: Number of questions to generate
    
    Returns:
        Tuple of display elements for first question
    """
    result = generate_quiz_data(num_questions)
    
    if not result["success"]:
        return (
            result.get("error", "Error generating quiz"),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            ""
        )
    
    return show_current_question()


def show_current_question() -> Tuple:
    """
    Display current question
    
    Returns:
        Tuple of display elements for current question
    """
    if not quiz_state.questions:
        return ("No quiz generated", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), "")
    
    current_idx = quiz_state.current_q
    total = len(quiz_state.questions)
    
    if current_idx >= total:
        # Quiz finished
        return show_final_results()
    
    q = quiz_state.questions[current_idx]
    
    question_text = f"""## Question {current_idx + 1} of {total}

### {q['question']}
"""
    
    choices = [
        f"A: {q.get('A', 'N/A')}",
        f"B: {q.get('B', 'N/A')}",
        f"C: {q.get('C', 'N/A')}",
        f"D: {q.get('D', 'N/A')}"
    ]
    
    return (
        question_text,
        gr.update(choices=choices, value=None, visible=True, interactive=True),
        gr.update(visible=True),
        gr.update(visible=False),
        ""
    )


def check_answer(selected_option: str) -> Tuple:
    """
    Check if answer is correct and show feedback
    
    Args:
        selected_option: User's selected answer
    
    Returns:
        Tuple of display elements with feedback
    """
    if not selected_option:
        return (
            gr.update(),
            gr.update(),
            gr.update(visible=False),
            gr.update(visible=False),
            "Please select an option!"
        )
    
    current_idx = quiz_state.current_q
    q = quiz_state.questions[current_idx]
    
    # Extract letter from selection ("A: text" -> "A")
    user_answer = selected_option[0].upper()
    correct_answer = q["correct"]
    
    is_correct = (user_answer == correct_answer)
    
    # Record answer
    quiz_state.add_answer({
        "question": q["question"],
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct
    })
    
    # Feedback message
    if is_correct:
        feedback = f"""## ✅ Correct!

**Explanation:** {q.get('explanation', 'Good job!')}
"""
    else:
        feedback = f"""## ❌ Incorrect

**Correct Answer:** {correct_answer}: {q.get(correct_answer, 'N/A')}

**Explanation:** {q.get('explanation', 'Review the material.')}
"""
    
    return (
        gr.update(),
        gr.update(interactive=False),
        gr.update(visible=False),
        gr.update(visible=True),
        feedback
    )


def next_question() -> Tuple:
    """
    Move to next question
    
    Returns:
        Tuple of display elements for next question
    """
    quiz_state.current_q += 1
    return show_current_question()


def show_final_results() -> Tuple:
    """
    Display final quiz results
    
    Returns:
        Tuple of display elements with final results
    """
    score = quiz_state.score
    total = len(quiz_state.questions)
    percentage = quiz_state.get_percentage()
    
    result_text = f"""# 🎉 Quiz Complete!

## Your Score: {score}/{total} ({percentage}%)

"""
    
    if percentage >= 80:
        result_text += "### 🌟 Excellent! You've mastered this content!\n\n"
    elif percentage >= 60:
        result_text += "### 👍 Good job! Keep practicing!\n\n"
    else:
        result_text += "### 📚 Review the material and try again!\n\n"
    
    result_text += "### 📊 Question Review:\n\n"
    
    for i, answer in enumerate(quiz_state.answers):
        icon = "✅" if answer["is_correct"] else "❌"
        result_text += f"{i+1}. {icon} {answer['question'][:60]}...\n"
        if not answer["is_correct"]:
            result_text += f"   - Your answer: {answer['user_answer']} | Correct: {answer['correct_answer']}\n"
    
    return (
        result_text,
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        ""
    )
