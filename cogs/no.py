import logging

import interactions

import util

logger = logging.getLogger(__name__)


class No(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="no", description="no")
    async def no(self, ctx: interactions.SlashContext) -> None:
        await ctx.send("no\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ")
