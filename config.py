import os
import sys

HOVER_DELAY = 0.6          
CAPTURE_WIDTH = 420        
CAPTURE_HEIGHT = 140       
MIN_WORD_LENGTH = 4        
TOOLTIP_PADDING = 20       
MIN_DISPLAY_SECONDS = 4    

SPEECH_RATE = 110


def _bundled_tesseract():
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    candidate = os.path.join(base, "vendor", "tesseract", "tesseract.exe")
    return candidate if os.path.exists(candidate) else None

TESSERACT_CMD = _bundled_tesseract()