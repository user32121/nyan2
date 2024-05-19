import logging
import typing

import interactions

import util

from .edits import animated, basic, blur, image_io, meta, misc
from .edits import util as edit_util

logger = logging.getLogger(__name__)

base_command = interactions.SlashCommand(**util.command_args, name="edit", description="various image edits")
basic_group = base_command.group("basic", "simple edits")
blur_group = base_command.group("blur", "various blur effects")
animated_group = base_command.group("animated", "effects that make gifs")
misc_group = base_command.group("misc", "miscellaneous effects")
meta_group = base_command.group("meta", "edits that use other edits")


def slash_colour_option(required):
    return interactions.slash_str_option("the colour to apply (see PIL's getrgb() for technical details)", required=required)


file_option = typing.Annotated[interactions.Attachment, interactions.slash_attachment_option("the image to edit", True)]
required_colour_option = typing.Annotated[edit_util.ColourType, edit_util.ColourConverter, slash_colour_option(required=True)]
colour_option = typing.Annotated[edit_util.ColourType, edit_util.ColourConverter, slash_colour_option(required=False)]
coord_x_option = typing.Annotated[float, edit_util.makeCoordConverter(False), interactions.slash_float_option("in the range [0, 1], positive is rightward")]
coord_y_option = typing.Annotated[float, edit_util.makeCoordConverter(True), interactions.slash_float_option("in the range [0, 1], positive is upward")]


class Edit(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")
        self.last_img: typing.Optional[list[edit_util.ImageFrame]] = None
        self.last_edit: typing.Optional[edit_util.ImageEditType] = None
        self.last_args: typing.Optional[tuple] = None
        self.last_send_args: typing.Optional[dict[str, typing.Any]] = None

    @basic_group.subcommand(sub_cmd_name="red", sub_cmd_description="isolate the red component")
    async def red(self, ctx: interactions.SlashContext,
                  file: file_option,
                  ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ((255, 0, 0, 255),)
        img = await edit_util.run_in_subprocess(ctx, basic.multiply, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.multiply, args, {}

    @basic_group.subcommand(sub_cmd_name="green", sub_cmd_description="isolate the green component")
    async def green(self, ctx: interactions.SlashContext,
                    file: file_option,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ((0, 255, 0, 255),)
        img = await edit_util.run_in_subprocess(ctx, basic.multiply, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.multiply, args, {}

    @basic_group.subcommand(sub_cmd_name="blue", sub_cmd_description="isolate the blue component")
    async def blue(self, ctx: interactions.SlashContext,
                   file: file_option,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ((0, 0, 255, 255),)
        img = await edit_util.run_in_subprocess(ctx, basic.multiply, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.multiply, args, {}

    @basic_group.subcommand(sub_cmd_name="hsv_hue", sub_cmd_description="isolate the HSV hue")
    async def hue(self, ctx: interactions.SlashContext,
                  file: file_option,
                  ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ()
        img = await edit_util.run_in_subprocess(ctx, basic.hsv_hue, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.hsv_hue, args, {}

    @basic_group.subcommand(sub_cmd_name="hsv_saturation", sub_cmd_description="isolate the HSV saturation")
    async def saturation(self, ctx: interactions.SlashContext,
                         file: file_option,
                         ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ()
        img = await edit_util.run_in_subprocess(ctx, basic.hsv_saturation, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.hsv_saturation, args, {}

    @basic_group.subcommand(sub_cmd_name="hsv_value", sub_cmd_description="isolate the HSV value")
    async def value(self, ctx: interactions.SlashContext,
                    file: file_option,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ()
        img = await edit_util.run_in_subprocess(ctx, basic.hsv_value, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.hsv_value, args, {}

    @basic_group.subcommand(sub_cmd_name="invert", sub_cmd_description="invert")
    async def invert(self, ctx: interactions.SlashContext,
                     file: file_option,
                     ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ()
        img = await edit_util.run_in_subprocess(ctx, basic.invert, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.invert, args, {}

    @basic_group.subcommand(sub_cmd_name="tint", sub_cmd_description="average with a colour")
    async def tint(self, ctx: interactions.SlashContext,
                   file: file_option,
                   colour: required_colour_option,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (colour,)
        img = await edit_util.run_in_subprocess(ctx, basic.tint, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.tint, args, {}

    @basic_group.subcommand(sub_cmd_name="multiply", sub_cmd_description="multiply by a colour")
    async def multiply(self, ctx: interactions.SlashContext,
                       file: file_option,
                       colour: required_colour_option,
                       ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (colour,)
        img = await edit_util.run_in_subprocess(ctx, basic.multiply, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.multiply, args, {}

    @basic_group.subcommand(sub_cmd_name="grid", sub_cmd_description="display a grid for easier finding of coordinates")
    async def grid(self, ctx: interactions.SlashContext,
                   file: file_option,
                   thickness: typing.Annotated[int, interactions.slash_int_option("line thickness, in pixels")] = 1,
                   colour: colour_option = (0, 0, 0, 255),
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (thickness, colour)
        img = await edit_util.run_in_subprocess(ctx, basic.grid, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.grid, args, {}

    @basic_group.subcommand(sub_cmd_name="text", sub_cmd_description="add text")
    async def text(self, ctx: interactions.SlashContext,
                   file: file_option,
                   caption: typing.Annotated[str, interactions.slash_str_option(r"text to put on the image, separated by a ','. Escape with '\' to avoid splitting", True)],
                   font_size: typing.Annotated[int, interactions.slash_float_option("relative size of caption")] = 1,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (caption, font_size)
        img = await edit_util.run_in_subprocess(ctx, basic.add_caption, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, basic.add_caption, args, {}

    @blur_group.subcommand(sub_cmd_name="blur", sub_cmd_description="apply a gaussian blur")
    async def blur(self, ctx: interactions.SlashContext,
                   file: file_option,
                   radius: typing.Annotated[float, interactions.slash_float_option("in pixels")] = 5,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (radius,)
        img = await edit_util.run_in_subprocess(ctx, blur.gaussianblur, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, blur.gaussianblur, args, {}

    @blur_group.subcommand(sub_cmd_name="motionblur", sub_cmd_description="apply a motion blur")
    async def motionblur(self, ctx: interactions.SlashContext,
                         file: file_option,
                         length: typing.Annotated[int, interactions.slash_int_option("in pixels")] = 10,
                         angle: typing.Annotated[float, interactions.slash_float_option("counter clockwise from the x axis, in degrees")] = 30,
                         ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (length, angle)
        img = await edit_util.run_in_subprocess(ctx, blur.motionblur, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, blur.motionblur, args, {}

    @blur_group.subcommand(sub_cmd_name="zoomblur", sub_cmd_description="apply a zoom blur")
    async def zoomblur(self, ctx: interactions.SlashContext,
                       file: file_option,
                       zoom: typing.Annotated[float, interactions.slash_float_option("zoom multiplier")] = 1.1,
                       interpolation: typing.Annotated[int, interactions.slash_int_option("number of interpolated values; more means higher quality, but slower", min_value=1)] = 30,
                       ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (zoom, interpolation)
        img = await edit_util.run_in_subprocess(ctx, blur.zoomblur, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, blur.zoomblur, args, {}

    @blur_group.subcommand(sub_cmd_name="circularblur", sub_cmd_description="apply a circular blur")
    async def circularblur(self, ctx: interactions.SlashContext,
                           file: file_option,
                           angle: typing.Annotated[float, interactions.slash_float_option("in degrees")] = 15,
                           interpolation: typing.Annotated[int, interactions.slash_int_option("number of interpolated values; more means higher quality, but slower", min_value=1)] = 30,
                           ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (angle, interpolation)
        img = await edit_util.run_in_subprocess(ctx, blur.circularblur, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, blur.circularblur, args, {}

    @animated_group.subcommand(sub_cmd_name="boom", sub_cmd_description="explosion")
    async def boom(self, ctx: interactions.SlashContext,
                   file: file_option,
                   delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 50,
                   frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 10,
                   amount: typing.Annotated[float, interactions.slash_float_option("strength")] = 2,
                   center_x: coord_x_option = 0.5,
                   center_y: coord_y_option = 0.5,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (delay, frames, amount, center_x, center_y)
        img = await edit_util.run_in_subprocess(ctx, animated.boom, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, animated.boom, args, {}

    @animated_group.subcommand(sub_cmd_name="rave", sub_cmd_description="apply a hue shift that changes with time")
    async def rave(self, ctx: interactions.SlashContext,
                   file: file_option,
                   delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 100,
                   frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 18,
                   cycles: typing.Annotated[float, interactions.slash_float_option("number of cycles per gif loop")] = 1,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (delay, frames, cycles, 0, 0)
        img = await edit_util.run_in_subprocess(ctx, animated.hueshift, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, animated.hueshift, args, {}

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
        args = (delay, frames, cycles, scale_x, scale_y)
        img = await edit_util.run_in_subprocess(ctx, animated.hueshift, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, animated.hueshift, args, {}

    @animated_group.subcommand(sub_cmd_name="spin", sub_cmd_description="stretch the center around")
    async def spin(self, ctx: interactions.SlashContext,
                   file: file_option,
                   delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 50,
                   frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 5,
                   cycles: typing.Annotated[float, interactions.slash_float_option("number of cycles per gif loop")] = 1,
                   radius: typing.Annotated[float, interactions.slash_float_option("strength of the offset, normalized")] = 0.5,
                   center_x: coord_x_option = 0.5,
                   center_y: coord_y_option = 0.5,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (delay, frames, cycles, radius, center_x, center_y)
        img = await edit_util.run_in_subprocess(ctx, animated.spin, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, animated.spin, args, {}

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
        args = (delay, frames, cycles, amount)
        img = await edit_util.run_in_subprocess(ctx, animated.squish, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, animated.squish, args, {}

    @animated_group.subcommand(sub_cmd_name="ash", sub_cmd_description="make images turn to ashes")
    async def ash(self, ctx: interactions.SlashContext,
                  file: file_option,
                  delay: typing.Annotated[int, interactions.slash_int_option("delay between frames if one is not already present, in milliseconds", min_value=0)] = 50,
                  frames: typing.Annotated[int, interactions.slash_int_option("number of frames to create if input is a static image", min_value=1)] = 50,
                  time_steps: typing.Annotated[float, interactions.slash_float_option("units of time to simulate")] = 3,
                  spread_delay: typing.Annotated[float, interactions.slash_float_option("units of time between changing colour and moving")] = 0.2,
                  spread_amount: typing.Annotated[float, interactions.slash_float_option("how much pixels spread out", min_value=0)] = 0.2,
                  gravity_x: typing.Annotated[float, interactions.slash_float_option("direction the pixels accelerate")] = 0,
                  gravity_y: typing.Annotated[float, interactions.slash_float_option("direction the pixels accelerate")] = -0.5,
                  ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (delay, frames, time_steps, spread_delay, spread_amount, gravity_x, gravity_y)
        img = await edit_util.run_in_subprocess(ctx, animated.ash, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, animated.ash, args, {}

    @misc_group.subcommand(sub_cmd_name="snap", sub_cmd_description="swap pixels around")
    async def snap(self, ctx: interactions.SlashContext,
                   file: file_option,
                   steps: typing.Annotated[float, interactions.slash_float_option("approximate number of steps, normalized (multiplied by number of pixels)", min_value=0)] = 2,
                   fuzzy: typing.Annotated[bool, interactions.slash_bool_option("whether to blend or swap pixels")] = False,
                   ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (steps, fuzzy)
        img = await edit_util.run_in_subprocess(ctx, misc.snap, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, misc.snap, args, {}

    @misc_group.subcommand(sub_cmd_name="magic", sub_cmd_description="spread out pixels")
    async def magic(self, ctx: interactions.SlashContext,
                    file: file_option,
                    steps: typing.Annotated[float, interactions.slash_float_option("approximate number of steps, normalized (multiplied by number of pixels)", min_value=0)] = 2,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (steps,)
        img = await edit_util.run_in_subprocess(ctx, misc.magic, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, misc.magic, args, {}

    @misc_group.subcommand(sub_cmd_name="bulge", sub_cmd_description="add a bulge")
    async def bulge(self, ctx: interactions.SlashContext,
                    file: file_option,
                    amount: typing.Annotated[float, interactions.slash_float_option("strength")] = 1,
                    center_x: coord_x_option = 0.5,
                    center_y: coord_y_option = 0.5,
                    ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (amount, center_x, center_y)
        img = await edit_util.run_in_subprocess(ctx, misc.bulge, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, misc.bulge, args, {}

    @misc_group.subcommand(sub_cmd_name="upscale", sub_cmd_description="double the image size using Waifu2x")
    async def upscale(self, ctx: interactions.SlashContext,
                      file: file_option,
                      ) -> None:
        await util.preprocess(ctx)
        ctx2 = edit_util.PsuedoContext(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ()
        img = await edit_util.run_in_subprocess(ctx2, misc.upscale, (img, *args))
        await edit_util.run_in_subprocess(ctx2, image_io.send_file, (img, False))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, misc.upscale, args, {"allow_downscaling": False}

    @misc_group.subcommand(sub_cmd_name="downscale", sub_cmd_description="half the image size")
    async def downscale(self, ctx: interactions.SlashContext,
                        file: file_option,
                        ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = ()
        img = await edit_util.run_in_subprocess(ctx, misc.downscale, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, misc.downscale, args, {}

    @meta_group.subcommand(sub_cmd_name="random", sub_cmd_description="perform random edits")
    async def random(self, ctx: interactions.SlashContext,
                     file: file_option,
                     iterations: typing.Annotated[int, interactions.slash_int_option("number of times to use another command", min_value=0)] = 3,
                     preset: typing.Annotated[str, interactions.slash_str_option("presets containing which edits are allowed", choices=util.as_choices(["all", "default", "no_basic", "no_basic, no_blur", "none"]))] = "default",
                     allow_basic: typing.Annotated[typing.Optional[bool], interactions.slash_bool_option("whether to allow basic edits")] = None,
                     allow_blur: typing.Annotated[typing.Optional[bool], interactions.slash_bool_option("whether to allow blur edits")] = None,
                     allow_animated: typing.Annotated[typing.Optional[bool], interactions.slash_bool_option("whether to allow animated edits")] = None,
                     allow_misc: typing.Annotated[typing.Optional[bool], interactions.slash_bool_option("whether to allow misc edits")] = None,
                     allow_text: typing.Annotated[typing.Optional[bool], interactions.slash_bool_option("whether to allow text")] = None,
                     ) -> None:
        await util.preprocess(ctx)
        img = image_io.from_url(file.proxy_url)
        args = (iterations, preset, allow_basic, allow_blur, allow_animated, allow_misc, allow_text)
        img = await edit_util.run_in_subprocess(ctx, meta.randomEdits, (img, *args))
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (img,))
        self.last_img, self.last_edit, self.last_args, self.last_send_args = img, meta.randomEdits, args, {}

    @meta_group.subcommand(sub_cmd_name="repeat", sub_cmd_description="run the previous command on its output")
    async def repeat(self, ctx: interactions.SlashContext,
                     ) -> None:
        await util.preprocess(ctx)
        if (self.last_img == None or self.last_send_args == None):
            raise interactions.errors.BadArgument("no edit has been run since startup")
        ctx2 = edit_util.PsuedoContext(ctx)
        img = await edit_util.run_in_subprocess(ctx2, meta.repeat, (self.last_img, self.last_edit, self.last_args))
        await edit_util.run_in_subprocess(ctx2, image_io.send_file, (img,), self.last_send_args)
        self.last_img = img

    @meta_group.subcommand(sub_cmd_name="repost", sub_cmd_description="send the output of the last edit")
    async def repost(self, ctx: interactions.SlashContext
                     ) -> None:
        await util.preprocess(ctx)
        if (self.last_img == None or self.last_send_args == None):
            raise interactions.errors.BadArgument("no edit has been run since startup")
        await edit_util.run_in_subprocess(ctx, image_io.send_file, (self.last_img,), self.last_send_args)
