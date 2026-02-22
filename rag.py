"""
RAG (Retrieval Augmented Generation) functions for AtlasMind
"""

from models import video_state, pdf_state, get_active_state, set_active_source
from vector_db import semantic_search, chunk_text
from llm import ask_groq
from config import TRANSCRIPT_PREVIEW_LENGTH
from pdf_processor import extract_text_from_pdf


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
        return "❌ **Error:** Please enter a YouTube URL!"
    
    print("\n" + "="*60)
    print("PROCESSING VIDEO (using yt-dlp)")
    print("="*60)
    
    # Fetch transcript
    status_msg = "🔄 **Step 1/3:** Fetching transcript from YouTube...\n\nThis may take 10-30 seconds depending on video length."
    print(status_msg)
    
    result = fetch_transcript_ytdlp(video_url)
    if not result["success"]:
        return f"❌ **Error:** {result['error']}"
    
    # Store in vector DB
    print("🔄 Step 2/3: Storing in vector database...")
    video_state.transcript = result["transcript"]
    video_state.video_id = result["video_id"]
    video_state.collection = store_in_vector_db(result["video_id"], result["transcript"])
    
    # Set as active source
    set_active_source("video")
    
    # Generate summary
    print("🔄 Step 3/3: Generating AI summary...")
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
    
    print("✅ Summary generated!")
    print("="*60 + "\n")
    
    return f"""✅ **Video Processed Successfully!**

**Video ID:** {result['video_id']}  
**Transcript Length:** {len(result['transcript'])} characters  
**Chunks Stored:** {len(chunk_text(result['transcript']))}

---

{summary}"""


def process_pdf(pdf_file) -> str:
    """
    Process PDF document: Extract text, store in DB, generate summary
    
    Args:
        pdf_file: Gradio file upload object
    
    Returns:
        Summary and processing status
    """
    from vector_db import store_in_vector_db
    
    if not pdf_file:
        return "❌ **Error:** Please upload a PDF file!"
    
    print("\n" + "="*60)
    print("PROCESSING PDF DOCUMENT")
    print("="*60)
    
    # Extract text from PDF
    print("🔄 Step 1/3: Extracting text from PDF...")
    result = extract_text_from_pdf(pdf_file)
    if not result["success"]:
        return f"❌ **Error:** {result['error']}"
    
    # Store in vector DB
    print("🔄 Step 2/3: Storing in vector database...")
    pdf_state.transcript = result["text"]
    pdf_state.video_id = result["pdf_id"]
    pdf_state.collection = store_in_vector_db(result["pdf_id"], result["text"])
    
    # Set as active source
    set_active_source("pdf")
    
    # Generate summary
    print("🔄 Step 3/3: Generating AI summary...")
    prompt = f"""You are AtlasMind, an AI learning companion.

Analyze this document and provide:

## 📝 Summary
A concise 3-4 sentence overview.

## 🔑 Key Concepts
5-7 most important points as bullets.

## 💡 Takeaways
3-5 actionable insights.

Content: {result['text'][:TRANSCRIPT_PREVIEW_LENGTH]}"""
    
    summary = ask_groq(prompt)
    
    print("✅ Summary generated!")
    print("="*60 + "\n")
    
    return f"""✅ **PDF Processed Successfully!**

**Filename:** {result['filename']}  
**Pages:** {result['num_pages']}  
**Text Length:** {len(result['text'])} characters  
**Chunks Stored:** {len(chunk_text(result['text']))}

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
    active_state = get_active_state()
    
    if not active_state.transcript:
        return "Please process a video or PDF first!"
    
    if not question or not question.strip():
        return "Please enter a question!"
    
    print(f"\nQuestion: {question}")
    
    context = semantic_search(question, active_state.collection)
    if not context:
        context = active_state.transcript[:3000]
    
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
    active_state = get_active_state()
    
    if not active_state.transcript:
        return "Please process a video or PDF first!"
    
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

Transcript: {active_state.transcript[:6000]}"""
    
    notes = ask_groq(prompt)
    print("Notes generated!\n")
    return notes
