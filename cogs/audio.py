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


class Audio(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")
        self.queue = []

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="play", sub_cmd_description="play audio from a YT url")
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

        ctx2 = util.PsuedoContext(ctx)
        await ctx2.send(content="downloading...")
        hook = ProgressHook()
        os.makedirs("audio", exist_ok=True)
        ytdl = youtube_dl.YoutubeDL({"outtmpl": "audio/%(id)s.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}], "progress_hooks": [hook.progress_hook]})
        ytdl.download([url])

        filename = re.sub(r"(?:\.\w+)+", ".mp3", hook.filename)
        audio = interactions.api.voice.audio.AudioVolume(filename)
        if not isinstance(ctx2.ctx.guild, interactions.Guild) or not isinstance(ctx2.ctx.guild.voice_state, interactions.ActiveVoiceState):
            raise interactions.errors.BadArgument("lost access to voice channel")
        if ctx2.ctx.guild.voice_state.playing:
            await ctx2.edit(content="waiting for previous audio to finish...")
            await ctx2.ctx.guild.voice_state.wait_for_stopped()
        await ctx2.edit(content="playing...")
        await ctx2.ctx.guild.voice_state.play(audio)

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="audio", description="voice channel audio commands", sub_cmd_name="skip", sub_cmd_description="stop the current audio")
    async def skip(self, ctx: interactions.SlashContext) -> None:
        await util.preprocess(ctx)
        if not isinstance(ctx.voice_state, interactions.ActiveVoiceState):
            raise interactions.errors.BadArgument("not currently playing")
        await ctx.voice_state.stop()
        await ctx.edit(content="skipped")
