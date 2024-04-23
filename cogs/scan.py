import asyncio
import logging
import time

import interactions

import util

logger = logging.getLogger(__name__)


class Scan(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="scan", description="preload all messages from a channel for faster searching")
    async def scan(self, ctx: interactions.SlashContext,
                   ) -> None:
        await util.preprocess(ctx)
        await fill_cache(ctx.bot, ctx.channel, ctx)
        await ctx.send("finished scan")


cache_locks: dict[int, asyncio.Lock] = {}
most_recent_cached: dict[int, int] = {}
message_cache: dict[int, list[tuple[int, int, str]]] = {}


async def fill_cache(bot: interactions.Client, channel: interactions.TYPE_MESSAGEABLE_CHANNEL, ctx_updates: interactions.SlashContext):
    await ctx_updates.send("preparing to fill cache")
    await asyncio.sleep(1)

    if (channel.id not in cache_locks):
        cache_locks[channel.id] = asyncio.Lock()
    if (cache_locks[channel.id].locked()):
        await ctx_updates.edit(content="another command is currently filling the cache")
    await cache_locks[channel.id].acquire()

    if (channel.id not in message_cache):
        message_cache[channel.id] = []
    await ctx_updates.edit(content=f"filling cache: {len(message_cache[channel.id])} messages")
    last_updated = time.time()

    is_newest_message = True
    async for m in channel.history(limit=0, after=most_recent_cached.get(channel.id, None)):
        m: interactions.Message
        if (is_newest_message):
            most_recent_cached[channel.id] = m.id
            is_newest_message = False
        if (time.time() - last_updated >= 5):
            await ctx_updates.edit(content=f"filling cache: {len(message_cache[channel.id])} messages")
            last_updated = time.time()
        message_cache[channel.id].append((m.id, m.author.id, m.content))
    await ctx_updates.edit(content=f"finished filling cache: {len(message_cache[channel.id])} messages")
    cache_locks[channel.id].release()
