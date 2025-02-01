import logging

import interactions

import util

logger = logging.getLogger(__name__)


class Nya(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="nya", description="nya")
    async def nya(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        await ctx.send("nya!")
