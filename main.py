import datetime
import logging
import typing

import interactions

import secret
import util

util.configure_logger()
logger = logging.getLogger(__name__)

bot = interactions.Client(
    intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT,
)


@interactions.listen()
async def on_ready():
    logger.info("Bot ready")
    await bot.change_presence(activity=interactions.Activity(f"uptime since {datetime.datetime.now(datetime.timezone.utc)}", interactions.ActivityType.WATCHING))


@interactions.listen()
async def on_command_error(event: interactions.events.CommandError):
    ctx: interactions.SlashContext = typing.cast(interactions.SlashContext, event.ctx)
    err = event.error
    if isinstance(err, interactions.errors.Forbidden):
        await ctx.send("bot is missing permissions")


@interactions.listen()
async def on_message_create(event: interactions.events.MessageCreate):
    if (event.message.content.startswith("nyan ")):
        # await event.message.reply("Nyan is moving to slash commands")
        pass

bot.load_extensions("cogs")

bot.start(secret.BOT_TOKEN)
