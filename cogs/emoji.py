import logging
import time

import interactions

import util

logger = logging.getLogger(__name__)


# TODO send only one emoji
class Emoji(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="emoji", description="send emojis")
    async def emoji(self, ctx: interactions.SlashContext,
                    guild: interactions.slash_str_option("the id of the guild or \"all\"; defaults to the current guild") = None,  # type: ignore
                    emoji: interactions.slash_str_option("emoji to send; defaults to \"all\"", autocomplete=True) = "all",  # type: ignore
                    ) -> None:
        if (guild == "all"):
            guilds = ctx.bot.guilds
        elif (guild == None):
            if (ctx.guild == None):
                await ctx.send("not in a guild")
                return
            guilds = [ctx.guild]
        else:
            guild = await util.get_guild(ctx, guild)
            if (guild == None):
                return
            guilds = [guild]
        if (emoji != "all"):
            emo = await util.get_emoji(ctx, emoji)
            if(emo == None):
                return
            await ctx.send(str(emo))
            return

        msg = ""
        prev_msg = ""
        for g in guilds:
            for e in await g.fetch_all_custom_emojis():
                prev_msg = msg
                msg += str(e)
                if (len(msg) > 2000):
                    await ctx.send(prev_msg)
                    msg = str(e)
        await ctx.send(msg)

    @emoji.autocomplete("emoji")
    async def get_emojis(self, ctx: interactions.AutocompleteContext):
        await util.get_emojis(ctx)
