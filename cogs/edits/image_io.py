import io
import logging
import tempfile
import typing

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
    for i in range(img.n_frames):
        img.seek(i)
        imgs.append(ImageFrame(img.convert(), img.info["duration"]))
    return imgs


def to_file(imgs: list[ImageFrame]) -> tuple[tempfile._TemporaryFileWrapper, str]:
    f = tempfile.TemporaryFile()
    ext = ""
    if (len(imgs) == 1):
        ext = "png"
    else:
        ext = "gif"
    frames = [x.frame for x in imgs]
    durations = [x.duration for x in imgs]
    imgs[0].frame.save(f.file, ext, save_all=True, append_images=frames[1:], loop=0, duration=durations)
    f.seek(0)
    return (f, ext)


async def from_url(ctx_update: interactions.SlashContext, url: str) -> typing.Optional[list[ImageFrame]]:
    res = requests.get(url)
    with io.BytesIO(res.content) as f:
        try:
            return from_file(f)
        except PIL.UnidentifiedImageError as e:
            await ctx_update.send("unable to read image file")
            logger.info(e)
            return None


async def send_file(ctx_update: interactions.SlashContext, img: list[ImageFrame]) -> None:
    f, ext = to_file(img)
    await ctx_update.send(file=interactions.File(typing.cast(io.IOBase, f.file), f"file.{ext}"))
