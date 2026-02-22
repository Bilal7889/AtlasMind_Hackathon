"""
RAG (Retrieval Augmented Generation) functions for AtlasMind
"""

from models import current_video
from vector_db import semantic_search, chunk_text
from llm import ask_groq
from config import TRANSCRIPT_PREVIEW_LENGTH


def process_video(video_url: str) -> str:
    """
    Main function: Fetch transcript, store in DB, generate summary
    
    Args:
        video_url: YouTube URL
    
    Returns:
        Summary and processing status
    """
    from youtube import fetch_transcript_ytdlp
    from vector_db import store_in_vector_db
    
    if not video_url or not video_url.strip():
        return "Please enter a YouTube URL!"
    
    print("\n" + "="*60)
    print("PROCESSING VIDEO (using yt-dlp)")
    print("="*60)
    
    # Fetch transcript
    result = fetch_transcript_ytdlp(video_url)
    if not result["success"]:
        return result["error"]
    
    # Store in vector DB
    current_video.transcript = result["transcript"]
    current_video.video_id = result["video_id"]
    current_video.collection = store_in_vector_db(result["video_id"], result["transcript"])
    
    # Generate summary
    print("Generating AI summary...")
    prompt = f"""You are AtlasMind, an AI learning companion.

Analyze this lecture and provide:

## 📝 Summary
A concise 3-4 sentence overview.

## 🔑 Key Concepts
5-7 most important points as bullets.

## 💡 Takeaways
3-5 actionable insights.

Transcript: {result['transcript'][:TRANSCRIPT_PREVIEW_LENGTH]}"""
    
    summary = ask_groq(prompt)
    
    print("Summary generated!")
    print("="*60 + "\n")
    
    return f"""**Video Processed Successfully!**

**Video ID:** {result['video_id']}  
**Transcript Length:** {len(result['transcript'])} characters  
**Chunks Stored:** {len(chunk_text(result['transcript']))}

---

{summary}"""


def answer_question(question: str) -> str:
    """
    Answer questions using RAG
    
    Args:
        question: User's question
    
    Returns:
        Answer based on video context
    """
    if not current_video.transcript:
        return "Please process a video first!"
    
    if not question or not question.strip():
        return "Please enter a question!"
    
    print(f"\nQuestion: {question}")
    
    context = semantic_search(question, current_video.collection)
    if not context:
        context = current_video.transcript[:3000]
    
    print(f"Found relevant context ({len(context)} chars)")
    
    prompt = f"""Based on this video lecture, answer the question clearly and concisely.

Question: {question}

Provide a helpful answer."""
    
    print(f"Generating answer...")
    answer = ask_groq(prompt, context)
    print(f"Answer ready!\n")
    
    return answer


def generate_notes() -> str:
    """
    Generate study notes from video
    
    Returns:
        Formatted study notes
    """
    if not current_video.transcript:
        return "Please process a video first!"
    
    print("\nGenerating study notes...")
    
    prompt = f"""Create comprehensive study notes from this lecture.

Format:

## 📚 Main Topics
[List main topics]

## 📖 Key Definitions
[Important terms and definitions]

## 💡 Examples
[Key examples mentioned]

## 🎯 Important Concepts
[Core concepts to remember]

Transcript: {current_video.transcript[:6000]}"""
    
    notes = ask_groq(prompt)
    print("Notes generated!\n")
    return notes
