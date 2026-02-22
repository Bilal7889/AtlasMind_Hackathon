import os
import warnings
warnings.filterwarnings('ignore')

from ui import create_ui


def main():
    print("\n" + "="*60)
    print("AtlasMind - AI Learning Companion")
    print("="*60)

    demo = create_ui()
    demo.queue()
    # PORT and 0.0.0.0 for Railway, Render, Fly.io, etc.
    server_port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=server_port)


if __name__ == "__main__":
    main()
