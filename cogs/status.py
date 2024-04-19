import logging
import typing

import interactions

import util

logger = logging.getLogger(__name__)
allowed_bot_activities = {
    "playing": interactions.ActivityType.PLAYING,
    "streaming": interactions.ActivityType.STREAMING,
    "listening": interactions.ActivityType.LISTENING,
    "watching": interactions.ActivityType.WATCHING,
    "competing": interactions.ActivityType.COMPETING,
}


class Status(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="status", description="set bot activity")
    async def status(self, ctx: interactions.SlashContext,
                     activity: interactions.slash_str_option(description="activity name", required=True) = None,  # type: ignore
                     activity_type: interactions.slash_str_option(description="e.g. playing, streaming", required=True,  # type: ignore
                                                                  choices=[interactions.SlashCommandChoice(k, str(int(v))) for k, v in allowed_bot_activities.items()]) = None,
                     ) -> None:
        self.bot: interactions.Client
        activity: str
        activity_type: str
        await self.bot.change_presence(activity=interactions.Activity(activity, interactions.ActivityType(int(activity_type))))
        await ctx.send("updated status")
