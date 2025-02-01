import logging
import typing
import warnings

import dateutil.parser
import dateutil.parser._parser
import interactions
import datetime
import util

from .timezones import tz

logger = logging.getLogger(__name__)


class Timezone(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="timezone", description="get a global timestamp for a datetime")
    async def timezone(self, ctx: interactions.SlashContext,
                       time: typing.Annotated[str, interactions.slash_str_option(description="preferred format: mm/dd/yyyy hh:mm:ss MM ZZ", required=True)],
                       ) -> None:
        await util.preprocess(ctx)
        msg = ""
        if (time == "now"):
            dt = datetime.datetime.now()
        else:
            try:
                warnings.filterwarnings("error", module="dateutil.parser._parser")
                dt = dateutil.parser.parse(time, tzinfos=tz.timezone_info)
            except dateutil.parser._parser.UnknownTimezoneWarning as e:
                msg = f"warning: {type(e)}\n"
                warnings.resetwarnings()
                dt = dateutil.parser.parse(time, tzinfos=tz.timezone_info)
            finally:
                warnings.resetwarnings()
        await ctx.send(f"{msg}{interactions.Timestamp.fromdatetime(dt)}({interactions.Timestamp.fromdatetime(dt).format(interactions.TimestampStyles.RelativeTime)})")
