import logging

import interactions
import numpy as np
import PIL.Image
import PIL.ImageColor
import PIL.ImageDraw
import PIL.ImageFont

from . import image_io

logger = logging.getLogger(__name__)


def add_caption(imgs: list[image_io.ImageFrame], text: str, relative_font_size: float = 1) -> list[image_io.ImageFrame]:
    text = text.replace(r"\\", chr(0))
    text = text.replace(r"\,", chr(1))
    text = text.replace(r"\n", chr(2))
    texts = text.split(",")
    if (len(texts) < 2):
        texts.append("")
    for i in range(2):
        texts[i] = texts[i].replace(chr(0), "\\")
        texts[i] = texts[i].replace(chr(1), ",")
        texts[i] = texts[i].replace(chr(1), "\n")

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
        try:
            res = PIL.ImageColor.getrgb(arg)
        except ValueError as e:
            raise interactions.errors.BadArgument(str(e))
        if (len(res) == 3):
            return (*res, 255)
        return res


def hsv_hue(imgs: list[image_io.ImageFrame]) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("HSV"))
        ar[np.expand_dims(((ar[:, :, 0:2] != 0).any(axis=2)), axis=2) & [[[False, True, True]]]] = 255
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
