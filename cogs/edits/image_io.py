import logging
import io
import tempfile
import typing

import requests
import PIL.Image
import interactions

logger = logging.getLogger(__name__)


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


async def from_url(ctx_update: interactions.SlashContext, url: str) -> typing.Optional[list[PIL.Image.Image]]:
    res = requests.get(url)
    with io.BytesIO(res.content) as f:
        try:
            return from_file(f)
        except PIL.UnidentifiedImageError as e:
            await ctx_update.send("unable to read image file")
            logger.info(e)
            return None


async def send_file(ctx_update: interactions.SlashContext, img: list[PIL.Image.Image]) -> None:
    f, ext = to_file(img)
    await ctx_update.send(file=interactions.File(typing.cast(io.IOBase, f.file), f"file.{ext}"))
