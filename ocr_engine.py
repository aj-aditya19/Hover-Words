import pytesseract
from PIL import Image

import config

if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def get_words_with_boxes(image: Image.Image):
    """
    Runs OCR on the given image and returns a list of dicts:
    {'text', 'left', 'top', 'width', 'height'} -- all coordinates are
    relative to the top-left of `image`.
    """
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    words = []
    n = len(data["text"])

    for i in range(n):
        text = data["text"][i].strip()
        try:
            conf = int(float(data["conf"][i]))
        except (ValueError, TypeError):
            conf = -1

        if text and conf > 30:
            words.append({
                "text": text,
                "left": data["left"][i],
                "top": data["top"][i],
                "width": data["width"][i],
                "height": data["height"][i],
            })

    return words
