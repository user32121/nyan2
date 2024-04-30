import interactions
import numpy as np
import numpy.typing


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
