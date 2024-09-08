import logging
import typing
import warnings

import dateutil.parser
import dateutil.parser._parser
import dateutil.tz
import dateutil.utils
import dateutil.zoneinfo
import interactions

import util

from .timezones import tz

logger = logging.getLogger(__name__)


class Timezone(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="timezone", description="get a global timestamp for a datetime")
    async def timezone(self, ctx: interactions.SlashContext,
                       datetime: typing.Annotated[str, interactions.slash_str_option(description="preferred format: mm/dd/yyyy hh:mm:ss MM ZZ", required=True)],
                       ) -> None:
        await util.preprocess(ctx)
        msg = ""
        try:
            warnings.filterwarnings("error", module="dateutil.parser._parser")
            dt = dateutil.parser.parse(datetime, tzinfos=tz.timezone_info)
        except dateutil.parser._parser.UnknownTimezoneWarning as e:
            msg = f"warning: {type(e)}\nresults might not be accurate\n"
            warnings.resetwarnings()
            dt = dateutil.parser.parse(datetime, tzinfos=tz.timezone_info)
        finally:
            warnings.resetwarnings()
        await ctx.send(f"{msg}{interactions.Timestamp.fromdatetime(dt)}")
