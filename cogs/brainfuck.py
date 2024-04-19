import logging

import interactions

import util

logger = logging.getLogger(__name__)


# TODO
class Brainfuck(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.not_implemented_args, name="brainfuck")
    async def brainfuck(self, ctx: interactions.SlashContext) -> None:
        # 5D Brainfuck With Multiverse Time Travel
        await util.not_implemented(ctx)
