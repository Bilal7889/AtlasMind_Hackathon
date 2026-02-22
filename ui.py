"""
AtlasMind – Modern Premium UI Implementation
"""

import gradio as gr
from rag import process_video, process_pdf, answer_question, generate_notes
from quiz import start_quiz, check_answer, next_question
from config import APP_TITLE, APP_DESCRIPTION
from models import set_active_source, video_state, pdf_state

# Enhanced CSS for a refined, professional look
CUSTOM_CSS = """
/* Global Styles */
.gradio-container {
    min-width: 1000px !important;
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
    max-width: 1000px;
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

.card-wrapper h1, .card-wrapper h2, .card-wrapper h3,
.card-wrapper h4, .card-wrapper h5, .card-wrapper h6 {
    color: #ffffff !important;
    font-weight: 600 !important;
}

.card-wrapper p {
    color: #e4e7eb !important;
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

/* Make ALL tabs visible and prominent (including Analysis Engine tabs) */
button[role="tab"] {
    color: #e4e7eb !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    padding: 12px 20px !important;
    opacity: 0.8 !important;
    transition: all 0.2s ease !important;
}

button[role="tab"]:hover {
    color: #ffffff !important;
    opacity: 1 !important;
    background-color: transparent !important;
}

button[role="tab"][aria-selected="true"] {
    color: #ffffff !important;
    opacity: 1 !important;
    border-bottom: 3px solid #a855f7 !important;
    background-color: transparent !important;
}

/* Make tabs MORE visible and prominent */
.tabs-container button {
    color: #e4e7eb !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    padding: 12px 20px !important;
    opacity: 0.8 !important;
    transition: all 0.2s ease !important;
}

.tabs-container button:hover {
    color: #ffffff !important;
    opacity: 1 !important;
    background-color: transparent !important;
}

.tabs-container button.selected {
    border-bottom: 2px solid #a855f7 !important;
    color: #fff !important;
    background: transparent !important;
    opacity: 1 !important;
}

/* Input Fields */
input, textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 12px !important;
    transition: all 0.2s ease;
    color: #ffffff !important;
}

input:focus, textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2) !important;
}

/* Slider number input - white text, no border */
input[type="number"] {
    background: #0b0e14 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
}

/* Slider component - all text should be visible on dark background */
.gr-slider span {
    color: #e4e7eb !important;
    font-weight: 500 !important;
}

/* Slider reset/undo button - make it visible */
.gr-slider button,
.gr-slider .icon-button,
input[type="number"] ~ button {
    background: #30363d !important;
    color: #e4e7eb !important;
    border: 1px solid #484f58 !important;
}

.gr-slider button:hover,
.gr-slider .icon-button:hover,
input[type="number"] ~ button:hover {
    background: #3d444d !important;
    color: #ffffff !important;
    border-color: #a855f7 !important;
}

/* Radio button options - Make text visible with dark text */
label[data-testid="block-label"] span {
    color: #ffffff !important; /* Keep "Select your answer" white */
}

/* Radio options text - DARK for visibility on light background */
.gr-radio label > span,
fieldset label span,
input[type="radio"] ~ span,
.gr-radio .wrap span {
    color: #0b0e14 !important;
    font-weight: 500 !important;
}

/* Radio button container - light background */
fieldset {
    background: #f8fafc !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

/* All text within radio group */
.gr-radio, .gr-radio * {
    color: #0b0e14 !important;
}

/* Radio button styling - make selected one VERY visible */
input[type="radio"] {
    width: 18px !important;
    height: 18px !important;
    accent-color: #a855f7 !important; /* Purple when checked */
    cursor: pointer !important;
}

/* When radio is checked - highlight the entire option */
input[type="radio"]:checked + label,
input[type="radio"]:checked ~ span {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(34, 211, 238, 0.15)) !important;
    border-left: 4px solid #a855f7 !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin-left: -8px !important;
    font-weight: 600 !important;
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

/* All buttons should be visible */
button {
    color: #ffffff !important;
}

/* Secondary button styling - for non-primary buttons */
.gr-button:not([variant="primary"]) {
    color: #e4e7eb !important;
    background: #1c2128 !important;
    border: 1px solid #373e47 !important;
    font-weight: 500 !important;
}

.gr-button:not([variant="primary"]):hover {
    background: #262d36 !important;
    border-color: #484f58 !important;
}

/* Footer */
.footer-text {
    text-align: center;
    color: #484f58;
    margin-top: 60px;
    padding-bottom: 30px;
    font-size: 0.9rem;
}

/* Loading Spinner */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(168, 85, 247, 0.3);
    border-radius: 50%;
    border-top-color: #a855f7;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.processing-overlay {
    background: rgba(11, 14, 20, 0.8);
    backdrop-filter: blur(5px);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.status-message {
    color: #8b949e;
    margin-top: 10px;
    font-size: 0.95rem;
}

/* Markdown Output Styling */
.markdown-text {
    color: #f0f6fc !important;
}

.markdown-text h1, .markdown-text h2, .markdown-text h3, 
.markdown-text h4, .markdown-text h5, .markdown-text h6 {
    color: #ffffff !important;
    font-weight: 600 !important;
    margin-top: 1.2em !important;
    margin-bottom: 0.6em !important;
}

/* Quiz question numbers and feedback - extra prominent */
.markdown-text h2 {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.4rem !important;
}

/* All Gradio Markdown headings should be white */
label, .label {
    color: #ffffff !important;
}

/* Ensure all headings are white and VISIBLE */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 600 !important;
}

.markdown-text strong {
    color: #ffffff !important;
}

.markdown-text p {
    color: #e4e7eb !important;
    line-height: 1.6 !important;
}

/* List items MUST be visible - light color */
.markdown-text ul, .markdown-text ol {
    color: #e4e7eb !important;
    padding-left: 20px !important;
    margin-left: 0 !important;
}

.markdown-text li {
    color: #e4e7eb !important;
    margin-bottom: 0.5em !important;
    margin-left: 0 !important;
    padding-left: 8px !important;
    line-height: 1.6 !important;
}

.markdown-text li:hover {
    background-color: transparent !important;
}

.markdown-text ul li::marker,
.markdown-text ol li::marker {
    color: #a855f7 !important;
}

.markdown-text code {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #22d3ee !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}

/* Card wrapper - ensure nested markdown is visible */
.card-wrapper .markdown-text h3 {
    color: #ffffff !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
}

/* Active content indicator - make PDF/video names MORE visible */
.active-content-indicator em {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-style: normal !important;
    opacity: 1 !important;
}

.active-content-indicator strong {
    color: #ffffff !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/* Prevent hover effects from making text invisible */
.markdown-text *:hover {
    background-color: transparent !important;
}
"""

# Helper function for PDF download
def save_notes_as_pdf(notes_content):
    """Save notes as PDF file"""
    import tempfile
    import os
    import re
    from datetime import datetime
    from models import get_active_state
    from fpdf import FPDF
    
    if not notes_content or notes_content.strip() == "":
        return None
    
    # Clean content - remove emojis and non-Latin-1 characters
    def clean_text(text):
        """Remove emojis and special Unicode characters"""
        # Remove emojis and other non-Latin-1 characters
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        
        # Replace common symbols
        text = text.replace('✓', 'v')
        text = text.replace('✗', 'x')
        text = text.replace('→', '->')
        text = text.replace('←', '<-')
        text = text.replace('•', '*')
        text = text.replace('…', '...')
        
        # Keep only Latin-1 compatible characters
        return ''.join(char if ord(char) < 256 else '?' for char in text)
    
    active_state = get_active_state()
    source_name = active_state.video_id if active_state.is_loaded() else "notes"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"AtlasMind_Notes_{source_name}_{timestamp}.pdf"
    
    # Create temp file
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    # Clean the content
    clean_content = clean_text(notes_content)
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "AtlasMind Study Notes", ln=True, align='C')
    pdf.ln(10)
    
    # Add content (convert markdown to plain text for PDF)
    pdf.set_font("Arial", '', 11)
    
    # Simple markdown to PDF conversion
    lines = clean_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        
        try:
            # Handle headers
            if line.startswith('###'):
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 6, line.replace('###', '').strip())
                pdf.set_font("Arial", '', 11)
            elif line.startswith('##'):
                pdf.set_font("Arial", 'B', 13)
                pdf.multi_cell(0, 7, line.replace('##', '').strip())
                pdf.set_font("Arial", '', 11)
            elif line.startswith('#'):
                pdf.set_font("Arial", 'B', 14)
                pdf.multi_cell(0, 8, line.replace('#', '').strip())
                pdf.set_font("Arial", '', 11)
            # Handle bullet points
            elif line.startswith('-') or line.startswith('*'):
                # Check if bullet line has bold text
                if '**' in line:
                    # Handle bold within bullet (simple approach: just remove **)
                    clean_line = line.replace('**', '')
                    pdf.multi_cell(0, 6, '  * ' + clean_line[1:].strip())
                else:
                    pdf.multi_cell(0, 6, '  * ' + line[1:].strip())
            # Handle lines with bold text (but not as headings)
            elif '**' in line:
                # Simple approach: just remove ** markers and keep text normal
                # This prevents entire lines from becoming bold
                clean_line = line.replace('**', '')
                pdf.multi_cell(0, 6, clean_line)
            else:
                pdf.multi_cell(0, 6, line)
        except Exception as e:
            # Skip problematic lines
            print(f"Skipping line due to error: {e}")
            continue
    
    pdf.output(filepath)
    return filepath

def create_ui():
    # Use the Glassmorphism approach for the overall theme
    demo = gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Default())

    with demo:
        # State to track active source
        active_source = gr.State(value=None)  # Will be "video" or "pdf"
        active_source_name = gr.State(value="None")  # Video title or PDF filename
        
        # 1. Header Section
        with gr.Column(elem_classes="header-container"):
            gr.HTML(f"<h1>{APP_TITLE}</h1>")
            gr.HTML(f"<p>{APP_DESCRIPTION}</p>")

        # 2. Hero Action (Video/PDF Input)
        with gr.Column(elem_classes="card-wrapper"):
            gr.Markdown("### **Analysis Engine**", elem_classes="markdown-text")
            
            with gr.Tabs() as analysis_tabs:
                # YouTube Tab
                with gr.Tab("📹 YouTube Video", id=0) as video_tab:
                    with gr.Row(variant="compact"):
                        video_input = gr.Textbox(
                            placeholder="Enter YouTube lecture URL to begin...",
                            scale=4,
                            show_label=False,
                            container=False
                        )
                        process_btn = gr.Button("Process Video", variant="primary", elem_classes="primary-btn", scale=1)
                    
                    video_status = gr.Markdown(label="Video Processing Status", elem_classes="markdown-text")
                
                # PDF Tab
                with gr.Tab("📄 PDF Document", id=1) as pdf_tab:
                    with gr.Row(variant="compact"):
                        pdf_input = gr.File(
                            label="Upload PDF",
                            file_types=[".pdf"],
                            type="filepath",
                            scale=4
                        )
                        process_pdf_btn = gr.Button("Process PDF", variant="primary", elem_classes="primary-btn", scale=1)
                    
                    pdf_status = gr.Markdown(label="PDF Processing Status", elem_classes="markdown-text")

        # Active Source Indicator (Positioned after Analysis Engine)
        with gr.Column(elem_classes="card-wrapper"):
            active_indicator = gr.Markdown(
                "### 🎯 **Active Content:** *None processed yet*",
                elem_classes="markdown-text active-content-indicator"
            )

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
                    answer_output = gr.Markdown(label="Response", elem_classes="markdown-text")

            # --- NOTES TAB ---
            with gr.Tab("Study Notes", id="notes_tab"):
                with gr.Column(elem_classes="card-wrapper"):
                    gr.Markdown("### **AI-Structured Summary**", elem_classes="markdown-text")
                    notes_btn = gr.Button("Generate Study Guide", variant="primary", elem_classes="primary-btn")
                    notes_output = gr.Markdown(elem_classes="markdown-text")
                    
                    download_pdf_btn = gr.DownloadButton("📥 Export Notes to PDF", visible=False, variant="primary", elem_classes="primary-btn")

            # --- QUIZ TAB ---
            with gr.Tab("Assessment", id="quiz_tab"):
                with gr.Column(elem_classes="card-wrapper"):
                    num_questions = gr.Slider(
                        minimum=5, maximum=15, value=5, step=1,
                        label="Target Question Count"
                    )
                    start_quiz_btn = gr.Button("Initialize Quiz", variant="primary", elem_classes="primary-btn")

                    with gr.Column(visible=True) as quiz_area:
                        quiz_question = gr.Markdown(elem_classes="markdown-text")
                        quiz_options = gr.Radio(choices=[], visible=False, label="Select your answer:")
                        
                        with gr.Row():
                            submit_btn = gr.Button("Check Answer", visible=False, variant="primary", elem_classes="primary-btn")
                            next_btn = gr.Button("Next Question", visible=False, variant="primary", elem_classes="primary-btn")

                        quiz_feedback = gr.Markdown(elem_classes="markdown-text")

        # Footer
        gr.HTML("""
            <div class="footer-text">
                Built with RAG Architecture • Optimized via Groq • Persistence by ChromaDB
            </div>
        """)

        # --- EVENT LISTENERS (Logic maintained) ---
        
        # Helper function to update active source indicator
        def update_active_indicator(source_type, source_name):
            if source_type == "video":
                return f"### 🎯 **Active Content:** 📹 YouTube Video - **{source_name}**"
            elif source_type == "pdf":
                return f"### 🎯 **Active Content:** 📄 PDF Document - **{source_name}**"
            return "### 🎯 **Active Content:** *None processed yet*"
        
        # Tab selection handlers - switches active source when clicking tabs
        def switch_to_video():
            """Switch active source to video"""
            set_active_source("video")
            if video_state.is_loaded():
                return f"### 🎯 **Active Source:** 📹 YouTube Video - **{video_state.video_id}**"
            else:
                return "### 🎯 **Active Source:** 📹 YouTube (not processed yet)"
        
        def switch_to_pdf():
            """Switch active source to PDF"""
            set_active_source("pdf")
            if pdf_state.is_loaded():
                return f"### 🎯 **Active Source:** 📄 PDF Document - **{pdf_state.video_id}**"
            else:
                return "### 🎯 **Active Source:** 📄 PDF (not processed yet)"
        
        # Video processing with active source tracking
        def process_video_wrapper(url):
            result = process_video(url)
            # Extract video ID from result for display
            video_id = "Video"
            if "**Video ID:**" in result:
                try:
                    video_id = result.split("**Video ID:**")[1].split("\n")[0].strip()
                except:
                    video_id = "Video"
            return result, "video", video_id
        
        # Disable button, process video, update indicator, then re-enable
        process_btn.click(
            lambda: gr.update(interactive=False, value="⏳ Processing..."),
            None,
            process_btn,
            queue=False
        ).then(
            fn=process_video_wrapper,
            inputs=video_input,
            outputs=[video_status, active_source, active_source_name],
            api_name="process_video"
        ).then(
            fn=update_active_indicator,
            inputs=[active_source, active_source_name],
            outputs=active_indicator
        ).then(
            lambda: gr.update(interactive=True, value="Process Video"),
            None,
            process_btn
        )
        
        # PDF processing with active source tracking
        def process_pdf_wrapper(pdf_file):
            result = process_pdf(pdf_file)
            # Extract filename from result for display
            filename = "PDF"
            if "**Filename:**" in result:
                try:
                    filename = result.split("**Filename:**")[1].split("\n")[0].strip()
                except:
                    filename = "PDF"
            elif pdf_file:
                import os
                filename = os.path.basename(pdf_file)
            return result, "pdf", filename
        
        # Disable button, process PDF, update indicator, then re-enable
        process_pdf_btn.click(
            lambda: gr.update(interactive=False, value="⏳ Processing..."),
            None,
            process_pdf_btn,
            queue=False
        ).then(
            fn=process_pdf_wrapper,
            inputs=pdf_input,
            outputs=[pdf_status, active_source, active_source_name],
            api_name="process_pdf"
        ).then(
            fn=update_active_indicator,
            inputs=[active_source, active_source_name],
            outputs=active_indicator
        ).then(
            lambda: gr.update(interactive=True, value="Process PDF"),
            None,
            process_pdf_btn
        )

        # Disable button, process Q&A, then re-enable
        ask_btn.click(
            lambda: gr.update(interactive=False, value="🤔 Thinking..."),
            None,
            ask_btn,
            queue=False
        ).then(
            fn=answer_question,
            inputs=question_input,
            outputs=answer_output
        ).then(
            lambda: gr.update(interactive=True, value="Query Transcript"),
            None,
            ask_btn
        )

        # Disable button, generate notes, then re-enable and show download button
        notes_btn.click(
            lambda: [gr.update(interactive=False, value="📝 Generating..."), gr.update(visible=False)],
            None,
            [notes_btn, download_pdf_btn],
            queue=False
        ).then(
            fn=generate_notes,
            inputs=None,
            outputs=notes_output
        ).then(
            lambda notes: [
                gr.update(interactive=True, value="Generate Study Guide"), 
                gr.update(visible=True, value=save_notes_as_pdf(notes) if notes and notes.strip() else None)
            ],
            inputs=notes_output,
            outputs=[notes_btn, download_pdf_btn]
        )

        # Disable button, build quiz, then re-enable
        start_quiz_btn.click(
            lambda: gr.update(interactive=False, value="⚙️ Building Quiz..."),
            None,
            start_quiz_btn,
            queue=False
        ).then(
            fn=start_quiz,
            inputs=[num_questions],
            outputs=[quiz_question, quiz_options, submit_btn, next_btn, quiz_feedback]
        ).then(
            lambda: gr.update(interactive=True, value="Initialize Quiz"),
            None,
            start_quiz_btn
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
        
        # Tab switching - update active source when user switches between YouTube/PDF tabs
        video_tab.select(
            fn=switch_to_video,
            inputs=None,
            outputs=active_indicator
        )
        
        pdf_tab.select(
            fn=switch_to_pdf,
            inputs=None,
            outputs=active_indicator
        )

    return demo