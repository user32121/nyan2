import logging

import numpy as np
import PIL.Image
import torch

from . import util

logger = logging.getLogger(__name__)


def bulge(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], amount: float, center_x: float, center_y: float) -> list[util.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        shape = ar.shape[:2]
        xys = list(np.ndindex(shape))
        xys = np.reshape(xys, (*shape, 2))
        xys = util.normalize_coordinates(xys, shape)
        xys = xys - [center_y, center_x]
        dists = np.linalg.norm(xys, axis=2)
        dists = np.minimum(dists, 1)
        xys *= np.expand_dims(dists ** ((2 ** amount) - 1), axis=2)
        xys = xys + [center_y, center_x]
        xys = util.unnormalize_coordinates(xys, shape).astype(int)
        xys = np.clip(xys, 0, np.array(shape)-1)
        ar = ar[xys[:, :, 0], xys[:, :, 1]]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def snap(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], steps: float, fuzzy: bool) -> list[util.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        xys = util.unnormalize_coordinates(np.random.random((1000, 2)) * 2 - 1, ar.shape[:2] - np.array([1, 1]), False).astype(int)
        for _ in range(int(np.ceil(steps * imgs[i].frame.width * imgs[i].frame.height / 1000))):
            ps = ar[xys[:, 0], xys[:, 1]]
            dirs = np.random.randint(0, 3, size=1000)
            xys2 = xys + np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])[dirs]
            xys2 = xys2 % ar.shape[:2]
            ps2 = ar[xys2[:, 0], xys2[:, 1]]
            if (fuzzy):
                ps = ps2 = (ps + ps2.astype(int)) / 2
            ar[xys[:, 0], xys[:, 1]] = ps2
            ar[xys2[:, 0], xys2[:, 1]] = ps
            xys = xys2
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def magic(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], steps: float) -> list[util.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        for _ in range(int(np.ceil(steps * imgs[i].frame.width * imgs[i].frame.height / 1000))):
            xys = util.unnormalize_coordinates(np.random.random((1000, 2)) * 2 - 1, ar.shape[:2] - np.array([1, 1]), False).astype(int)
            xys2 = xys + [[[0, 1]], [[1, 0]], [[0, -1]], [[-1, 0]]]
            xys2 = xys2 % ar.shape[:2]
            ar[xys2[:, :, 0], xys2[:, :, 1]] = ar[xys[:, 0], xys[:, 1]]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def estimate_upscale_time(imgs: list[util.ImageFrame]) -> float:
    model = np.array([0.01719520916958716, 0.015768912367664353, 0.00010084009583629158, 3.083678905690488])
    total = 0
    for img in imgs:
        width = img.frame.width
        height = img.frame.height
        total += np.dot([width, height, width * height, 1], model)
    return total


def upscale(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame]) -> list[util.ImageFrame]:
    expected_time = estimate_upscale_time(imgs)
    ctx.send(content=f"processing... (approximately {expected_time:.3f}s)")
    upscale_model = torch.hub.load("nagadomi/nunif:master", "waifu2x", method="scale", noise_level=3)  # , trust_repo=False)
    for img in imgs:
        img.frame = upscale_model.infer(img.frame)
    return imgs


def downscale(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame]) -> list[util.ImageFrame]:
    for img in imgs:
        img.frame = img.frame.resize((img.frame.width // 2, img.frame.height // 2))
    return imgs
