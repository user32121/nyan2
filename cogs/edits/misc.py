import logging
import random

import numpy as np
import PIL.Image
import torch

from . import animated, image_io

logger = logging.getLogger(__name__)


def bulge(imgs: list[image_io.ImageFrame], amount: float, center_x: float, center_y: float) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        shape = ar.shape[:2]
        xys = list(np.ndindex(shape))
        xys = np.reshape(xys, (*shape, 2))
        xys = animated.normalize_coordinates(xys, shape)
        xys = xys - [center_y, center_x]
        dists = np.linalg.norm(xys, axis=2)
        dists = np.minimum(dists, 1)
        xys *= np.expand_dims(dists ** ((2 ** amount) - 1), axis=2)
        xys = xys + [center_y, center_x]
        xys = animated.unnormalize_coordinates(xys, shape).astype(int)
        xys = np.clip(xys, 0, np.array(shape)-1)
        ar = ar[xys[:, :, 0], xys[:, :, 1]]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def snap(imgs: list[image_io.ImageFrame], steps: float, fuzzy: bool) -> list[image_io.ImageFrame]:
    # TODO optimize by batching
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        xy = animated.unnormalize_coordinates(np.random.random(2) * 2 - 1, ar.shape[:2] - np.array([1, 1]), False).astype(int)
        for _ in range(int(steps * imgs[i].frame.width * imgs[i].frame.height)):
            p = ar[xy[0], xy[1]]
            dir = random.randint(0, 3)
            xy2 = xy + np.select([dir == 0, dir == 1, dir == 2, dir == 3], [[0, 1], [1, 0], [0, -1], [-1, 0]])
            xy2 = xy2 % ar.shape[:2]
            p2 = ar[xy2[0], xy2[1]]
            if (fuzzy):
                p = p2 = (p + p2.astype(int)) / 2
            ar[xy[0], xy[1]] = p2
            ar[xy2[0], xy2[1]] = p
            xy = xy2
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def magic(imgs: list[image_io.ImageFrame], steps: float) -> list[image_io.ImageFrame]:
    # TODO optimize by batching
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        for _ in range(int(steps * imgs[i].frame.width * imgs[i].frame.height)):
            xy = animated.unnormalize_coordinates(np.random.random(2) * 2 - 1, ar.shape[:2] - np.array([1, 1]), False).astype(int)
            xy2 = xy + [[0, 1], [1, 0], [0, -1], [-1, 0]]
            xy2 = xy2 % ar.shape[:2]
            ar[xy2[:, 0], xy2[:, 1]] = ar[xy[0], xy[1]]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


upscale_model = torch.hub.load("nagadomi/nunif:master", "waifu2x", method="scale", noise_level=3)  # , trust_repo=False)


def upscale(imgs: list[image_io.ImageFrame]) -> list[image_io.ImageFrame]:
    for img in imgs:
        img.frame = upscale_model.infer(img.frame)
    return imgs
