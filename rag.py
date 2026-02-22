"""
RAG (Retrieval Augmented Generation) for AtlasMind.
Separate sessions for Video and PDF; each tab uses its own session.
"""

import gradio as gr
from models import get_session
from vector_db import semantic_search, store_in_vector_db
from llm import ask_groq
from config import TRANSCRIPT_PREVIEW_LENGTH


def _process_content_text(content_id: str, transcript: str, source_label: str, source: str) -> str:
    """Store text in vector DB, set session state, generate summary. source is 'video' or 'pdf'."""
    session = get_session(source)
    session.transcript = transcript
    session.content_id = content_id
    session.collection = store_in_vector_db(content_id, transcript)

    print("Generating AI summary...")
    prompt = f"""You are AtlasMind, an AI learning companion.

Analyze this content and provide:

## 📝 Summary
A concise 3-4 sentence overview.

## 🔑 Key Concepts
5-7 most important points as bullets.

## 💡 Takeaways
3-5 actionable insights.

Content: {transcript[:TRANSCRIPT_PREVIEW_LENGTH]}"""

    summary = ask_groq(prompt)
    print("Summary generated!")
    return f"""**{source_label} Processed Successfully!**

---

{summary}"""


def process_video(video_url: str, progress=gr.Progress()) -> str:
    """Process YouTube URL for the Video tab. Updates video_session."""
    try:
        from youtube import fetch_transcript_ytdlp
        from config import GROQ_API_KEY

        if not GROQ_API_KEY:
            return "**Configuration error:** `GROQ_API_KEY` is not set."
        video_url = (video_url or "").strip()
        if not video_url:
            return "Please enter a YouTube URL."

        progress(0, desc="Fetching video...")
        result = fetch_transcript_ytdlp(video_url)
        if not result["success"]:
            return f"**Video error:** {result['error']}"

        progress(0.5, desc="Generating summary...")
        out = _process_content_text(
            result["video_id"], result["transcript"], "Video", "video"
        )
        progress(1.0, desc="Done!")
        return out
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"**Error:** {str(e)}"


def process_pdf(pdf_file, progress=gr.Progress()) -> str:
    """Process uploaded PDF for the PDF tab. Updates pdf_session."""
    try:
        from pdf import extract_text_from_pdf
        from config import GROQ_API_KEY

        if not GROQ_API_KEY:
            return "**Configuration error:** `GROQ_API_KEY` is not set."
        pdf_path = None
        if pdf_file is not None:
            if isinstance(pdf_file, list) and len(pdf_file) > 0:
                f = pdf_file[0]
                pdf_path = f if isinstance(f, str) else getattr(f, "name", getattr(f, "path", None))
            elif isinstance(pdf_file, str):
                pdf_path = pdf_file
            else:
                pdf_path = getattr(pdf_file, "name", getattr(pdf_file, "path", None))
        if not pdf_path:
            return "Please upload a PDF file."

        progress(0, desc="Reading PDF...")
        result = extract_text_from_pdf(pdf_path)
        if not result["success"]:
            return f"**PDF error:** {result['error']}"

        progress(0.5, desc="Generating summary...")
        out = _process_content_text(
            result["content_id"], result["transcript"], "PDF", "pdf"
        )
        progress(1.0, desc="Done!")
        return out
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"**Error:** {str(e)}"


def answer_question(question: str, source: str) -> str:
    """Answer using the session for the given source ('video' or 'pdf')."""
    session = get_session(source)
    if not session.transcript:
        return "Process a video or PDF in this tab first."
    if not (question or "").strip():
        return "Please enter a question."

    context = semantic_search(question, session.collection)
    if not context:
        context = session.transcript[:3000]
    prompt = f"""Based on this content (lecture or document), answer the question clearly and concisely.

Question: {question}

Provide a helpful answer."""
    return ask_groq(prompt, context)


def generate_notes(source: str) -> tuple:
    """Generate notes for the given source. Returns (notes_markdown, file_path or None)."""
    session = get_session(source)
    if not session.transcript:
        return ("Process a video or PDF in this tab first.", None)

    prompt = f"""Create DETAILED study notes from this content (lecture or document). Aim for about 1.5 pages of a Word document.

Rules:
- Use CONTENT-SPECIFIC section headings (e.g. "How Backpropagation Works") — NOT generic headings.
- Mix short paragraphs and bullet points. Write to EXPLAIN.
- Cover main concepts in depth.

Content:
{session.transcript[:6000]}"""

    notes = ask_groq(prompt)
    file_path = None
    try:
        file_path = _notes_to_docx(notes)
    except Exception as e:
        print(f"Could not save notes: {e}")
    return (notes, file_path)


def _notes_to_docx(markdown_text: str):
    import os
    import tempfile
    try:
        from docx import Document
    except ImportError:
        raise ImportError("pip install python-docx")

    doc = Document()
    lines = markdown_text.replace("\r\n", "\n").split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("###"):
            doc.add_heading(stripped.lstrip("#").strip(), level=2)
        elif stripped.startswith("##"):
            doc.add_heading(stripped.lstrip("#").strip(), level=1)
        elif stripped.startswith("#"):
            doc.add_heading(stripped.lstrip("#").strip(), level=1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            doc.add_paragraph(stripped[2:].strip(), style="List Bullet")
        else:
            doc.add_paragraph(stripped)

    fd, path = tempfile.mkstemp(suffix=".docx", prefix="atlasmind_notes_")
    os.close(fd)
    doc.save(path)
    return path
