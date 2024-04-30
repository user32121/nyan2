import io
import logging
import random
import re
import tempfile
import typing

import interactions
import PIL.Image
import requests

import config

from . import util

logger = logging.getLogger(__name__)


def from_file(file: io.IOBase) -> list[util.ImageFrame]:
    img = PIL.Image.open(file)
    imgs: list[util.ImageFrame] = []
    for i in range(getattr(img, "n_frames", 1)):
        img.seek(i)
        imgs.append(util.ImageFrame(img.convert("RGBA"), img.info.get("duration", 0)))
    return imgs


def to_file(imgs: list[util.ImageFrame]) -> tuple[tempfile._TemporaryFileWrapper, str]:
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


def from_url(url: str) -> list[util.ImageFrame]:
    res = requests.get(url)
    with io.BytesIO(res.content) as f:
        try:
            return from_file(f)
        except PIL.UnidentifiedImageError as e:
            logger.info(e)
            raise interactions.errors.BadArgument(f"unable to read {url} as image file")


async def send_file(ctx_update: interactions.SlashContext | util.PsuedoContext, img: list[util.ImageFrame], allow_downscaling=True):
    from . import misc
    f, ext = to_file(img)
    file_size = f.seek(0, 2)
    while allow_downscaling and file_size > config.MAX_FILE_SIZE:
        await ctx_update.send(content=f"{file_size} > {config.MAX_FILE_SIZE} bytes, downscaling...")
        img = misc.downscale(img)
        f, ext = to_file(img)
        file_size = f.seek(0, 2)
    f.seek(0)
    if (file_size <= config.MAX_FILE_SIZE):
        await ctx_update.send(file=interactions.File(typing.cast(io.IOBase, f.file), f"file.{ext}"))
    else:
        await ctx_update.send(content=f"{file_size} > {config.MAX_FILE_SIZE} bytes, using tmpfiles.org...")
        res = requests.post(url="https://tmpfiles.org/api/v1/upload", files={"file": (f"{random.randint(0, 1 << 64):x}.{ext}", f)})
        if (res.status_code == 200):
            url = res.json()["data"]["url"]
            url = re.sub(r"https:\/\/tmpfiles\.org\/(\d+\/\w+\.\w+)", r"https://tmpfiles.org/dl/\1", url)
            await ctx_update.send(content=url)
        else:
            raise RuntimeError(res.content)
