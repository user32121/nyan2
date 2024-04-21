import io
import logging
import tempfile
import typing

import interactions
import pydub
import requests

import util

logger = logging.getLogger(__name__)


class Earrape(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="earrape")
    async def earrape(self, ctx: interactions.SlashContext,
                      file: interactions.slash_attachment_option("the file to modify", True),  # type: ignore
                      gain: interactions.slash_int_option("the amount to increase by") = 10,  # type: ignore
                      ) -> None:
        await ctx.defer()
        res = requests.get(file.proxy_url)
        with io.BytesIO(res.content) as f:
            try:
                audio: pydub.AudioSegment = pydub.AudioSegment.from_file(f)
            except IndexError as e:
                await ctx.send("unable to read audio file")
                logger.info(e)
                return
            audio = audio.apply_gain(gain)
        with typing.cast(tempfile._TemporaryFileWrapper, audio.export()) as f:
            await ctx.send(file=interactions.File(typing.cast(io.IOBase, f.file), file_name="file.mp3"))
