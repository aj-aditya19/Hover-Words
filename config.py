import os
import sys

# --- Behavior settings ---
HOVER_DELAY = 0.6          # seconds the mouse must stay still before we trigger a lookup
CAPTURE_WIDTH = 420        # width (px) of the screen region grabbed around the cursor
CAPTURE_HEIGHT = 140       # height (px) of the screen region grabbed around the cursor
MIN_WORD_LENGTH = 4        # ignore very short words (a, an, is, to...)
TOOLTIP_MS = 6000          # how long the tooltip stays visible (milliseconds)


def _bundled_tesseract():
    """
    When this app is packaged with PyInstaller and a portable Tesseract
    build is bundled under vendor/tesseract/, this returns its path so
    end users never need to install Tesseract separately.

    Returns None if no bundled copy is found (e.g. running from source
    during development) - in that case pytesseract falls back to
    whatever's on PATH.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running as a PyInstaller-frozen exe: bundled files were
        # extracted next to _MEIPASS.
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    candidate = os.path.join(base, "vendor", "tesseract", "tesseract.exe")
    return candidate if os.path.exists(candidate) else None


# --- Tesseract path (Windows) ---
# Priority: explicit override below > bundled portable copy > system PATH.
# If you installed Tesseract yourself and it's not on PATH, set it here, e.g.:
# TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CMD = _bundled_tesseract()
