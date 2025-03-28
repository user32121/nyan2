import datetime
import logging
import typing

import interactions

import util

logger = logging.getLogger(__name__)


class Relative(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="duration", description="display a timestamp relative to the current time")
    async def duration(self, ctx: interactions.SlashContext,
                       number: typing.Annotated[int, interactions.slash_float_option(description="the number of time units", required=True)],
                       unit: typing.Annotated[str, interactions.slash_str_option(description="the unit of time", required=True, choices=util.as_choices(["seconds", "minutes", "hours", "days", "weeks"]))],
                       ) -> None:
        await util.preprocess(ctx)
        dt = datetime.datetime.now()
        dt += datetime.timedelta(**{unit: number})
        await ctx.send(f"{interactions.Timestamp.fromdatetime(dt)}({interactions.Timestamp.fromdatetime(dt).format(interactions.TimestampStyles.RelativeTime)})")
