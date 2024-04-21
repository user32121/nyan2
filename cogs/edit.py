import logging

import interactions

import util
from .edits import image_io, basic

logger = logging.getLogger(__name__)
base_command = interactions.SlashCommand(**util.command_args, name="edit", description="various image edits")
basic_group = base_command.group("basic", "simple edits")
blur_group = base_command.group("blur", "various blur effects")
animated_group = base_command.group("animated", "effects that make gifs")
misc_group = base_command.group("misc", "miscellaneous effects")
file_option = interactions.slash_attachment_option("the image to edit", True)
colour_option = interactions.slash_str_option("the colour to apply; either comma separated integers or a hex colour code", True)


class Edit(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @basic_group.subcommand(sub_cmd_name="red", sub_cmd_description="isolate the red component of the image")
    async def red(self, ctx: interactions.SlashContext,
                  file: file_option,  # type: ignore
                  ) -> None:
        await ctx.defer()
        img = await image_io.from_url(ctx, file.proxy_url)
        if (img == None):
            return
        img = basic.multiply(img, (1, 0, 0, 1))
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="green", sub_cmd_description="isolate the green component of the image")
    async def green(self, ctx: interactions.SlashContext,
                    file: file_option,  # type: ignore
                    ) -> None:
        await ctx.defer()
        img = await image_io.from_url(ctx, file.proxy_url)
        if (img == None):
            return
        img = basic.multiply(img, (0, 1, 0, 1))
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="blue", sub_cmd_description="isolate the blue component of the image")
    async def blue(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await ctx.defer()
        img = await image_io.from_url(ctx, file.proxy_url)
        if (img == None):
            return
        img = basic.multiply(img, (0, 0, 1, 1))
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="hue", sub_cmd_description="not implemented")
    async def hue(self, ctx: interactions.SlashContext,
                  file: file_option,  # type: ignore
                  ) -> None:
        await util.not_implemented(ctx)

    @basic_group.subcommand(sub_cmd_name="saturation", sub_cmd_description="not implemented")
    async def saturation(self, ctx: interactions.SlashContext,
                         file: file_option,  # type: ignore
                         ) -> None:
        await util.not_implemented(ctx)

    @basic_group.subcommand(sub_cmd_name="luminosity", sub_cmd_description="not implemented")
    async def luminosity(self, ctx: interactions.SlashContext,
                         file: file_option,  # type: ignore
                         ) -> None:
        await util.not_implemented(ctx)

    @basic_group.subcommand(sub_cmd_name="invert", sub_cmd_description="not implemented")
    async def invert(self, ctx: interactions.SlashContext,
                     file: file_option,  # type: ignore
                     ) -> None:
        await util.not_implemented(ctx)

    @basic_group.subcommand(sub_cmd_name="blend", sub_cmd_description="not implemented")
    async def tint(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   colour: colour_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @basic_group.subcommand(sub_cmd_name="multiply", sub_cmd_description="multiply the image by a colour")
    async def multiply(self, ctx: interactions.SlashContext,
                       file: file_option,  # type: ignore
                       colour: colour_option,  # type: ignore
                       ) -> None:
        await ctx.defer()
        img = await image_io.from_url(ctx, file.proxy_url)
        if (img == None):
            return
        colour = await basic.parse_colour(ctx, colour)
        if(colour == None):
            return
        img = basic.multiply(img, colour)
        await image_io.send_file(ctx, img)

    @basic_group.subcommand(sub_cmd_name="grid", sub_cmd_description="not implemented")
    async def grid(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @basic_group.subcommand(sub_cmd_name="text", sub_cmd_description="not implemented")
    async def text(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @blur_group.subcommand(sub_cmd_name="blur", sub_cmd_description="not implemented")
    async def blur(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @blur_group.subcommand(sub_cmd_name="motionblur", sub_cmd_description="not implemented")
    async def motionblur(self, ctx: interactions.SlashContext,
                         file: file_option,  # type: ignore
                         ) -> None:
        await util.not_implemented(ctx)

    @blur_group.subcommand(sub_cmd_name="zoomblur", sub_cmd_description="not implemented")
    async def zoomblur(self, ctx: interactions.SlashContext,
                       file: file_option,  # type: ignore
                       ) -> None:
        await util.not_implemented(ctx)

    @blur_group.subcommand(sub_cmd_name="circularblur", sub_cmd_description="not implemented")
    async def circularblur(self, ctx: interactions.SlashContext,
                           file: file_option,  # type: ignore
                           ) -> None:
        await util.not_implemented(ctx)

    @animated_group.subcommand(sub_cmd_name="boom", sub_cmd_description="not implemented")
    async def boom(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @animated_group.subcommand(sub_cmd_name="rave", sub_cmd_description="not implemented")
    async def rave(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @animated_group.subcommand(sub_cmd_name="rainbow", sub_cmd_description="not implemented")
    async def rainbow(self, ctx: interactions.SlashContext,
                      file: file_option,  # type: ignore
                      ) -> None:
        await util.not_implemented(ctx)

    @animated_group.subcommand(sub_cmd_name="spin", sub_cmd_description="not implemented")
    async def spin(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @animated_group.subcommand(sub_cmd_name="squish", sub_cmd_description="not implemented")
    async def squish(self, ctx: interactions.SlashContext,
                     file: file_option,  # type: ignore
                     ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="snap", sub_cmd_description="not implemented")
    async def snap(self, ctx: interactions.SlashContext,
                   file: file_option,  # type: ignore
                   ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="magic", sub_cmd_description="not implemented")
    async def magic(self, ctx: interactions.SlashContext,
                    file: file_option,  # type: ignore
                    ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="bulge", sub_cmd_description="not implemented")
    async def bulge(self, ctx: interactions.SlashContext,
                    file: file_option,  # type: ignore
                    ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="break", sub_cmd_description="not implemented")
    async def break_(self, ctx: interactions.SlashContext,
                     file: file_option,  # type: ignore
                     ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="upscale", sub_cmd_description="not implemented")
    async def upscale(self, ctx: interactions.SlashContext,
                      file: file_option,  # type: ignore
                      ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="downscale", sub_cmd_description="not implemented")
    async def downscale(self, ctx: interactions.SlashContext,
                        file: file_option,  # type: ignore
                        ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="random", sub_cmd_description="not implemented")
    async def random(self, ctx: interactions.SlashContext,
                     file: file_option,  # type: ignore
                     ) -> None:
        await util.not_implemented(ctx)

    @misc_group.subcommand(sub_cmd_name="repeat", sub_cmd_description="not implemented")
    async def repeat(self, ctx: interactions.SlashContext,
                     file: file_option,  # type: ignore
                     ) -> None:
        await util.not_implemented(ctx)
