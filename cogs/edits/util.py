import asyncio
import multiprocessing
import typing

import interactions
import numpy as np
import numpy.typing
import PIL.Image


class ImageFrame:
    def __init__(self, frame: PIL.Image.Image, duration: int) -> None:
        self.frame = frame
        self.duration = duration


def normalize_coordinates(coords: np.ndarray, shape: numpy.typing.ArrayLike, square=True) -> np.ndarray:
    # convert integer coordinates to [-1,1] range
    centerd = coords - np.array(shape) / 2
    m = np.min(shape) if square else np.array(shape)
    scaled = centerd / m * 2
    return scaled


def unnormalize_coordinates(coords: np.ndarray, shape: numpy.typing.ArrayLike, square=True) -> np.ndarray:
    m = np.min(shape) if square else np.array(shape)
    centered = coords * m / 2
    unnormalized = centered + np.array(shape) / 2
    return unnormalized


class PsuedoContext:
    """A class with a send method. Minimally imitates a SlashContext. For commands where the context expires before it finishes."""

    def __init__(self, msg: interactions.Message) -> None:
        self.msg = msg

    async def send(self, **kwargs) -> None:
        self.msg = await self.msg.reply(**kwargs)


async def run_in_subprocess(f: typing.Callable[..., list[ImageFrame]], args: tuple) -> list[ImageFrame]:
    q: multiprocessing.Queue[list[ImageFrame] | Exception] = multiprocessing.Queue()

    p = multiprocessing.Process(target=run_process, args=(f, args, q))
    p.start()
    while p.is_alive() and q.empty():
        await asyncio.sleep(1)
    if (q.empty()):
        raise RuntimeError(f"subprocess exited with code {p.exitcode} and returned no output")
    res = q.get()
    if (isinstance(res, Exception)):
        raise res
    return res


def run_process(f: typing.Callable[..., list[ImageFrame]], args: tuple, q: multiprocessing.Queue):
    try:
        q.put(f(*args))
    except Exception as e:
        q.put(e)
