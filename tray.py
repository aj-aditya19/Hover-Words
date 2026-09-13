import threading

from PIL import Image, ImageDraw
import pystray


def _make_icon_image(paused: bool) -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    color = "#888888" if paused else "#2b6cb0"
    draw.ellipse((4, 4, size - 4, size - 4), fill=color)
    draw.text((22, 16), "D", fill="white")

    return img


class TrayApp:

    def __init__(self, on_quit):
        self.paused = False
        self._on_quit_callback = on_quit
        self._lock = threading.Lock()

        self.icon = pystray.Icon(
            "hover_dictionary",
            _make_icon_image(False),
            "Hover Dictionary",
            menu=pystray.Menu(
                pystray.MenuItem(self._pause_label, self._toggle_pause),
                pystray.MenuItem("Quit", self._quit),
            ),
        )

    def _pause_label(self, item):
        return "Resume" if self.paused else "Pause"

    def _toggle_pause(self, icon, item):
        with self._lock:
            self.paused = not self.paused
        icon.icon = _make_icon_image(self.paused)
        icon.update_menu()

    def _quit(self, icon, item):
        icon.stop()
        self._on_quit_callback()

    def is_paused(self) -> bool:
        with self._lock:
            return self.paused

    def run_detached(self):
        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()
        return thread
