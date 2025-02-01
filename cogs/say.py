import logging
import typing

import interactions

import util

logger = logging.getLogger(__name__)


class Say(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="say", description="say a message")
    async def say(self, ctx: interactions.SlashContext,
                  text: typing.Annotated[str, interactions.slash_str_option("text to say", required=True)],
                  ) -> None:
        await util.preprocess(ctx)
        await ctx.send(text)
