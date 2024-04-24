import numpy as np
import PIL
import PIL.Image

from . import image_io


def rave(imgs: list[image_io.ImageFrame], delay: int, frames: int, cycles: float) -> list[image_io.ImageFrame]:
    if (len(imgs) == 1):
        imgs *= frames
        delays = [delay]*frames
    else:
        delays = [x.duration for x in imgs]
    hs = np.linspace(0, cycles*256-1, len(imgs)+1)
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("HSV"))
        ar[:, :, 0] = ar[:, :, 0] + hs[i]
        imgs[i] = image_io.ImageFrame(PIL.Image.fromarray(ar, "HSV").convert("RGBA"), delays[i])
    return imgs
