import logging
import time
import typing

import interactions

import util

logger = logging.getLogger(__name__)


class React(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @ interactions.slash_command(** util.command_args, name="react", description="react to a message with an emoji")
    async def react(self, ctx: interactions.SlashContext,
                    message: typing.Annotated[interactions.Message, interactions.MessageConverter, interactions.slash_str_option("message id to react to", True)],
                    emoji: typing.Annotated[str, interactions.slash_str_option("emoji to react with", True, autocomplete=True)],
                    ) -> None:
        await util.preprocess(ctx)
        self.bot: interactions.Client

        e = await util.get_emoji(ctx, emoji)

        await message.add_reaction(e)
        await ctx.send("reacted")

    @ react.autocomplete("emoji")
    async def get_emojis(self, ctx: interactions.AutocompleteContext):
        await util.get_emojis(ctx)
