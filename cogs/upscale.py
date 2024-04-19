import logging

import interactions

import util

logger = logging.getLogger(__name__)


# TODO
class Upscale(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.not_implemented_args, name="upscale")
    async def upscale(self, ctx: interactions.SlashContext) -> None:
        await util.not_implemented(ctx)
