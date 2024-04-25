import logging

import interactions
import numpy as np
import PIL
import PIL.Image
from matplotlib import pyplot as plt

from . import image_io

logger = logging.getLogger(__name__)


def hueshift(imgs: list[image_io.ImageFrame], delay: int, frames: int, cycles: float, scale_x: float, scale_y: float) -> list[image_io.ImageFrame]:
    if (len(imgs) == 1):
        imgs *= frames
        delays = [delay]*frames
    else:
        delays = [x.duration for x in imgs]
    hs = np.linspace(0, cycles*256-1, len(imgs)+1)
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("HSV"))

        ar[:, :, 0] = ar[:, :, 0] + hs[i]
        # note that x and y are swapped by PIL
        ar[:, :, 0] = ar[:, :, 0] + np.array(range(ar.shape[1])) * scale_x
        ar = np.swapaxes(ar, 0, 1)
        ar[:, :, 0] = ar[:, :, 0] + np.array(range(ar.shape[1])) * scale_y
        ar = np.swapaxes(ar, 0, 1)

        imgs[i] = image_io.ImageFrame(PIL.Image.fromarray(ar, "HSV").convert("RGBA"), delays[i])
    return imgs


def normalize_coordinates(coords: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    # convert integer coordinates to [-1,1] range
    centerd = coords - np.array(shape) / 2
    m = np.min(shape)
    scaled = centerd / m * 2
    return scaled


def unnormalize_coordinates(coords: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    m = np.min(shape)
    centered = coords * m / 2
    unnormalized = centered + np.array(shape) / 2
    return unnormalized


def centered_score(x: np.ndarray, center: float) -> np.ndarray:
    return np.maximum(1 - np.abs(x-center), 0)


def cubic(t: np.ndarray, ar: np.ndarray):
    # https://www.desmos.com/calculator/pqkx8j4ulh
    return -2 * t**3 * ar + 3 * t**2 * ar


async def spin(ctx: interactions.SlashContext, imgs: list[image_io.ImageFrame], delay: int, frames: int, cycles: float, radius: float, center_x: float, center_y: float) -> list[image_io.ImageFrame]:
    await ctx.send("this edit is very slow")
    if (len(imgs) == 1):
        imgs *= frames
        delays = [delay]*frames
    else:
        delays = [x.duration for x in imgs]
    thetas = np.linspace(0, cycles*2*np.pi, len(imgs)+1)
    for i in range(len(imgs)):
        await ctx.edit(content=f"this edit is very slow ({i}/{len(imgs)})")
        ar = np.array(imgs[i].frame.convert("RGBA"))

        offset = radius*np.array([np.cos(thetas[i]), np.sin(thetas[i])])
        shape = ar.shape[:2]
        xys = list(np.ndindex(shape))
        xys = np.reshape(xys, (*shape, 2))
        xys = normalize_coordinates(xys, shape)
        xys = xys + cubic(centered_score(xys[:, :, :1], center_y), cubic(centered_score(xys[:, :, 1:], center_x), offset.reshape((1, 1, 2))))
        # I don't think there's a way to conveniently vectorize this
        ar2 = np.zeros_like(ar)
        for j in range(1, shape[0]):
            for k in range(1, shape[1]):
                T1, L1 = unnormalize_coordinates(xys[j-1, k-1], shape)
                T2, R1 = unnormalize_coordinates(xys[j-1, k], shape)
                B1, L2 = unnormalize_coordinates(xys[j, k-1], shape)
                B2, R2 = unnormalize_coordinates(xys[j, k], shape)
                T = int(np.min((T1, T2)))
                B = int(np.max((B1, B2)))
                L = int(np.min((L1, L2)))
                R = int(np.max((R1, R2)))
                ar2[T:B, L:R] = ar[j, k]
        imgs[i] = image_io.ImageFrame(PIL.Image.fromarray(ar2, "RGBA"), delays[i])
    await ctx.edit(content="edit finished")
    return imgs
