import numpy as np
import PIL
import PIL.Image
import PIL.ImageFilter
import scipy

from . import image_io


def gaussianblur(imgs: list[image_io.ImageFrame], radius: float) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        imgs[i].frame = imgs[i].frame.filter(PIL.ImageFilter.GaussianBlur(radius))
    return imgs


def motionblur(imgs: list[image_io.ImageFrame], length: int, angle: float) -> list[image_io.ImageFrame]:
    kernel = np.reshape([0, 0, 1, 0, 0], (5, 1))
    kernel = PIL.Image.fromarray(kernel)
    kernel = kernel.resize((length, 5))
    kernel = kernel.rotate(angle, expand=True)
    kernel = np.array(kernel)
    kernel = kernel / np.sum(kernel)
    for i in range(len(imgs)):
        ar = np.array(imgs[i].frame.convert("RGBA"))
        for j in range(ar.shape[2]):
            ar[:, :, j] = scipy.signal.convolve2d(ar[:, :, j], kernel, "same")
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs


def zoomblur(imgs: list[image_io.ImageFrame], zoom: float, interpolation: int) -> list[image_io.ImageFrame]:
    for i in range(len(imgs)):
        ars = []
        for z in np.linspace(1, zoom, interpolation):
            img = imgs[i].frame.resize((int(imgs[i].frame.width*z), int(imgs[i].frame.height*z)))
            img = img.crop(((img.width-imgs[i].frame.width)//2, (img.height-imgs[i].frame.height)//2, (img.width+imgs[i].frame.width)//2, (img.height+imgs[i].frame.height)//2))
            ars.append(np.array(img.convert("RGBA")))
        ar = np.mean(ars, axis=0).astype(ars[0].dtype)
        imgs[i].frame = PIL.Image.fromarray(ar, "RGBA")
    return imgs
