import io
import tempfile

import PIL.Image


def from_file(file: io.IOBase) -> list[PIL.Image.Image]:
    img = PIL.Image.open(file)
    imgs = []
    for i in range(img.n_frames):
        img.seek(i)
        imgs.append(img.convert())
    return imgs


def to_file(imgs: list[PIL.Image.Image]) -> tuple[tempfile._TemporaryFileWrapper, str]:
    f = tempfile.TemporaryFile()
    ext = ""
    if (len(imgs) == 1):
        ext = "png"
    else:
        ext = "gif"
    imgs[0].save(f.file, ext, save_all=True, append_images=imgs[1:])
    f.seek(0)
    return (f, ext)
