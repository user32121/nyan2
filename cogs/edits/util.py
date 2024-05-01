import asyncio
import multiprocessing
import traceback
import typing

import interactions
import numpy as np
import numpy.typing
import PIL.Image
import PIL.ImageColor

T = typing.TypeVar("T")
ColourType = tuple[int, int, int, int]


class ColourConverter(interactions.Converter):
    async def convert(self, ctx: interactions.SlashContext, arg: str) -> ColourType:
        try:
            res = PIL.ImageColor.getrgb(arg)
        except ValueError as e:
            raise interactions.errors.BadArgument(str(e))
        if (len(res) == 3):
            return (*res, 255)
        return res


class ImageFrame:
    def __init__(self, frame: PIL.Image.Image, duration: int) -> None:
        self.frame = frame
        self.duration = duration


ImageEditType = typing.Callable[..., list[ImageFrame]]


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

    def __init__(self, ctx: interactions.Message | interactions.SlashContext) -> None:
        self.ctx = ctx

    async def send(self, **kwargs) -> interactions.Message:
        if (isinstance(self.ctx, interactions.SlashContext)):
            self.ctx = await self.ctx.send(**kwargs)
        else:
            self.ctx = await self.ctx.reply(**kwargs)
        return self.ctx


class MultiprocessingResult(typing.Generic[T]):
    def __init__(self, res: T) -> None:
        self.res = res


class MultiprocessingPsuedoContext:
    """Allows sending basic text so the user knows what is happening"""

    def __init__(self, q: multiprocessing.Queue) -> None:
        self.q = q

    def send(self, **kwargs) -> None:
        self.q.put(kwargs)


async def run_in_subprocess(ctx: interactions.SlashContext | PsuedoContext, f: typing.Callable[..., T], args: tuple, kwargs: dict[str, typing.Any] = {}) -> T:
    q: multiprocessing.Queue[MultiprocessingResult[T] | tuple[Exception, list[str]] | dict] = multiprocessing.Queue()

    p = multiprocessing.Process(target=run_process, args=(f, args, kwargs, q))
    p.start()
    while True:
        while p.is_alive() and q.empty():
            await asyncio.sleep(1)
        if (q.empty()):
            raise RuntimeError(f"subprocess exited with code {p.exitcode} and returned no output")
        res = q.get()
        if (type(res) == dict):
            await ctx.send(**res)
        else:
            break
    if (type(res) == tuple):
        e, tb = res
        print("\n".join(tb))
        raise e
    elif (type(res) == MultiprocessingResult):
        return res.res
    raise TypeError(f"unhandled type {type(res)}")


def run_process(f:  typing.Callable[..., T], args: tuple, kwargs: dict[str, typing.Any], q: multiprocessing.Queue):
    q2: multiprocessing.Queue[MultiprocessingResult[T] | tuple[Exception, list[str]] | dict] = q
    try:
        q2.put(MultiprocessingResult(f(MultiprocessingPsuedoContext(q2), *args, **kwargs)))
    except Exception as e:
        q2.put((e, traceback.format_exception(e)))
