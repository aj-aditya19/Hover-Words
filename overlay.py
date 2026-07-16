import tkinter as tk
from typing import Optional

import config


class Tooltip:
    """A small borderless, always-on-top popup shown near the cursor."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.win = None

    def show(self, x: int, y: int, word: str, definition: Optional[dict]):
        self.hide()

        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)      # no title bar / borders
        self.win.attributes("-topmost", True)
        try:
            self.win.attributes("-alpha", 0.96)  # slight transparency, if supported
        except tk.TclError:
            pass
        self.win.configure(bg="#2b2b2b")

        if definition:
            phonetic = f" {definition['phonetic']}" if definition["phonetic"] else ""
            pos = definition["part_of_speech"]
            header = f"{word}{phonetic}"
            body = f"({pos}) {definition['definition']}" if pos else definition["definition"]
            if definition.get("example"):
                body += f"\n\u201c{definition['example']}\u201d"
        else:
            header = word
            body = "No definition found."

        frame = tk.Frame(self.win, bg="#2b2b2b", padx=10, pady=8)
        frame.pack()

        tk.Label(
            frame, text=header, bg="#2b2b2b", fg="#ffffff",
            font=("Segoe UI", 11, "bold"), anchor="w", justify="left",
        ).pack(anchor="w")

        tk.Label(
            frame, text=body, bg="#2b2b2b", fg="#dddddd",
            font=("Segoe UI", 10), wraplength=320, justify="left", anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        self.win.update_idletasks()
        self.win.geometry(f"+{x + 18}+{y + 18}")

        self.root.after(config.TOOLTIP_MS, self.hide)

    def hide(self):
        if self.win is not None:
            try:
                self.win.destroy()
            except tk.TclError:
                pass
            self.win = None
