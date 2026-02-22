"""
Quiz generation and management. Separate quiz state per source (video / pdf).
"""

from typing import Dict, Tuple
import gradio as gr
from models import get_session, get_quiz_state
from llm import ask_groq
from config import QUIZ_CONTEXT_LENGTH


def generate_quiz_data(num_questions: int, source: str) -> Dict:
    """Generate quiz for the given source ('video' or 'pdf')."""
    session = get_session(source)
    quiz_state = get_quiz_state(source)
    if not session.transcript:
        return {"success": False, "error": "Process a video or PDF in this tab first."}

    prompt = f"""Create {num_questions} multiple choice questions based on this content.

Format EXACTLY like this (use ### as separator):

QUESTION: [clear question text]
A: [option A text]
B: [option B text]
C: [option C text]
D: [option D text]
CORRECT: [A/B/C/D]
EXPLANATION: [2-3 sentence explanation]
###
QUESTION: [next question]
...

Transcript: {session.transcript[:QUIZ_CONTEXT_LENGTH]}"""

    response = ask_groq(prompt)
    questions = []
    for block in response.split("###"):
        if "QUESTION:" not in block:
            continue
        try:
            lines = block.strip().split("\n")
            q_data = {}
            for line in lines:
                if line.startswith("QUESTION:"):
                    q_data["question"] = line.replace("QUESTION:", "").strip()
                elif line.startswith("A:"):
                    q_data["A"] = line.replace("A:", "").strip()
                elif line.startswith("B:"):
                    q_data["B"] = line.replace("B:", "").strip()
                elif line.startswith("C:"):
                    q_data["C"] = line.replace("C:", "").strip()
                elif line.startswith("D:"):
                    q_data["D"] = line.replace("D:", "").strip()
                elif line.startswith("CORRECT:"):
                    q_data["correct"] = line.replace("CORRECT:", "").strip().upper()[0]
                elif line.startswith("EXPLANATION:"):
                    q_data["explanation"] = line.replace("EXPLANATION:", "").strip()
            if "question" in q_data and "correct" in q_data:
                questions.append(q_data)
        except Exception:
            continue

    if questions:
        quiz_state.reset()
        quiz_state.questions = questions
        return {"success": True, "count": len(questions)}
    return {"success": False, "error": "Failed to parse quiz questions."}


def start_quiz(num_questions: int, source: str) -> Tuple:
    """Start quiz for the given source. Returns (question_md, options_update, submit_vis, next_vis, feedback)."""
    result = generate_quiz_data(num_questions, source)
    if not result["success"]:
        return (
            result.get("error", "Error"),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "",
        )
    return _show_current_question(source)


def _show_current_question(source: str) -> Tuple:
    quiz_state = get_quiz_state(source)
    if not quiz_state.questions:
        return ("No quiz", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), "")

    current_idx = quiz_state.current_q
    total = len(quiz_state.questions)
    if current_idx >= total:
        return _show_final_results(source)

    q = quiz_state.questions[current_idx]
    question_text = f"## Question {current_idx + 1} of {total}\n\n### {q['question']}\n"
    choices = [f"A: {q.get('A', 'N/A')}", f"B: {q.get('B', 'N/A')}", f"C: {q.get('C', 'N/A')}", f"D: {q.get('D', 'N/A')}"]

    return (
        question_text,
        gr.update(choices=choices, value=None, visible=True, interactive=True),
        gr.update(visible=True),
        gr.update(visible=False),
        "",
    )


def check_answer(selected_option: str, source: str) -> Tuple:
    quiz_state = get_quiz_state(source)
    if not selected_option:
        return (gr.update(), gr.update(), gr.update(visible=False), gr.update(visible=False), "Please select an option.")

    current_idx = quiz_state.current_q
    q = quiz_state.questions[current_idx]
    user_answer = selected_option[0].upper()
    correct_answer = q["correct"]
    is_correct = user_answer == correct_answer

    quiz_state.add_answer({
        "question": q["question"],
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
    })

    if is_correct:
        feedback = f"## ✅ Correct!\n\n**Explanation:** {q.get('explanation', 'Good job!')}"
    else:
        feedback = f"## ❌ Incorrect\n\n**Correct Answer:** {correct_answer}: {q.get(correct_answer, 'N/A')}\n\n**Explanation:** {q.get('explanation', '')}"

    return (
        gr.update(),
        gr.update(interactive=False),
        gr.update(visible=False),
        gr.update(visible=True),
        feedback,
    )


def next_question(source: str) -> Tuple:
    get_quiz_state(source).current_q += 1
    return _show_current_question(source)


def _show_final_results(source: str) -> Tuple:
    quiz_state = get_quiz_state(source)
    score = quiz_state.score
    total = len(quiz_state.questions)
    pct = quiz_state.get_percentage()
    result_text = f"# 🎉 Quiz Complete!\n\n## Your Score: {score}/{total} ({pct}%)\n\n"
    if pct >= 80:
        result_text += "### 🌟 Excellent!\n\n"
    elif pct >= 60:
        result_text += "### 👍 Good job!\n\n"
    else:
        result_text += "### 📚 Review and try again.\n\n"
    result_text += "### 📊 Review:\n\n"
    for i, a in enumerate(quiz_state.answers):
        icon = "✅" if a["is_correct"] else "❌"
        result_text += f"{i+1}. {icon} {a['question'][:60]}...\n"
        if not a["is_correct"]:
            result_text += f"   Your answer: {a['user_answer']} | Correct: {a['correct_answer']}\n"

    return (
        result_text,
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        "",
    )
