import warnings
warnings.filterwarnings('ignore')

from ui import create_ui


def main():
    
    print("\n" + "="*60)
    print("AtlasMind - AI Learning Companion")
    print("="*60)
    
    demo = create_ui()
    demo.launch()


if __name__ == "__main__":
    main()
