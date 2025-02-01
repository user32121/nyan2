import logging

import interactions

import util

logger = logging.getLogger(__name__)


class Ping(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(**util.command_args, name="ping", description="check if the bot is responsive")
    async def ping(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        await ctx.send("pong\nping")
