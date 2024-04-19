import logging

import interactions

import util

logger = logging.getLogger(__name__)


class Emoji(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="emoji", description="sends all of a guild's emojis")
    async def emoji(self, ctx: interactions.SlashContext,
                    guild: interactions.slash_str_option("the id of the guild, or \"all\", or omit for the current guild") = None,  # type: ignore
                    ) -> None:
        if (guild == "all"):
            guilds = ctx.bot.guilds
        else:
            guild = guild or ctx.guild_id
            try:
                guild = int(guild)
            except ValueError as e:
                await ctx.send("invalid guild")
                logger.info(e)
                return
            guild = await ctx.bot.fetch_guild(guild)
            if (guild == None):
                await ctx.send("could not find guild")
                return
            guilds = [guild]

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
