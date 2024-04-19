import logging

import interactions

import util

logger = logging.getLogger(__name__)


class Nya(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="nya")
    async def nya(self, ctx: interactions.SlashContext) -> None:
        await ctx.send("nya!")
