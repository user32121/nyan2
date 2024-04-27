import numpy as np
import PIL.Image

from . import image_io, animated


def bulge(imgs: list[image_io.ImageFrame], amount: float, center_x: float, center_y: float) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        shape = ar.shape[:2]
        xys = list(np.ndindex(shape))
        xys = np.reshape(xys, (*shape, 2))
        xys = animated.normalize_coordinates(xys, shape)
        xys = xys - [center_x, center_y]
        dists = np.linalg.norm(xys, axis=2)
        xys *= np.expand_dims(dists ** ((1.5 ** amount) - 1), axis=2)
        xys = xys + [center_y, center_x]
        xys = animated.unnormalize_coordinates(xys, shape).astype(int)
        xys = np.clip(xys, 0, np.array(shape)-1)
        ar = ar[xys[:, :, 0], xys[:, :, 1]]
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs
