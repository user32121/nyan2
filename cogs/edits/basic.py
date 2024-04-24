import logging
import re
import typing

import interactions
import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from . import image_io

logger = logging.getLogger(__name__)


def add_caption(imgs: list[image_io.ImageFrame], text: str, relative_font_size: float = 1) -> list[image_io.ImageFrame]:
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
        font_size = int(img.frame.width / 15 * relative_font_size)
        font = PIL.ImageFont.truetype("impact.ttf", font_size)
        stroke_width = int(font_size/10)
        draw = PIL.ImageDraw.Draw(img.frame)
        _, _, w, _ = draw.textbbox((0, 0), texts[0], font, align="center", stroke_width=3)
        draw.text(((img.frame.width-w)/2, 0), texts[0], fill="white", font=font, align="center", stroke_width=stroke_width, stroke_fill="black")
        _, _, w, h = draw.textbbox((0, 0), texts[1], font, align="center", stroke_width=3)
        draw.text(((img.frame.width-w)/2, img.frame.height-h), texts[1], fill="white", font=font, align="center", stroke_width=stroke_width, stroke_fill="black")

    return imgs


def multiply(imgs: list[image_io.ImageFrame], color: tuple[int, int, int, int]) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        ar = (ar * color / 255).astype(ar.dtype)
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


class ColourConverter(interactions.Converter):
    async def convert(self, ctx: interactions.SlashContext, arg: str) -> tuple[int, int, int, int]:
        arg = arg.strip()
        if (arg.count(",") == 2 or arg.count(",") == 3):
            ss = arg.split(",")
            if (arg.count(",") == 2):
                ss.append("255")
            base = 10
        elif (len(arg) >= 6 and len(arg) <= 9 and (len(arg) % 2 == 0 or arg[0] == "#")):
            if (len(arg) % 2 == 1):
                arg = arg[1:]
            ss = [arg[0:2], arg[2:4], arg[4:6], arg[6:8] if len(arg) == 8 else "FF"]
            base = 16
        else:
            raise interactions.errors.BadArgument("unknown colour format")
        try:
            return typing.cast(tuple[int, int, int, int], tuple([int(x, base) for x in ss]))
        except ValueError as e:
            logger.info(e)
            raise interactions.errors.BadArgument("bad colour format")


def hsv_hue(imgs: list[image_io.ImageFrame]) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("HSV"))
        ar[:, :, [1, 2]] = 255
        imgs[i].frame = PIL.Image.fromarray(ar, "HSV").convert("RGBA")
    return imgs


def hsv_saturation(imgs: list[image_io.ImageFrame]) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("HSV"))
        ar[:, :, 0] = ar[:, :, 1]
        ar[:, :, 2] = ar[:, :, 1]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGB")
    return imgs


def hsv_value(imgs: list[image_io.ImageFrame]) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("HSV"))
        ar[:, :, 0] = ar[:, :, 2]
        ar[:, :, 1] = ar[:, :, 2]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGB")
    return imgs


def invert(imgs: list[image_io.ImageFrame]) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        ar[:, :, :3] = 255 - ar[:, :, :3]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def tint(imgs: list[image_io.ImageFrame], colour: tuple[int, int, int, int]) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        ar = ((ar + colour) / 2).astype(ar.dtype)
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def grid(imgs: list[image_io.ImageFrame], thickness: int, colour: tuple[int, int, int, int]) -> list[image_io.ImageFrame]:
    t = thickness
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        for j in range(1, 10):
            width, height, _ = ar.shape
            x = width * j // 10
            y = height * j // 10
            ar[x-t//2:x+(t+1)//2, :] = colour
            ar[:, y-t//2:y+(t+1)//2] = colour
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs
