import logging
import re
import typing

import interactions
import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

logger = logging.getLogger(__name__)


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


def multiply(imgs: list[PIL.Image.Image], color: tuple[float, float, float, float]) -> list[PIL.Image.Image]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].convert("RGBA"))
        ar = (ar * color).astype(ar.dtype)
        imgs[i] = PIL.Image.fromarray(ar, "RGBA")
    return imgs


async def parse_colour(ctx_update: interactions.SlashContext, s: str) -> typing.Optional[tuple[float, float, float, float]]:
    s = s.strip()
    if (s.count(",") == 2 or s.count(",") == 3):
        ss = s.split(",")
        if (s.count(",") == 2):
            ss.append("255")
        base = 10
    elif (len(s) >= 6 and len(s) <= 9 and (len(s) % 2 == 0 or s[0] == "#")):
        if (len(s) % 2 == 1):
            s = s[1:]
        ss = [s[0:2], s[2:4], s[4:6], s[6:8] if len(s) == 8 else "FF"]
        base = 16
    else:
        await ctx_update.send("unknown colour format")
        return None
    try:
        return typing.cast(tuple[float, float, float, float], tuple([int(x, base)/255 for x in ss]))
    except ValueError as e:
        logger.info(e)
        await ctx_update.send("bad colour format")
        return None
