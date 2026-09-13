import tkinter as tk
from typing import Optional

from tts import speak


class Tooltip:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.win = None
        self._origin = None

    def show(self, x: int, y: int, word: str, definition: Optional[dict]):
        self.hide()
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        try:
            self.win.attributes("-alpha", 0.96)
        except tk.TclError:
            pass
        self.win.configure(bg="#2b2b2b")

        if definition:
            header_text = word
            body = definition["definition"]
        else:
            header_text = word
            body = "No definition found."

        frame = tk.Frame(self.win, bg="#2b2b2b", padx=10, pady=8)
        frame.pack()
        header_row = tk.Frame(frame, bg="#2b2b2b")
        header_row.pack(anchor="w", fill="x")
        tk.Label(
            header_row, text=header_text, bg="#2b2b2b", fg="#ffffff",
            font=("Segoe UI", 11, "bold"), anchor="w", justify="left",
        ).pack(side="left")

        speak_btn = tk.Button(
            header_row, text="\U0001F50A", bg="#2b2b2b", fg="#ffffff",
            activebackground="#3f3f3f", activeforeground="#ffffff",
            relief="flat", bd=0, font=("Segoe UI", 11),
            cursor="hand2", command=lambda: speak(word),
        )
        speak_btn.pack(side="left", padx=(8, 0))

        tk.Label(
            frame, text=body, bg="#2b2b2b", fg="#dddddd",
            font=("Segoe UI", 10), wraplength=320, justify="left", anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        offset_x, offset_y = x + 18, y + 18
        self.win.geometry(f"+{offset_x}+{offset_y}")
        self.win.update_idletasks()
        self.win.update()
        self._origin = (offset_x, offset_y)

    def get_bbox(self, padding: int = 0):
        if self.win is None or self._origin is None:
            return None
        try:
            w = self.win.winfo_width()
            h = self.win.winfo_height()
        except tk.TclError:
            return None

        x1, y1 = self._origin
        return (x1 - padding, y1 - padding, x1 + w + padding, y1 + h + padding)

    def hide(self):
        if self.win is not None:
            try:
                self.win.destroy()
            except tk.TclError:
                pass
            self.win = None
        self._origin = None