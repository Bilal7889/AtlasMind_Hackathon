import os
import warnings
warnings.filterwarnings('ignore')

from fastapi import FastAPI
import gradio as gr

from ui import create_ui

# Build Gradio demo and mount on FastAPI so Render/uvicorn can bind to PORT
print("AtlasMind - loading UI...")
demo = create_ui()
demo.queue()

app = FastAPI(title="AtlasMind")


@app.get("/health")
def health():
    return {"status": "ok"}


app = gr.mount_gradio_app(app, demo, path="/")


def main():
    # Local run or when not using uvicorn
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)


if __name__ == "__main__":
    # Use uvicorn so the process binds to PORT immediately (needed for Render)
    port = int(os.environ.get("PORT", 7860))
    import uvicorn
    print(f"Starting on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
