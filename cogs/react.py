import logging
import time

import interactions

import util

logger = logging.getLogger(__name__)


class React(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @ interactions.slash_command(** util.command_args, name="react", description="react to a message with an emoji")
    async def react(self, ctx: interactions.SlashContext,
                    message: interactions.slash_str_option("message id to react to", True),  # type: ignore
                    emoji: interactions.slash_str_option("emoji to react with", True, autocomplete=True),  # type: ignore
                    ) -> None:
        if (await util.preprocess(ctx)):
            return
        self.bot: interactions.Client

        msg = await util.get_message(ctx, message)
        if (msg == None):
            return
        emo = await util.get_emoji(ctx, emoji)
        if (emo == None):
            return

        await msg.add_reaction(emo)
        await ctx.send("reacted", ephemeral=True)

    @ react.autocomplete("emoji")
    async def get_emojis(self, ctx: interactions.AutocompleteContext):
        await util.get_emojis(ctx)
