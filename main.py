import time
import threading
import tkinter as tk

from pynput import mouse

import config
from screen_capture import capture_region
from ocr_engine import get_words_with_boxes
from dictionary_client import get_definition
from common_words import is_common
from overlay import Tooltip
from tray import TrayApp
from logger import get_logger

log = get_logger()


def find_closest_word(words, offset_x, offset_y, cursor_x, cursor_y):
    """Given OCR word boxes (relative to captured image) and the absolute
    cursor position, find whichever word's center is closest to the cursor."""
    best = None
    best_dist = None

    for w in words:
        center_x = offset_x + w["left"] + w["width"] / 2
        center_y = offset_y + w["top"] + w["height"] / 2
        dist = (center_x - cursor_x) ** 2 + (center_y - cursor_y) ** 2
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best = w

    return best


def hover_worker(root: tk.Tk, tooltip: Tooltip, x: int, y: int):
    """Runs off the main thread: capture -> OCR -> lookup. Schedules the
    actual UI update back onto the main thread via root.after()."""
    try:
        image, offset_x, offset_y = capture_region(x, y)
        words = get_words_with_boxes(image)
        target = find_closest_word(words, offset_x, offset_y, x, y)

        if target is None:
            return

        clean_word = "".join(ch for ch in target["text"] if ch.isalpha())
        if len(clean_word) < config.MIN_WORD_LENGTH or is_common(clean_word):
            return

        definition = get_definition(clean_word)
        root.after(0, tooltip.show, x, y, clean_word, definition)

    except Exception as exc:  # noqa: BLE001 - keep the background loop alive
        log.warning(f"lookup error: {exc}")


def main():
    log.info("Hover Dictionary starting up.")

    root = tk.Tk()
    root.withdraw()  # we never show the root window itself
    tooltip = Tooltip(root)

    state = {"pos": None, "last_move": time.time(), "fired": False}
    lock = threading.Lock()

    def request_quit():
        # Called from the tray icon's own thread; hand off to the main
        # thread since tkinter isn't safe to touch from other threads.
        root.after(0, root.destroy)

    tray = TrayApp(on_quit=request_quit)
    tray.run_detached()

    def on_move(x, y):
        with lock:
            state["pos"] = (x, y)
            state["last_move"] = time.time()
            state["fired"] = False

    listener = mouse.Listener(on_move=on_move)
    listener.daemon = True
    listener.start()

    def poll():
        if tray.is_paused():
            root.after(150, poll)
            return

        with lock:
            pos = state["pos"]
            idle = time.time() - state["last_move"]
            fired = state["fired"]
            if pos and idle >= config.HOVER_DELAY and not fired:
                state["fired"] = True
                x, y = pos
                threading.Thread(
                    target=hover_worker, args=(root, tooltip, x, y), daemon=True
                ).start()
        root.after(100, poll)

    log.info("Hover Dictionary running (tray icon active).")

    root.after(100, poll)
    root.mainloop()

    log.info("Hover Dictionary shut down.")


if __name__ == "__main__":
    main()
