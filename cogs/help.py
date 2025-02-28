import logging

import interactions

import util

logger = logging.getLogger(__name__)


class Help(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="help", description="list info about commands")
    async def help(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        msg = ""
        for name, keyword, description in util.all_commands:
            # TODO make a util function for this
            line = f"{name} ({keyword}): {description}\n"
            if len(msg + line) > 2000:
                await ctx.send(msg)
                msg = ""
            msg += line
        await ctx.send(msg)
