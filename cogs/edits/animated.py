import logging
import os

import numpy as np
import PIL.Image

from . import image_io, misc, util

logger = logging.getLogger(__name__)


def hueshift(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], delay: int, frames: int, cycles: float, scale_x: float, scale_y: float) -> list[util.ImageFrame]:
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

        imgs[i] = util.ImageFrame(PIL.Image.fromarray(ar, "HSV").convert("RGBA"), delays[i])
    return imgs


def centered_score(x: np.ndarray, center: float) -> np.ndarray:
    return np.maximum(1 - np.abs(x-center), 0)


def cubic(t: np.ndarray, ar: np.ndarray) -> np.ndarray:
    # https://www.desmos.com/calculator/pqkx8j4ulh
    return -2 * t**3 * ar + 3 * t**2 * ar


def spin(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], delay: int, frames: int, cycles: float, radius: float, center_x: float, center_y: float) -> list[util.ImageFrame]:
    if (len(imgs) == 1):
        imgs *= frames
        delays = [delay]*frames
    else:
        delays = [x.duration for x in imgs]
    thetas = np.linspace(0, cycles*2*np.pi, len(imgs)+1)
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))

        offset = radius*np.array([np.cos(thetas[i]), np.sin(thetas[i])])
        shape = ar.shape[:2]
        xys = list(np.ndindex(shape))
        xys = np.reshape(xys, (*shape, 2))
        xys = util.normalize_coordinates(xys, shape)
        xys = xys + cubic(centered_score(xys[:, :, :1], center_y), cubic(centered_score(xys[:, :, 1:], center_x), offset.reshape((1, 1, 2))))
        # optimize by precomputing TBLR
        xys_unnorm = util.unnormalize_coordinates(xys, shape)
        Ts = np.minimum(xys_unnorm[:-1, :-1, 0], xys_unnorm[:-1, 1:, 0]).astype(int)
        Bs = np.maximum(xys_unnorm[1:, :-1, 0], xys_unnorm[1:, 1:, 0]).astype(int)
        Ls = np.minimum(xys_unnorm[:-1, :-1, 1], xys_unnorm[1:, :-1, 1]).astype(int)
        Rs = np.maximum(xys_unnorm[:-1, 1:, 1], xys_unnorm[1:, 1:, 1]).astype(int)
        # I don't think there's a way to conveniently vectorize this
        ar2 = np.full_like(ar, 255)
        for j in range(0, shape[0] - 1):
            for k in range(0, shape[1] - 1):
                ar2[Ts[j, k]:Bs[j, k], Ls[j, k]:Rs[j, k]] = ar[j, k]
        imgs[i] = util.ImageFrame(PIL.Image.fromarray(ar2, "RGBA"), delays[i])
    return imgs


def boom(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], delay: int, frames: int, amount: float, center_x: float, center_y: float) -> list[util.ImageFrame]:
    if (len(imgs) == 1):
        imgs *= frames
        delays = [delay]*frames
    else:
        delays = [x.duration for x in imgs]
    amounts = np.linspace(0, amount, len(imgs)+1)
    for i in range(len(imgs)):
        img = util.ImageFrame(imgs[i].frame.copy(), 0)
        img = misc.bulge(ctx, [img], amounts[i], center_x, center_y)[0]
        imgs[i] = util.ImageFrame(img.frame, delays[i])
    boom_imgs = image_io.from_file(open(os.path.join("cogs", "images", "boom.gif"), "rb"))
    for i in range(len(boom_imgs)):
        boom_imgs[i].frame = boom_imgs[i].frame.resize(imgs[0].frame.size)
    return imgs + boom_imgs


def squish(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], delay: int, frames: int, cycles: float, amount: float) -> list[util.ImageFrame]:
    if (len(imgs) == 1):
        imgs *= frames
        delays = [delay]*frames
    else:
        delays = [x.duration for x in imgs]
    thetas = np.linspace(0, 2 * np.pi * cycles, len(imgs)+1)
    for i in range(len(imgs)):
        factor = 2 ** (np.sin(thetas[i]) * amount / 2)
        # note: width used twice is intended
        img = imgs[i].frame.resize((int(imgs[i].frame.width * factor), int(imgs[i].frame.width / factor)))
        img2 = PIL.Image.new("RGBA", imgs[i].frame.size, "white")
        img2.alpha_composite(img, ((img2.width - img.width) // 2, (img2.height - img.height) // 2))
        imgs[i] = util.ImageFrame(img2, delays[i])
    return imgs


def gradient(xys: np.ndarray, t: float) -> np.ndarray:
    return 2 * xys[:, 0] + xys[:, 1] + t * 3


def ash(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], delay: int, frames: int, time_steps: int) -> list[util.ImageFrame]:
    if (len(imgs) == 1):
        imgs *= frames
        delays = [delay]*frames
    else:
        delays = [x.duration for x in imgs]

    init_vel = None
    ts = np.linspace(0, time_steps, len(imgs)+1)
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        shape = ar.shape[:2]
        xys = list(np.ndindex(shape))
        xys = np.reshape(xys, (*shape, 2))
        if (init_vel is None):
            init_vel = np.random.normal(0, 0.2, (*shape[:2], 4, 2))
        mask = (ar < 240).any(axis=2)
        xys = xys[mask]
        xys = np.repeat(xys, 4, axis=0)
        xys = util.normalize_coordinates(xys, shape)
        grad1 = np.expand_dims(np.maximum(gradient(xys, ts[i] - 1.5), 0), 1) / 3
        grav_vel = np.array([-0.5, 0]) * grad1
        xys2 = xys + np.reshape(init_vel[mask], (-1, 2)) * grad1 + grav_vel * grad1
        xys2 = np.round(util.unnormalize_coordinates(xys2, shape)).astype(int)
        xys2 = np.clip(xys2, 0, np.array(shape) - 1)
        ar2 = np.full_like(ar, 255)
        grad2 = np.expand_dims(np.clip(gradient(xys, ts[i] - 1), 0, 1), 1) * 0.9
        ar2[xys2[:, 0], xys2[:, 1]] = (1 - grad2) * np.repeat(ar[mask], 4, axis=0) + grad2 * [46, 28, 12, 255]
        imgs[i] = util.ImageFrame(PIL.Image.fromarray(ar2, "RGBA"), delays[i])
    return imgs
