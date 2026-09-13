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


def show_tooltip_and_track(tooltip: Tooltip, state: dict, lock: threading.Lock,
                            x: int, y: int, word: str, definition):
    tooltip.show(x, y, word, definition)
    bbox = tooltip.get_bbox(padding=config.TOOLTIP_PADDING)
    with lock:
        state["tooltip_bbox"] = bbox


def hover_worker(root: tk.Tk, tooltip: Tooltip, state: dict, lock: threading.Lock,
                  x: int, y: int):
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
        root.after(0, show_tooltip_and_track, tooltip, state, lock, x, y, clean_word, definition)

    except Exception as exc:
        log.warning(f"lookup error: {exc}")


def main():
    log.info("Hover Dictionary starting up.")

    root = tk.Tk()
    root.withdraw()
    tooltip = Tooltip(root)

    state = {"pos": None, "last_move": time.time(), "fired": False, "tooltip_bbox": None}
    lock = threading.Lock()

    def request_quit():
        root.after(0, root.destroy)

    tray = TrayApp(on_quit=request_quit)
    tray.run_detached()

    def on_move(x, y):
        with lock:
            state["pos"] = (x, y)
            state["last_move"] = time.time()
            state["fired"] = False
            bbox = state["tooltip_bbox"]

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            if not (x1 <= x <= x2 and y1 <= y <= y2):
                with lock:
                    state["tooltip_bbox"] = None
                root.after(0, tooltip.hide)

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
                    target=hover_worker, args=(root, tooltip, state, lock, x, y), daemon=True
                ).start()
        root.after(100, poll)

    log.info("Hover Dictionary running (tray icon active).")

    root.after(100, poll)
    root.mainloop()

    log.info("Hover Dictionary shut down.")


if __name__ == "__main__":
    main()