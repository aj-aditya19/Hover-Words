# Hover Dictionary

A background tool that watches your cursor, reads whatever text is on
screen near it (via OCR), and pops up a definition when you pause over
a word — works over *any* app: PDFs, e-books, images of text, etc.

## How it works

1. A mouse listener tracks your cursor position in the background.
2. When you stop moving the mouse for ~0.6s, it grabs a small
   screenshot centered on your cursor.
3. Tesseract OCR reads the text in that region and returns each
   word's position.
4. It finds the word closest to your cursor, skips it if it's too
   short or a very common word (the, and, is...), and otherwise looks
   it up in a **bundled offline dictionary database** — no internet
   connection needed for definitions.
5. A small popup near your cursor shows the word, part of speech,
   and definition, with a 🔊 speaker button to hear the word spoken
   aloud (offline text-to-speech). The popup has **no fixed timer** —
   it stays open as long as you want and only closes once you actually
   move the mouse away from it.

## Setup (Windows)

**1. Install Python 3.10+** if you don't have it: https://www.python.org/downloads/

**2. Install Tesseract OCR** (the actual OCR engine — `pytesseract` is
just a wrapper around it):
- Download the Windows installer from:
  https://github.com/UB-Mannheim/tesseract/wiki
- Install it (default path is usually
  `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- If it's not automatically on your PATH, open `config.py` and set:
  ```python
  TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

**3. Install Python dependencies:**
```bash
cd hover-dictionary
pip install -r requirements.txt
```

**4. Run it:**
```bash
python main.py
```

Now hover your mouse over a word anywhere on screen and hold still
for a moment — a definition popup should appear near your cursor.
Press `Ctrl+C` in the terminal (or close it) to stop.

## Tuning it

Open `config.py`:
- `HOVER_DELAY` — how long the mouse must stay still before it triggers (seconds).
- `CAPTURE_WIDTH` / `CAPTURE_HEIGHT` — size of the screen region grabbed around the cursor. Bigger = more context but slower OCR.
- `MIN_WORD_LENGTH` — ignores words shorter than this.
- `HIDE_MOVE_THRESHOLD` — how many pixels the cursor must move away from the popup before it closes. Lower = closes sooner on small movements; higher = more forgiving of small hand jitter.

You can also edit `common_words.py` to add/remove words you never
want it to bother looking up.

## Offline dictionary

This app needs no internet access to look up words. It bundles
`offline_dictionary.db` — a SQLite database built from **Wiktionary**
data via the [open-dictionary](https://github.com/mhollingshead/open-dictionary)
project. It covers **~263,000 English words**, including modern
vocabulary, part of speech, and example sentences — not just archaic
terms.

**Only Tesseract OCR and TTS need to work locally** (both already do)
— nothing in this app calls the internet anymore.

**Known limitation:** very recent slang/brand-new coinages (e.g.
internet-era words that Wiktionary hasn't documented) may still be
missing, but coverage of genuinely "hard"/uncommon vocabulary —
academic, literary, scientific — is very strong.

**If you ever want to rebuild the database:**
```bash
curl -L -o open-dict.zip https://codeload.github.com/mhollingshead/open-dictionary/zip/refs/heads/main
unzip open-dict.zip
python build_offline_dictionary.py open-dictionary-main/api
```
This regenerates `offline_dictionary.db` (~39 MB) in the project folder.

## Tray icon

Once running, look for a small icon in the Windows system tray (bottom
right, may be under the "^" hidden icons arrow). Right-click it for:
- **Pause / Resume** — temporarily stop lookups without closing the app.
- **Quit** — closes it fully.

Logs (including any OCR/API errors) are written to:
```
%LOCALAPPDATA%\HoverDictionary\hover-dictionary.log
```
Check this file if something isn't working and you don't see a console.

## Building a distributable installer (so anyone can just install it)

This turns the project into a normal Windows `setup.exe` — no Python,
no separate Tesseract install, no terminal required for the end user.

**Step 1 — Get a portable Tesseract build.**
The regular Tesseract installer doesn't give you a clean redistributable
folder, so grab a portable/standalone build instead, for example the
zipped builds here: https://github.com/UB-Mannheim/tesseract/wiki
(or install normally once, then copy the entire
`C:\Program Files\Tesseract-OCR` folder — it's self-contained).

Place it in the project so it looks like:
```
hover-dictionary/
  vendor/
    tesseract/
      tesseract.exe
      tessdata/
        eng.traineddata
        ... (other files from the Tesseract folder)
```
`config.py` automatically detects and uses this bundled copy — end
users won't need to install Tesseract themselves.

**Step 2 — Build the standalone .exe.**
```bash
pip install -r requirements.txt
build.bat
```
This runs PyInstaller and produces `dist\HoverDictionary.exe` — a
single file with Python, all dependencies, and the offline dictionary
database baked in. Make sure `offline_dictionary.db` exists in the
project folder before running this (see "Offline dictionary" section
above if it's missing).

**Step 3 — Build the installer.**
- Install Inno Setup (free): https://jrsoftware.org/isdl.php
- Open `installer.iss` in the Inno Setup Compiler and click **Compile**
  (or run `iscc installer.iss` from the command line).
- This produces `installer_output\HoverDictionary-Setup.exe`.

**That final `HoverDictionary-Setup.exe` is what you share.** Anyone
who runs it gets: the app installed, a Start Menu entry, an uninstaller,
and (if they leave the checkbox ticked) it launches automatically every
time they log into Windows — no Python, no manual Tesseract setup, no
terminal.

**Notes:**
- The installer doesn't require admin rights (installs to the user's
  own folder), which also means no Windows "unknown publisher" admin
  prompt — though you may still see a SmartScreen warning ("Windows
  protected your PC") the first time someone runs an unsigned exe. This
  is expected for apps without a paid code-signing certificate; users
  can click "More info" -> "Run anyway."
- Every time you change the code, repeat steps 2 and 3 to produce a new
  installer.

## Known limitations / things to improve next

- **OCR accuracy** varies with font, size, and anti-aliasing —
  small or stylized text (some e-readers, some PDF renderers) may OCR
  poorly. You may need to tune `CAPTURE_WIDTH/HEIGHT` or add image
  pre-processing (contrast/threshold) in `ocr_engine.py` for tricky
  apps.
- **"Hard word" detection is currently just "not in a common-word
  list."** If you want it smarter, consider swapping `common_words.py`
  for the `wordfreq` package (frequency-based) so obscure words are
  detected more precisely regardless of length.
- **No system tray icon yet** — right now you start/stop it from a
  terminal. Adding a tray icon (e.g. with `pystray`) would make it
  feel more like a real background app.
- **Performance**: OCR runs on every hover, which is fine for casual
  reading but can lag on rapid mouse movement. The debounce (`fired`
  flag) already prevents repeat lookups on the same spot.
- **Multi-monitor / DPI scaling**: `mss` handles multiple monitors,
  but if you have unusual display scaling (125%/150%) and see
  offset/misaligned lookups, that's the usual culprit — you may need
  to adjust cursor coordinate scaling.
