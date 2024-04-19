import logging

import interactions

import util

logger = logging.getLogger(__name__)


# TODO
class Nyons(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.not_implemented_args, name="nyons")
    async def nyons(self, ctx: interactions.SlashContext) -> None:
        await util.not_implemented(ctx)

# nyons
# beg
# give
# highlow
# roll
# slots
# stats
# daily
# rob
