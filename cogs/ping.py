import logging

import interactions

import util

logger = logging.getLogger(__name__)


class Ping(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(**util.command_args, name="ping", description="check if the bot is responsive")
    async def ping(self, ctx: interactions.SlashContext) -> None:
        if (await util.preprocess(ctx)):
            return
        await ctx.send("pong\nping")
