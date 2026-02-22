"""
Groq LLM interface for AtlasMind
"""

from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)


def ask_groq(prompt: str, context: str = "") -> str:
    """
    Query Groq LLM with optional context
    
    Args:
        prompt: Main prompt/question
        context: Optional context for RAG
    
    Returns:
        LLM response
    """
    try:
        full_prompt = f"{prompt}\n\nContext: {context}" if context else prompt
        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Groq Error: {str(e)}"
