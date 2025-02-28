import logging
import typing

import interactions

import util

logger = logging.getLogger(__name__)


class Test(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="test", description="for testing things")
    async def test(self, ctx: interactions.SlashContext,
                   s: typing.Annotated[str, interactions.slash_str_option("link to the video", required=True)],
                   ) -> None:
        await util.preprocess(ctx)
        o = "nya?"
        if isinstance(o, typing.Awaitable):
            o = await o
        await ctx.send(content=str(o))
