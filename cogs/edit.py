import logging
import tempfile
import io

import interactions
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

import util

logger = logging.getLogger(__name__)


# TODO
class Edit(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.not_implemented_args, name="edit")
    async def edit(self, ctx: interactions.SlashContext) -> None:
        await util.not_implemented(ctx)


def from_file(file: io.IOBase) -> list[PIL.Image.Image]:
    img = PIL.Image.open(file)
    imgs = []
    for i in range(img.n_frames):
        img.seek(i)
        imgs.append(img.convert())
    return imgs


def to_file(imgs: list[PIL.Image.Image]) -> tuple[tempfile._TemporaryFileWrapper, str]:
    f = tempfile.TemporaryFile()
    ext = ""
    if (len(imgs) == 1):
        ext = "png"
    else:
        ext = "gif"
    imgs[0].save(f.file, ext, save_all=True, append_images=imgs[1:])
    f.seek(0)
    return (f, ext)


def add_caption(imgs: list[PIL.Image.Image], text: str, relative_font_size: float = 1) -> list[PIL.Image.Image]:
    text = text.replace(r"\n", "\n")
    text = text.replace(r"\\", "\\")
    texts = text.split(",")
    if (len(texts) < 2):
        texts.append("")
    texts[0] = texts[0].replace(r"\,", ",")
    texts[1] = texts[1].replace(r"\,", ",")
    for img in imgs:
        font_size = int(img.width / 15 * relative_font_size)
        font = PIL.ImageFont.truetype("impact.ttf", font_size)
        stroke_width = int(font_size/10)
        draw = PIL.ImageDraw.Draw(img)
        _, _, w, _ = draw.textbbox((0, 0), text, font, align="center", stroke_width=3)
        draw.text(((img.width-w)/2, 0), texts[0], fill="white", font=font, align="center", stroke_width=stroke_width, stroke_fill="black")
        _, _, w, h = draw.textbbox((0, 0), text, font, align="center", stroke_width=3)
        draw.text(((img.width-w)/2, img.height-h), texts[1], fill="white", font=font, align="center", stroke_width=stroke_width, stroke_fill="black")
    return imgs
