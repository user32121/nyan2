import logging

import interactions

import util

logger = logging.getLogger(__name__)


class Say(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="say", description="say a message")
    async def say(self, ctx: interactions.SlashContext,
                  text: interactions.slash_str_option("text to say", required=True),  # type: ignore
                  ) -> None:
        await ctx.send(text)
