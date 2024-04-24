import logging
import os
import pathlib
import typing

import interactions

import util

from .edits import basic, image_io

logger = logging.getLogger(__name__)


class Image(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="image", description="send an image")
    async def image(self, ctx: interactions.SlashContext,
                    image: typing.Annotated[str, interactions.slash_str_option("the image file", True, choices=util.as_choices(os.listdir(os.path.join("cogs", "images"))))],
                    caption: typing.Annotated[typing.Optional[str], interactions.slash_str_option(r"text to put on the image, separated by a ','. Escape with '\' to avoid splitting")] = None,
                    font_size: typing.Annotated[int, interactions.slash_float_option("relative size of caption")] = 1,
                    ) -> None:
        await util.preprocess(ctx)
        # surely this path sanitization is aggressive enough?
        if (".." in image or "/" in image or "\\" in image):
            raise interactions.errors.BadArgument("path traversal detected")
        filename = os.path.join("cogs", "images", image)
        # based on https://stackoverflow.com/a/56097763
        if (pathlib.Path("cogs", "images").resolve() not in pathlib.Path(filename).resolve().parents):
            raise interactions.errors.BadArgument("path traversal detected")

        if (caption == None):
            await ctx.send(file=filename)
        else:
            img = image_io.from_file(open(filename, "rb"))
            img = basic.add_caption(img, caption, font_size)
            await image_io.send_file(ctx, img)
