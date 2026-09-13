import mss
from PIL import Image

import config


def capture_region(center_x: int, center_y: int):
    left = center_x - config.CAPTURE_WIDTH // 2
    top = center_y - config.CAPTURE_HEIGHT // 2

    with mss.mss() as sct:
        region = {
            "left": left,
            "top": top,
            "width": config.CAPTURE_WIDTH,
            "height": config.CAPTURE_HEIGHT,
        }
        shot = sct.grab(region)
        img = Image.frombytes("RGB", shot.size, shot.rgb)

    return img, left, top
