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
        self.bot: interactions.Client

        if (ctx.guild == None):
            await ctx.send("not in a guild")
            return
        try:
            message = int(message)
        except ValueError as e:
            await ctx.send("invalid message id")
            logger.info(e)
            return
        msg = await ctx.channel.fetch_message(message)
        msg: interactions.Message | None
        if (msg == None):
            await ctx.send("could not find message")
            return
        try:
            sfs = emoji.split(",")
            emoji = int(sfs[0]), int(sfs[1])
        except (IndexError, ValueError):
            sfs = None
            for g in self.bot.guilds:
                for e in await g.fetch_all_custom_emojis():
                    if (e.name == emoji):
                        sfs = e.id, g.id
                        logger.info(sfs)
            if (sfs == None):
                await ctx.send("invalid emoji")
                logger.info(e)
                return
            emoji = sfs
        emoji = await self.bot.fetch_custom_emoji(*emoji)
        if (emoji == None):
            await ctx.send("could not find emoji")
            return

        await ctx.guild.fetch_all_custom_emojis()
        logger.info(emoji)
        await msg.add_reaction(emoji)
        await ctx.send("reacted", ephemeral=True)

    @ react.autocomplete("emoji")
    async def get_emojis(self, ctx: interactions.AutocompleteContext):
        start = time.time()
        ret = []
        for g in self.bot.guilds:
            if (time.time() - start > 2.5 or len(ret) >= 25):
                break
            emojis = await g.fetch_all_custom_emojis()
            for e in emojis:
                if (e.name != None and ctx.input_text.lower() in e.name.lower()):
                    ret.append(interactions.SlashCommandChoice(e.name, f"{e.id},{g.id}"))
                    if (len(ret) >= 25):
                        break
        await ctx.send(ret)
