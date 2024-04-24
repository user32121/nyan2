import logging
import os
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
        filename = os.path.join("cogs", "images", image)
        if (caption == None):
            await ctx.send(file=filename)  # TODO sanitize this
        else:
            img = image_io.from_file(open(filename, "rb"))
            img = basic.add_caption(img, caption, font_size)
            await image_io.send_file(ctx, img)
