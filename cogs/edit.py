import asyncio
import logging
import multiprocessing
import typing

import interactions

import util

from .edits import animated, basic, blur, image_io, misc

logger = logging.getLogger(__name__)

base_command = interactions.SlashCommand(**util.command_args, name="edit", description="various image edits")
basic_group = base_command.group("basic", "simple edits")
blur_group = base_command.group("blur", "various blur effects")
animated_group = base_command.group("animated", "effects that make gifs")
misc_group = base_command.group("misc", "miscellaneous effects")


def slash_colour_option(required):
    return interactions.slash_str_option("the colour to apply (see PIL's getrgb() for technical details)", required=required)


file_option = typing.Annotated[interactions.Attachment, interactions.slash_attachment_option("the image to edit", True)]
required_colour_option = typing.Annotated[tuple[int, int, int, int], basic.ColourConverter, slash_colour_option(required=True)]
colour_option = typing.Annotated[tuple[int, int, int, int], basic.ColourConverter, slash_colour_option(required=False)]


# TODO make all subcommands multiprocess/async?
class Edit(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @basic_group.subcommand(sub_cmd_name="red", sub_cmd_description="isolate the red component")
    async def red(self, ctx: interactions.SlashContext,
                  file: file_option,
                  ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.multiply(img, (255, 0, 0, 255))
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="green", sub_cmd_description="isolate the green component")
    async def green(self, ctx: interactions.SlashContext,
                    file: file_option,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.multiply(img, (0, 255, 0, 255))
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="blue", sub_cmd_description="isolate the blue component")
    async def blue(self, ctx: interactions.SlashContext,
                   file: file_option,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.multiply(img, (0, 0, 255, 255))
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="hsv_hue", sub_cmd_description="isolate the HSV hue")
    async def hue(self, ctx: interactions.SlashContext,
                  file: file_option,
                  ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.hsv_hue(img)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="hsv_saturation", sub_cmd_description="isolate the HSV saturation")
    async def saturation(self, ctx: interactions.SlashContext,
                         file: file_option,
                         ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.hsv_saturation(img)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="hsv_value", sub_cmd_description="isolate the HSV value")
    async def value(self, ctx: interactions.SlashContext,
                    file: file_option,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.hsv_value(img)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="invert", sub_cmd_description="invert")
    async def invert(self, ctx: interactions.SlashContext,
                     file: file_option,
                     ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.invert(img)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="tint", sub_cmd_description="average with a colour")
    async def tint(self, ctx: interactions.SlashContext,
                   file: file_option,
                   colour: required_colour_option,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.tint(img, colour)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="multiply", sub_cmd_description="multiply by a colour")
    async def multiply(self, ctx: interactions.SlashContext,
                       file: file_option,
                       colour: required_colour_option,
                       ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.multiply(img, colour)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="grid", sub_cmd_description="display a grid for easier finding of coordinates")
    async def grid(self, ctx: interactions.SlashContext,
                   file: file_option,
                   thickness: typing.Annotated[int, interactions.slash_int_option("line thickness, in pixels")] = 1,
                   colour: colour_option = (0, 0, 0, 255),
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.grid(img, thickness, colour)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="text", sub_cmd_description="add text")
    async def text(self, ctx: interactions.SlashContext,
                   file: file_option,
                   caption: typing.Annotated[str, interactions.slash_str_option(r"text to put on the image, separated by a ','. Escape with '\' to avoid splitting", True)],
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = basic.add_caption(img, caption)
        await image_io.send_file(ctx, img)

    @blur_group.subcommand(sub_cmd_name="blur", sub_cmd_description="apply a gaussian blur")
    async def blur(self, ctx: interactions.SlashContext,
                   file: file_option,
                   radius: typing.Annotated[float, interactions.slash_float_option("in pixels")] = 5,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = blur.gaussianblur(img, radius)
        await image_io.send_file(ctx, img)

    @blur_group.subcommand(sub_cmd_name="motionblur", sub_cmd_description="apply a motion blur")
    async def motionblur(self, ctx: interactions.SlashContext,
                         file: file_option,
                         length: typing.Annotated[int, interactions.slash_int_option("in pixels")] = 10,
                         angle: typing.Annotated[float, interactions.slash_float_option("counter clockwise from the x axis, in degrees")] = 30,
                         ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = blur.motionblur(img, length, angle)
        await image_io.send_file(ctx, img)

    @blur_group.subcommand(sub_cmd_name="zoomblur", sub_cmd_description="apply a zoom blur")
    async def zoomblur(self, ctx: interactions.SlashContext,
                       file: file_option,
                       zoom: typing.Annotated[float, interactions.slash_float_option("zoom multiplier")] = 1.1,
                       interpolation: typing.Annotated[int, interactions.slash_int_option("number of interpolated values; more means higher quality, but slower", min_value=1)] = 30,
                       ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = blur.zoomblur(img, zoom, interpolation)
        await image_io.send_file(ctx, img)

    @blur_group.subcommand(sub_cmd_name="circularblur", sub_cmd_description="apply a circular blur")
    async def circularblur(self, ctx: interactions.SlashContext,
                           file: file_option,
                           angle: typing.Annotated[float, interactions.slash_float_option("in degrees")] = 15,
                           interpolation: typing.Annotated[int, interactions.slash_int_option("number of interpolated values; more means higher quality, but slower", min_value=1)] = 30,
                           ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = blur.circularblur(img, angle, interpolation)
        await image_io.send_file(ctx, img)

    @animated_group.subcommand(sub_cmd_name="boom", sub_cmd_description="explosion")
    async def boom(self, ctx: interactions.SlashContext,
                   file: file_option,
                   delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 50,
                   frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 10,
                   amount: typing.Annotated[float, interactions.slash_float_option("strength")] = 2,
                   center_x: typing.Annotated[float, interactions.slash_float_option("normalized to [-1,1]")] = 0,
                   center_y: typing.Annotated[float, interactions.slash_float_option("normalized to [-1,1]")] = 0,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = animated.boom(img, delay, frames, amount, center_x, center_y)
        await image_io.send_file(ctx, img)

    @animated_group.subcommand(sub_cmd_name="rave", sub_cmd_description="apply a hue shift that changes with time")
    async def rave(self, ctx: interactions.SlashContext,
                   file: file_option,
                   delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 100,
                   frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 18,
                   cycles: typing.Annotated[float, interactions.slash_float_option("number of cycles per gif loop")] = 1,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = animated.hueshift(img, delay, frames, cycles, 0, 0)
        await image_io.send_file(ctx, img)

    @animated_group.subcommand(sub_cmd_name="rainbow", sub_cmd_description="apply a hue shift that changes with time and position")
    async def rainbow(self, ctx: interactions.SlashContext,
                      file: file_option,
                      delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 100,
                      frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 18,
                      cycles: typing.Annotated[float, interactions.slash_float_option("number of cycles per gif loop")] = 1,
                      scale_x: typing.Annotated[float, interactions.slash_float_option("closeness of vertical stripes")] = 1,
                      scale_y: typing.Annotated[float, interactions.slash_float_option("closeness of horizontal stripes")] = 1,
                      ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = animated.hueshift(img, delay, frames, cycles, scale_x, scale_y)
        await image_io.send_file(ctx, img)

    @animated_group.subcommand(sub_cmd_name="spin", sub_cmd_description="stretch the center around")
    async def spin(self, ctx: interactions.SlashContext,
                   file: file_option,
                   delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 50,
                   frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 5,
                   cycles: typing.Annotated[float, interactions.slash_float_option("number of cycles per gif loop")] = 1,
                   radius: typing.Annotated[float, interactions.slash_float_option("strength of the offset, normalized")] = 0.5,
                   center_x: typing.Annotated[float, interactions.slash_float_option("normalized to [-1,1]")] = 0,
                   center_y: typing.Annotated[float, interactions.slash_float_option("normalized to [-1,1]")] = 0,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = animated.spin(img, delay, frames, cycles, radius, center_x, center_y)
        await image_io.send_file(ctx, img)

    @animated_group.subcommand(sub_cmd_name="squish", sub_cmd_description="stretch horizontally and vertically")
    async def squish(self, ctx: interactions.SlashContext,
                     file: file_option,
                     delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 100,
                     frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 5,
                     cycles: typing.Annotated[float, interactions.slash_float_option("number of cycles per gif loop")] = 1,
                     amount: typing.Annotated[float, interactions.slash_float_option("stretch multiplier")] = 1,
                     ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = animated.squish(img, delay, frames, cycles, amount)
        await image_io.send_file(ctx, img)

    @misc_group.subcommand(sub_cmd_name="snap", sub_cmd_description="swap pixels around")
    async def snap(self, ctx: interactions.SlashContext,
                   file: file_option,
                   steps: typing.Annotated[float, interactions.slash_float_option("approximate number of steps, normalized (multiplied by number of pixels)", min_value=0)] = 2,
                   fuzzy: typing.Annotated[bool, interactions.slash_bool_option("whether to blend or swap pixels")] = False,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = misc.snap(img, steps, fuzzy)
        await image_io.send_file(ctx, img)

    @misc_group.subcommand(sub_cmd_name="magic", sub_cmd_description="spread out pixels")
    async def magic(self, ctx: interactions.SlashContext,
                    file: file_option,
                    steps: typing.Annotated[float, interactions.slash_float_option("approximate number of steps, normalized (multiplied by number of pixels)", min_value=0)] = 2,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = misc.magic(img, steps)
        await image_io.send_file(ctx, img)

    @misc_group.subcommand(sub_cmd_name="bulge", sub_cmd_description="add a bulge")
    async def bulge(self, ctx: interactions.SlashContext,
                    file: file_option,
                    amount: typing.Annotated[float, interactions.slash_float_option("strength")] = 1,
                    center_x: typing.Annotated[float, interactions.slash_float_option("normalized to [-1,1]")] = 0,
                    center_y: typing.Annotated[float, interactions.slash_float_option("normalized to [-1,1]")] = 0,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = misc.bulge(img, amount, center_x, center_y)
        await image_io.send_file(ctx, img)

    @misc_group.subcommand(sub_cmd_name="upscale", sub_cmd_description="double the image size using Waifu2x")
    async def upscale(self, ctx: interactions.SlashContext,
                      file: file_option,
                      ) -> None:
        # TODO upload to tmpfiles if too large
        await util.preprocess(ctx)
        msg = await ctx.send("processing...")
        img = image_io.from_url(file.proxy_url)
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=misc.upscale_multiprocess, args=(img, q))
        p.start()
        while (p.is_alive() and q.empty()):
            await asyncio.sleep(10)
        if (q.empty()):
            raise RuntimeError(f"subprocess exited with code {p.exitcode}")
        img = q.get(block=False)
        f, ext = image_io.to_file(img)
        # processing may take longer than 15 minutes (allotted defer time) so we reply to the message instead
        await msg.reply(file=interactions.File(f.file, f"file.{ext}"))  # type: ignore

    @misc_group.subcommand(sub_cmd_name="downscale", sub_cmd_description="half the image size")
    async def downscale(self, ctx: interactions.SlashContext,
                        file: file_option,
                        ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        img = misc.downscale(img)
        await image_io.send_file(ctx, img)

    @misc_group.subcommand(sub_cmd_name="random", sub_cmd_description="not implemented")
    async def random(self, ctx: interactions.SlashContext,
                     file: file_option,
                     ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="repeat", sub_cmd_description="not implemented")
    async def repeat(self, ctx: interactions.SlashContext,
                     file: file_option,
                     ) -> None:
        await util.not_implemented(ctx)
