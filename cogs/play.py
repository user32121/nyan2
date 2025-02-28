import logging
import os
import re
import typing

import interactions
import interactions.api.voice.audio
import youtube_dl

import util

logger = logging.getLogger(__name__)


class ProgressHook():
    def progress_hook(self, info):
        self.filename = info["filename"]


class Play(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="play", description="play audio from YT", sub_cmd_name="url", sub_cmd_description="play audio from a YT url")
    async def play(self, ctx: interactions.SlashContext,
                   url: typing.Annotated[str, interactions.slash_str_option("link to the video", required=True)],
                   ) -> None:
        await util.preprocess(ctx)

        if not ctx.voice_state:
            if not isinstance(ctx.author, interactions.Member):
                raise interactions.errors.BadArgument("command must be run in a guild channel")
            if not isinstance(ctx.author.voice, interactions.VoiceState):
                raise interactions.errors.BadArgument("please join a voice channel first")
            await ctx.author.voice.channel.connect()

        await ctx.send("downloading...")
        hook = ProgressHook()
        os.makedirs("audio", exist_ok=True)
        ytdl = youtube_dl.YoutubeDL({"outtmpl": "audio/%(id)s.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}], "progress_hooks": [hook.progress_hook]})
        ytdl.download([url])

        await ctx.edit(content="playing...")
        if not isinstance(ctx.voice_state, interactions.ActiveVoiceState):
            raise interactions.errors.BadArgument("lost access to voice channel")
        filename = re.sub(r"(?:\.\w+)+", ".mp3", hook.filename)
        logger.info(filename)
        audio = interactions.api.voice.audio.AudioVolume(filename)
        await ctx.voice_state.play(audio)
