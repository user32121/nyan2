import io
import logging
import tempfile
import typing

import PIL.GifImagePlugin
import interactions
import PIL.Image
import requests

logger = logging.getLogger(__name__)


class ImageFrame:
    def __init__(self, frame: PIL.Image.Image, duration: int) -> None:
        self.frame = frame
        self.duration = duration


def from_file(file: io.IOBase) -> list[ImageFrame]:
    img = PIL.Image.open(file)
    imgs: list[ImageFrame] = []
    for i in range(getattr(img, "n_frames", 1)):
        img.seek(i)
        imgs.append(ImageFrame(img.convert("RGBA"), img.info.get("duration", 0)))
    return imgs


def to_file(imgs: list[ImageFrame]) -> tuple[tempfile._TemporaryFileWrapper, str]:
    f = tempfile.TemporaryFile()
    ext = ""
    if (len(imgs) == 1):
        ext = "png"
    else:
        ext = "gif"
        for img in imgs:
            img.frame = img.frame.convert("RGB").quantize(method=PIL.Image.Quantize.MAXCOVERAGE)
    frames = [x.frame for x in imgs]
    durations = [x.duration for x in imgs]
    imgs[0].frame.save(f.file, ext, save_all=True, append_images=frames[1:], loop=0, duration=durations)
    f.seek(0)
    return (f, ext)


def from_url(url: str) -> list[ImageFrame]:
    res = requests.get(url)
    with io.BytesIO(res.content) as f:
        try:
            return from_file(f)
        except PIL.UnidentifiedImageError as e:
            logger.info(e)
            raise interactions.errors.BadArgument(f"unable to read {url} as image file")


async def send_file(ctx_update: interactions.SlashContext, img: list[ImageFrame]):
    f, ext = to_file(img)
    await ctx_update.send(file=interactions.File(typing.cast(io.IOBase, f.file), f"file.{ext}"))
