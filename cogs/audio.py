import logging
import os
import string
import re
import typing
import random
import asyncio

import interactions
import interactions.api.voice.audio
import youtube_dl

import util

logger = logging.getLogger(__name__)


class ProgressHook:
    def progress_hook(self, info):
        # TODO status update
        self.filename = info["filename"]


class Queue:
    def __init__(self) -> None:
        self.queue: list[tuple[str, util.PsuedoContext, interactions.TYPE_VOICE_CHANNEL]] = []
        self.run_lock = asyncio.Lock()

    async def add(self, url: str, ctx: util.PsuedoContext, channel: interactions.TYPE_VOICE_CHANNEL) -> None:
        await ctx.edit(content="downloading...")
        os.makedirs("audio", exist_ok=True)
        filename = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        hook = ProgressHook()
        ytdl = youtube_dl.YoutubeDL({"outtmpl": f"audio/{filename}.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}], "progress_hooks": [hook.progress_hook]})
        await asyncio.to_thread(ytdl.download, [url])
        filename = re.sub(r"(?:\.\w+)+", ".mp3", hook.filename)
        self.queue.append((filename, ctx, channel))
        await ctx.edit(content="queued")

    async def run(self) -> None:
        async with self.run_lock:
            filename, ctx, channel = self.queue.pop(0)

            if not channel.voice_state:
                await channel.connect()

            audio = interactions.api.voice.audio.AudioVolume(filename)
            if not isinstance(channel.voice_state, interactions.ActiveVoiceState):
                raise interactions.errors.BadArgument("lost access to voice channel")
            await channel.voice_state.play(audio)
            # TODO remove file when done
            if not len(self.queue):
                await channel.disconnect()


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

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="skip", sub_cmd_description="stop the current audio")
    async def skip(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        if not isinstance(ctx.voice_state, interactions.ActiveVoiceState) or ctx.voice_state.stopped:
            raise interactions.errors.BadArgument("not currently playing")
        await ctx.voice_state.stop()
        await ctx.edit(content="skipped")
