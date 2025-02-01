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

    @util.store_command()
    @interactions.slash_command(** util.command_args, name="earrape", description="make stuff very loud")
    async def earrape(self, ctx: interactions.SlashContext,
                      file: typing.Annotated[interactions.Attachment, interactions.slash_attachment_option("the file to modify", True)],
                      gain: typing.Annotated[int, interactions.slash_int_option("the amount to increase by, default: 10")] = 10,
                      ) -> None:
        await util.preprocess(ctx)
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
