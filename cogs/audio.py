import asyncio
import logging
import os
import random
import re
import string
import time
import typing

import interactions
import interactions.api.voice.audio
import youtube_dl

import util

logger = logging.getLogger(__name__)


class ProgressHook:
    def __init__(self, ctx: util.PsuedoContext, loop: asyncio.AbstractEventLoop) -> None:
        self.last_update = time.time()
        self.ctx = ctx
        self.loop = loop
        self.filename = ""

    def progress_hook(self, info: dict) -> None:
        self.filename = info["filename"]
        if info["status"] == "downloading" and time.time() - self.last_update < 2:
            return
        self.last_update = time.time()
        db = info["downloaded_bytes"]
        tb = info.get("total_bytes", round(info.get("total_bytes_estimate", 1)))
        ps = info.get("_percent_str", str(round(db/tb*100))+"%").strip()
        asyncio.run_coroutine_threadsafe(self.ctx.edit(content=f"downloading {db}/{tb} ({ps})..."), self.loop)


class Queue:
    def __init__(self) -> None:
        self.queue: list[tuple[util.PsuedoContext, interactions.TYPE_VOICE_CHANNEL, str, str, str]] = []
        self.run_lock = asyncio.Lock()

    async def add(self, url: str, ctx: util.PsuedoContext, channel: interactions.TYPE_VOICE_CHANNEL) -> None:
        await ctx.edit(content="downloading...")
        os.makedirs("audio", exist_ok=True)
        filename = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        hook = ProgressHook(ctx, asyncio.get_running_loop())
        ytdl = youtube_dl.YoutubeDL({"outtmpl": f"audio/{filename}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}], "progress_hooks": [hook.progress_hook], "noplaylist": True, "extract_flat": "in_playlist"})
        info = await asyncio.to_thread(ytdl.extract_info, url) or {}
        filename = re.sub(r"(?:\.\w+)+", ".mp3", hook.filename)
        assert filename, "not a video"
        self.queue.append((ctx, channel, filename, info["title"], url))
        await ctx.edit(content="queued")

    async def add_list(self, url: str, ctx: util.PsuedoContext, channel: interactions.TYPE_VOICE_CHANNEL) -> int:
        os.makedirs("audio", exist_ok=True)
        ytdl = youtube_dl.YoutubeDL({"outtmpl": f"audio/temp.%(ext)s", "extract_flat": True})
        info = await asyncio.to_thread(ytdl.extract_info, url) or {}
        assert "_type" in info and info["_type"] == "playlist", "not a playlist"
        msg = await ctx.send(content=f"found {len(info['entries'])} items")
        await ctx.send(content="downloading...")
        for i, video in enumerate(info["entries"]):
            await msg.edit(content=f"downloading playlist {i}/{len(info['entries'])}...")
            await self.add(video["url"], ctx, channel)
        await msg.edit(content="queued playlist")
        return len(info["entries"])

    async def run(self) -> None:
        async with self.run_lock:
            if not len(self.queue):
                return
            _, channel, filename, _, _ = self.queue.pop(0)

            if not channel.voice_state:
                await channel.connect()

            audio = interactions.api.voice.audio.AudioVolume(filename)
            if not isinstance(channel.voice_state, interactions.ActiveVoiceState):
                raise interactions.errors.BadArgument("lost access to voice channel")
            await channel.voice_state.play(audio)
            if not len(self.queue):
                await channel.disconnect()
            os.remove(filename)


class Audio(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")
        self.queue = Queue()

    @util.store_command("url")
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="play", sub_cmd_description="play audio from a YT url")
    async def play(self, ctx: interactions.SlashContext,
                   url: typing.Annotated[str, interactions.slash_str_option("link to the video", required=True)],
                   ) -> None:
        await util.preprocess(ctx)
        ctx2 = util.PsuedoContext(ctx)

        if not isinstance(ctx.author, interactions.Member):
            raise interactions.errors.BadArgument("command must be run in a guild channel")
        if not isinstance(ctx.author.voice, interactions.VoiceState):
            raise interactions.errors.BadArgument("please join a voice channel first")
        channel = ctx.author.voice.channel

        await self.queue.add(url, ctx2, channel)
        await self.queue.run()

    @util.store_command("url")
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="playlist", sub_cmd_description="play audio from a YT playlist url")
    async def playlist(self, ctx: interactions.SlashContext,
                       url: typing.Annotated[str, interactions.slash_str_option("link to the playlist", required=True)],
                       ) -> None:
        await util.preprocess(ctx)
        ctx2 = util.PsuedoContext(ctx)

        if not isinstance(ctx.author, interactions.Member):
            raise interactions.errors.BadArgument("command must be run in a guild channel")
        if not isinstance(ctx.author.voice, interactions.VoiceState):
            raise interactions.errors.BadArgument("please join a voice channel first")
        channel = ctx.author.voice.channel

        num = await self.queue.add_list(url, ctx2, channel)
        for _ in range(num):
            await self.queue.run()

    @util.store_command("stop")
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="skip", sub_cmd_description="stop the current audio")
    async def skip(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        if not isinstance(ctx.voice_state, interactions.ActiveVoiceState) or ctx.voice_state.stopped:
            raise interactions.errors.BadArgument("not currently playing")
        await ctx.voice_state.stop()
        await ctx.edit(content="skipped")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="clear", sub_cmd_description="remove all items from the queue")
    async def clear(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        self.queue.queue.clear()
        await ctx.send("cleared")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="queue", sub_cmd_description="view the current queue")
    async def view_queue(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        msg = ""
        for _, _, _, title, url in self.queue.queue:
            msg += f"[{title}](<{url}>)\n"
        await ctx.send(msg or "queue is empty")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="flush", sub_cmd_description="in case some audio is in the queue and is not playing, try this")
    async def flush(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        ctx2 = util.PsuedoContext(ctx)
        await ctx2.send(content="flushing...")
        while len(self.queue.queue):
            await self.queue.run()
        await ctx2.edit(content="flushed")
