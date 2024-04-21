import re

import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
import numpy as np


def add_caption(imgs: list[PIL.Image.Image], text: str, relative_font_size: float = 1) -> list[PIL.Image.Image]:
    text = text.replace(r"\\", "\0")
    m = re.fullmatch(r"(.+?)(?<!\\)(?:,(.+))?", text)
    if (m == None):
        texts = [text, ""]
    else:
        texts = [m[1], m[2] or ""]
    for i in range(2):
        texts[i] = texts[i].replace(r"\,", ",")
        texts[i] = texts[i].replace("\0", "\\")

    for img in imgs:
        font_size = int(img.width / 15 * relative_font_size)
        font = PIL.ImageFont.truetype("impact.ttf", font_size)
        stroke_width = int(font_size/10)
        draw = PIL.ImageDraw.Draw(img)
        _, _, w, _ = draw.textbbox((0, 0), texts[0], font, align="center", stroke_width=3)
        draw.text(((img.width-w)/2, 0), texts[0], fill="white", font=font, align="center", stroke_width=stroke_width, stroke_fill="black")
        _, _, w, h = draw.textbbox((0, 0), texts[1], font, align="center", stroke_width=3)
        draw.text(((img.width-w)/2, img.height-h), texts[1], fill="white", font=font, align="center", stroke_width=stroke_width, stroke_fill="black")

    return imgs


def isolate_red(imgs: list[PIL.Image.Image]) -> list[PIL.Image.Image]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].convert("RGBA"))
        ar[:, :, [1, 2]] = 0
        imgs[i] = PIL.Image.fromarray(ar, "RGBA")
    return imgs
