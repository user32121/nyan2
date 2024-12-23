import asyncio
import logging

import interactions

import util


logger = logging.getLogger(__name__)


class Test(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="test", description="for testing things")
    async def test(self, ctx: interactions.SlashContext,
                   ) -> None:
        await util.preprocess(ctx)
        ctx2 = util.PsuedoContext(ctx)
        await ctx2.send(content="message1 (next message in 10 seconds)")
        await asyncio.sleep(10)
        await ctx2.send(content="message2 (next message in 15 minutes 10 seconds)")
        await asyncio.sleep(15 * 60 + 10)
        await ctx2.send(content="message3")
