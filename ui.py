"""
AtlasMind – Modern Premium UI Implementation
"""

import gradio as gr
from rag import process_video, answer_question, generate_notes
from quiz import start_quiz, check_answer, next_question
from config import APP_TITLE, APP_DESCRIPTION

# Enhanced CSS for a refined, professional look
CUSTOM_CSS = """
/* Global Styles */
.gradio-container {
    max-width: 1000px !important;
    margin: auto !important;
    padding-top: 40px !important;
}

/* Typography & Theme */
body, .gradio-container {
    background-color: #0b0e14 !important;
    color: #f0f6fc !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* Header Section */
.header-container {
    text-align: center;
    margin-bottom: 40px;
    padding: 20px;
}

.header-container h1 {
    font-size: 3.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #fff 30%, #a855f7 70%, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px !important;
}

.header-container p {
    font-size: 1.1rem !important;
    color: #8b949e !important;
    max-width: 600px;
    margin: 0 auto !important;
}

/* Glassmorphism Cards */
.card-wrapper {
    background: rgba(23, 28, 36, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
    margin-bottom: 24px !important;
}

/* Tabs Styling */
.tabs-container {
    border: none !important;
    background: transparent !important;
}

.tabs-container .tab-nav {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    margin-bottom: 20px !important;
    gap: 12px !important;
}

.tabs-container button.selected {
    border-bottom: 2px solid #a855f7 !important;
    color: #fff !important;
    background: transparent !important;
}

/* Input Fields */
input, textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 12px !important;
    transition: all 0.2s ease;
}

input:focus, textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2) !important;
}

/* Buttons */
.primary-btn {
    background: linear-gradient(135deg, #9333ea, #0891b2) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    transition: transform 0.15s ease !important;
}

.primary-btn:hover {
    transform: translateY(-1px);
    filter: brightness(1.1);
}

/* Footer */
.footer-text {
    text-align: center;
    color: #484f58;
    margin-top: 60px;
    padding-bottom: 30px;
    font-size: 0.9rem;
}
"""

def create_ui():
    # Use the Glassmorphism approach for the overall theme
    demo = gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Default())

    with demo:
        # 1. Header Section
        with gr.Column(elem_classes="header-container"):
            gr.HTML(f"<h1>{APP_TITLE}</h1>")
            gr.HTML(f"<p>{APP_DESCRIPTION}</p>")

        # 2. Hero Action (Video URL Input)
        with gr.Column(elem_classes="card-wrapper"):
            gr.Markdown("### **Analysis Engine**")
            with gr.Row(variant="compact"):
                video_input = gr.Textbox(
                    placeholder="Enter YouTube lecture URL to begin...",
                    scale=4,
                    show_label=False,
                    container=False
                )
                process_btn = gr.Button("Process Video", variant="primary", elem_classes="primary-btn", scale=1)
            
            summary_output = gr.Markdown(label="Processing Status")

        # 3. Features Tab Section
        with gr.Tabs(elem_classes="tabs-container") as tabs:
            
            # --- Q&A TAB ---
            with gr.Tab("Knowledge Base", id="qa_tab"):
                with gr.Column(elem_classes="card-wrapper"):
                    question_input = gr.Textbox(
                        placeholder="What specific part of the lecture should I explain?",
                        lines=2,
                        label="Ask the AI Assistant"
                    )
                    ask_btn = gr.Button("Query Transcript", variant="primary", elem_classes="primary-btn")
                    answer_output = gr.Markdown(label="Response")

            # --- NOTES TAB ---
            with gr.Tab("Study Notes", id="notes_tab"):
                with gr.Column(elem_classes="card-wrapper"):
                    gr.Markdown("### **AI-Structured Summary**")
                    notes_btn = gr.Button("Generate Study Guide", variant="primary", elem_classes="primary-btn")
                    notes_output = gr.Markdown()

            # --- QUIZ TAB ---
            with gr.Tab("Assessment", id="quiz_tab"):
                with gr.Column(elem_classes="card-wrapper"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            num_questions = gr.Slider(
                                minimum=5, maximum=15, value=5, step=1,
                                label="Target Question Count"
                            )
                        with gr.Column(scale=1):
                            start_quiz_btn = gr.Button("Initialize Quiz", variant="primary", elem_classes="primary-btn")

                    with gr.Column(visible=True) as quiz_area:
                        quiz_question = gr.Markdown()
                        quiz_options = gr.Radio(choices=[], visible=False, label="Select your answer:")
                        
                        with gr.Row():
                            submit_btn = gr.Button("Check Answer", visible=False)
                            next_btn = gr.Button("Next Question", visible=False, variant="primary", elem_classes="primary-btn")

                        quiz_feedback = gr.Markdown()

        # Footer
        gr.HTML("""
            <div class="footer-text">
                Built with RAG Architecture • Optimized via Groq • Persistence by ChromaDB
            </div>
        """)

        # --- EVENT LISTENERS (Logic maintained) ---
        process_btn.click(
            fn=process_video,
            inputs=video_input,
            outputs=summary_output
        )

        ask_btn.click(
            fn=answer_question,
            inputs=question_input,
            outputs=answer_output
        )

        notes_btn.click(
            fn=generate_notes,
            inputs=None,
            outputs=notes_output
        )

        start_quiz_btn.click(
            fn=start_quiz,
            inputs=[num_questions],
            outputs=[quiz_question, quiz_options, submit_btn, next_btn, quiz_feedback]
        )

        submit_btn.click(
            fn=check_answer,
            inputs=[quiz_options],
            outputs=[quiz_question, quiz_options, submit_btn, next_btn, quiz_feedback]
        )

        next_btn.click(
            fn=next_question,
            inputs=None,
            outputs=[quiz_question, quiz_options, submit_btn, next_btn, quiz_feedback]
        )

    return demo