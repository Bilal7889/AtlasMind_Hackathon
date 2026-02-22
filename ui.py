"""
AtlasMind – Tab-based UI: Video and PDF each have their own session, summary, notes, and quiz.
"""

import gradio as gr
from rag import process_video, process_pdf, answer_question, generate_notes
from quiz import start_quiz, check_answer, next_question
from config import APP_TITLE, APP_DESCRIPTION

CUSTOM_CSS = """
.gradio-container { max-width: 1000px !important; margin: auto !important; padding-top: 40px !important; }
body, .gradio-container { background-color: #0b0e14 !important; color: #f0f6fc !important; font-family: 'Inter', -apple-system, sans-serif !important; }
.header-container { text-align: center; margin-bottom: 40px; padding: 20px; }
.header-container h1 { font-size: 3.2rem !important; font-weight: 800 !important; letter-spacing: -0.02em; background: linear-gradient(135deg, #fff 30%, #a855f7 70%, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px !important; }
.header-container p { font-size: 1.1rem !important; color: #8b949e !important; max-width: 600px; margin: 0 auto !important; }
.card-wrapper { background: rgba(23, 28, 36, 0.7) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 16px !important; padding: 24px !important; margin-bottom: 24px !important; }
.tabs-container { border: none !important; background: transparent !important; }
.tabs-container .tab-nav { border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important; margin-bottom: 20px !important; gap: 12px !important; }
.tabs-container button.selected { border-bottom: 2px solid #a855f7 !important; color: #fff !important; background: transparent !important; }
input, textarea { background: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px !important; padding: 12px !important; }
input:focus, textarea:focus { border-color: #a855f7 !important; box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2) !important; }
.primary-btn { background: linear-gradient(135deg, #9333ea, #0891b2) !important; border: none !important; color: white !important; font-weight: 600 !important; border-radius: 10px !important; padding: 10px 24px !important; transition: transform 0.15s ease !important; }
.primary-btn:hover { transform: translateY(-1px); filter: brightness(1.1); }
.primary-btn:disabled { opacity: 0.75 !important; cursor: wait !important; }
.footer-text { text-align: center; color: #484f58; margin-top: 60px; padding-bottom: 30px; font-size: 0.9rem; }
"""


def _notes_with_download(source: str):
    notes, path = generate_notes(source)
    if path:
        return notes, gr.update(value=path, visible=True)
    return notes, gr.update(visible=False)


def create_ui():
    demo = gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Default())

    with demo:
        with gr.Column(elem_classes="header-container"):
            gr.HTML(f"<h1>{APP_TITLE}</h1>")
            gr.HTML(f"<p>{APP_DESCRIPTION}</p>")

        # Top-level tabs: Video | PDF (each tab = one content type, its own session)
        with gr.Tabs(elem_classes="tabs-container") as main_tabs:
            # ---------- VIDEO TAB ----------
            with gr.Tab("Video", id="video_tab"):
                with gr.Column(elem_classes="card-wrapper"):
                    gr.Markdown("### **YouTube Video**")
                    video_input = gr.Textbox(placeholder="Enter YouTube lecture URL...", show_label=False, container=False)
                    video_process_btn = gr.Button("Process Video", variant="primary", elem_classes="primary-btn")
                    video_summary = gr.Markdown(label="Summary")

                with gr.Tabs():
                    with gr.Tab("Knowledge Base"):
                        with gr.Column(elem_classes="card-wrapper"):
                            video_question = gr.Textbox(placeholder="Ask about this video...", lines=2, label="Question")
                            video_ask_btn = gr.Button("Ask", variant="primary", elem_classes="primary-btn")
                            video_answer = gr.Markdown(label="Answer")
                    with gr.Tab("Study Notes"):
                        with gr.Column(elem_classes="card-wrapper"):
                            video_notes_btn = gr.Button("Generate Notes", variant="primary", elem_classes="primary-btn")
                            video_notes = gr.Markdown()
                            video_notes_download = gr.DownloadButton("Download Notes", visible=False)
                    with gr.Tab("Assessment"):
                        with gr.Column(elem_classes="card-wrapper"):
                            video_num_q = gr.Slider(5, 15, value=5, step=1, label="Number of questions")
                            video_start_quiz_btn = gr.Button("Start Quiz", variant="primary", elem_classes="primary-btn")
                            video_quiz_question = gr.Markdown()
                            video_quiz_options = gr.Radio(choices=[], visible=False, label="Choose answer")
                            with gr.Row():
                                video_submit_btn = gr.Button("Check Answer", visible=False)
                                video_next_btn = gr.Button("Next", visible=False, variant="primary", elem_classes="primary-btn")
                            video_quiz_feedback = gr.Markdown()

            # ---------- PDF TAB ----------
            with gr.Tab("PDF", id="pdf_tab"):
                with gr.Column(elem_classes="card-wrapper"):
                    gr.Markdown("### **PDF Document**")
                    pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
                    pdf_process_btn = gr.Button("Process PDF", variant="primary", elem_classes="primary-btn")
                    pdf_summary = gr.Markdown(label="Summary")

                with gr.Tabs():
                    with gr.Tab("Knowledge Base"):
                        with gr.Column(elem_classes="card-wrapper"):
                            pdf_question = gr.Textbox(placeholder="Ask about this document...", lines=2, label="Question")
                            pdf_ask_btn = gr.Button("Ask", variant="primary", elem_classes="primary-btn")
                            pdf_answer = gr.Markdown(label="Answer")
                    with gr.Tab("Study Notes"):
                        with gr.Column(elem_classes="card-wrapper"):
                            pdf_notes_btn = gr.Button("Generate Notes", variant="primary", elem_classes="primary-btn")
                            pdf_notes = gr.Markdown()
                            pdf_notes_download = gr.DownloadButton("Download Notes", visible=False)
                    with gr.Tab("Assessment"):
                        with gr.Column(elem_classes="card-wrapper"):
                            pdf_num_q = gr.Slider(5, 15, value=5, step=1, label="Number of questions")
                            pdf_start_quiz_btn = gr.Button("Start Quiz", variant="primary", elem_classes="primary-btn")
                            pdf_quiz_question = gr.Markdown()
                            pdf_quiz_options = gr.Radio(choices=[], visible=False, label="Choose answer")
                            with gr.Row():
                                pdf_submit_btn = gr.Button("Check Answer", visible=False)
                                pdf_next_btn = gr.Button("Next", visible=False, variant="primary", elem_classes="primary-btn")
                            pdf_quiz_feedback = gr.Markdown()

        gr.HTML('<div class="footer-text">RAG • Groq • ChromaDB</div>')

        # ---- Video tab events (source="video") ----
        video_process_btn.click(process_video, inputs=[video_input], outputs=video_summary)
        video_ask_btn.click(lambda q: answer_question(q, "video"), inputs=[video_question], outputs=video_answer)
        video_notes_btn.click(lambda: _notes_with_download("video"), inputs=None, outputs=[video_notes, video_notes_download])
        video_start_quiz_btn.click(
            lambda n: start_quiz(n, "video"),
            inputs=[video_num_q],
            outputs=[video_quiz_question, video_quiz_options, video_submit_btn, video_next_btn, video_quiz_feedback],
        )
        video_submit_btn.click(
            lambda opt: check_answer(opt, "video"),
            inputs=[video_quiz_options],
            outputs=[video_quiz_question, video_quiz_options, video_submit_btn, video_next_btn, video_quiz_feedback],
        )
        video_next_btn.click(
            lambda: next_question("video"),
            inputs=None,
            outputs=[video_quiz_question, video_quiz_options, video_submit_btn, video_next_btn, video_quiz_feedback],
        )

        # ---- PDF tab events (source="pdf") ----
        pdf_process_btn.click(process_pdf, inputs=[pdf_input], outputs=pdf_summary)
        pdf_ask_btn.click(lambda q: answer_question(q, "pdf"), inputs=[pdf_question], outputs=pdf_answer)
        pdf_notes_btn.click(lambda: _notes_with_download("pdf"), inputs=None, outputs=[pdf_notes, pdf_notes_download])
        pdf_start_quiz_btn.click(
            lambda n: start_quiz(n, "pdf"),
            inputs=[pdf_num_q],
            outputs=[pdf_quiz_question, pdf_quiz_options, pdf_submit_btn, pdf_next_btn, pdf_quiz_feedback],
        )
        pdf_submit_btn.click(
            lambda opt: check_answer(opt, "pdf"),
            inputs=[pdf_quiz_options],
            outputs=[pdf_quiz_question, pdf_quiz_options, pdf_submit_btn, pdf_next_btn, pdf_quiz_feedback],
        )
        pdf_next_btn.click(
            lambda: next_question("pdf"),
            inputs=None,
            outputs=[pdf_quiz_question, pdf_quiz_options, pdf_submit_btn, pdf_next_btn, pdf_quiz_feedback],
        )

    return demo
