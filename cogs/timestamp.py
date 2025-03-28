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


class Timestamp(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="timestamp", description="display a date and time using a Discord timestamp")
    async def timestamp(self, ctx: interactions.SlashContext,
                       time: typing.Annotated[str, interactions.slash_str_option(description="preferred format: mm/dd/yyyy hh:mm:ss am/pm timezone", required=True)],
                       ) -> None:
        await util.preprocess(ctx)
        msg = ""
        time = time.upper()
        if (time == "NOW"):
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
