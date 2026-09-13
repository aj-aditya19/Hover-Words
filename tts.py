import threading

import pyttsx3


def speak(word: str):

    def _run():
        try:
            engine = pyttsx3.init()
            engine.say(word)
            engine.runAndWait()
            engine.stop()
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()
