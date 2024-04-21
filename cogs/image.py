import logging
import os
import io
import typing

import interactions

import util
from .edits import image_io
from .edits import basic

logger = logging.getLogger(__name__)


class Image(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="image", description="send an image")
    async def image(self, ctx: interactions.SlashContext,
                    image: interactions.slash_str_option("the image file", True,  # type: ignore
                                                         choices=util.as_choices(os.listdir(os.path.join("cogs", "images")))),
                    caption: interactions.slash_str_option("text to put on the image, escaped with '\\' as necessary") = None,  # type: ignore
                    font_size: interactions.slash_float_option("relative size of caption") = 1,  # type: ignore
                    ) -> None:
        await ctx.defer()
        filename = os.path.join("cogs", "images", image)
        if (caption == None):
            await ctx.send(file=filename)  # might need to sanitize this
        else:
            img = image_io.from_file(open(filename, "rb"))
            img = basic.add_caption(img, caption, font_size)
            await image_io.send_file(ctx, img)
