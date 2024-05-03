import logging
import random
import string
import typing

import interactions

from . import animated, basic, blur, misc, util

logger = logging.getLogger(__name__)

RandomEditType = tuple[util.ImageEditType, tuple[typing.Callable[[], typing.Any], ...]]


def intGenerator(a, b) -> typing.Callable[[], int]:
    return lambda: random.randint(a, b)


def floatGenerator(a, b) -> typing.Callable[[], float]:
    return lambda: random.random() * (b - a) + a


def colourGenerator() -> util.ColourType:
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def strGenerator() -> str:
    return "".join(random.choices(string.printable, k=1000))


T = typing.TypeVar("T")


def constantGenerator(v: T) -> typing.Callable[[], T]:
    return lambda: v


def boolGenerator() -> bool:
    return not random.getrandbits(1)


# categories
basic_edits: dict[str, RandomEditType] = {
    "hsv_hue": (basic.hsv_hue, ()),
    "hsv_saturation": (basic.hsv_saturation, ()),
    "hsv_value": (basic.hsv_value, ()),
    "invert": (basic.invert, ()),
    "tint": (basic.tint, (colourGenerator,)),
    "multiply": (basic.multiply, (colourGenerator,)),
    "grid": (basic.grid, (intGenerator(1, 10), colourGenerator)),
    "text": (basic.add_caption, (strGenerator, floatGenerator(0.5, 2))),
}
blur_edits: dict[str, RandomEditType] = {
    "blur": (blur.gaussianblur, (floatGenerator(1, 10),)),
    "motionblur": (blur.motionblur, (intGenerator(1, 20), floatGenerator(0, 360))),
    "zoomblur": (blur.zoomblur, (floatGenerator(0, 2), intGenerator(10, 30))),
    "circularblur": (blur.circularblur, (floatGenerator(1, 90), intGenerator(10, 30))),
}
animated_edits: dict[str, RandomEditType] = {
    "boom": (animated.boom, (constantGenerator(50), constantGenerator(10), floatGenerator(-3, 3), floatGenerator(-1, 1), floatGenerator(-1, 1))),
    "rave": (animated.hueshift, (constantGenerator(100), constantGenerator(18), constantGenerator(1), constantGenerator(1), constantGenerator(1))),
    "rainbow": (animated.hueshift, (constantGenerator(100), constantGenerator(18), constantGenerator(1), floatGenerator(0, 2), floatGenerator(0, 2))),
    "spin": (animated.spin, (constantGenerator(50), constantGenerator(5), constantGenerator(1), floatGenerator(0, 1), floatGenerator(-1, 1), floatGenerator(-1, 1))),
    "squish": (animated.squish, (constantGenerator(100), constantGenerator(5), constantGenerator(1), floatGenerator(0, 2))),
    "ash": (animated.ash, (constantGenerator(50), constantGenerator(50), constantGenerator(3), floatGenerator(0, 0.5), floatGenerator(0, 1), floatGenerator(-1, 1), floatGenerator(-1, 1))),
}
misc_edits: dict[str, RandomEditType] = {
    "snap": (misc.snap, (floatGenerator(0, 5), boolGenerator)),
    "magic": (misc.magic, (floatGenerator(0, 5),)),
    "bulge": (misc.bulge, (floatGenerator(-2, 2), floatGenerator(-1, 1), floatGenerator(-1, 1))),
}
categories: dict[str, dict[str, RandomEditType]] = {
    "basic": basic_edits,
    "blur": blur_edits,
    "animated": animated_edits,
    "misc": misc_edits,
}
# presets
presets: dict[str, dict[str, RandomEditType]] = {
    "all": basic_edits | blur_edits | animated_edits | misc_edits,
    "default": {x: basic_edits[x] for x in ["tint", "grid", "text"]} | blur_edits | animated_edits | misc_edits,
    "no_basic": blur_edits | animated_edits | misc_edits,
    "no_basic, no_blur": animated_edits | misc_edits,
    "none": {},
}


def randomEdits(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], iterations: int, preset: str, allow_basic: typing.Optional[bool], allow_blur: typing.Optional[bool], allow_animated: typing.Optional[bool], allow_misc: typing.Optional[bool]) -> list[util.ImageFrame]:
    available_edits = presets[preset]
    for c, b in [("basic", allow_basic), ("blur", allow_blur), ("animated", allow_animated), ("misc", allow_misc)]:
        if (b == None):
            continue
        for e in categories[c]:
            if (b):
                available_edits[e] = categories[c][e]
            else:
                available_edits.pop(e, None)
    if (len(available_edits) == 0):
        raise interactions.errors.BadArgument("no edits to choose from")
    available_edit_names = list(available_edits.keys())
    for _ in range(iterations):
        e = random.choice(available_edit_names)
        fun, args = available_edits[e]
        args = [f() for f in args]
        imgs = fun(ctx, imgs, *args)
    return imgs


def repeat(ctx: util.MultiprocessingPsuedoContext, imgs: list[util.ImageFrame], edit: util.ImageEditType, args: tuple) -> list[util.ImageFrame]:
    imgs = edit(ctx, imgs, *args)
    return imgs
