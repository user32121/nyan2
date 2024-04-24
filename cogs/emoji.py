import logging
import typing

import interactions

import util

logger = logging.getLogger(__name__)


class Emoji(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="emoji", description="send emojis")
    async def emoji(self, ctx: interactions.SlashContext,
                    guild: typing.Annotated[typing.Optional[str], interactions.slash_str_option("the guild or \"all\"; defaults to the current guild")] = None,
                    emoji: typing.Annotated[str, interactions.slash_str_option("emoji to send; defaults to \"all\"", autocomplete=True)] = "all",
                    ) -> None:
        await util.preprocess(ctx)
        if (guild == "all"):
            guilds = ctx.bot.guilds
        elif (guild == None):
            if (ctx.guild == None):
                await ctx.send("not in a guild")
                return
            guilds = [ctx.guild]
        else:
            guilds = [await interactions.GuildConverter().convert(ctx, guild)]
        if (emoji != "all"):
            e = await util.get_emoji(ctx, emoji)
            await ctx.send(str(e))
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
