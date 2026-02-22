"""
AtlasMind – entry point. Run with: python app.py
"""
import os
import warnings
warnings.filterwarnings("ignore")

from ui import create_ui

if __name__ == "__main__":
    demo = create_ui()
    demo.queue()
    port = int(os.environ.get("PORT", 7860))
    # Use 0.0.0.0 for deployment (Render/Railway); 127.0.0.1 for local to avoid Gradio localhost error
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    demo.launch(server_name=host, server_port=port, share=False)
