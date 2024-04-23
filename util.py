import logging
import random
import time
import typing

import colorama
import interactions

import config

logger = logging.getLogger(__name__)

command_args: dict[str, typing.Any] = {"scopes": config.GUILDS}
not_implemented_args: dict[str, typing.Any] = {"description": "not implemented", **command_args}


def configure_logger():
    logging.addLevelName(logging.INFO, f"{colorama.Fore.GREEN}{logging.getLevelName(logging.INFO)}{colorama.Fore.RESET}")
    logging.addLevelName(logging.WARNING, f"{colorama.Fore.YELLOW}{logging.getLevelName(logging.WARNING)}{colorama.Fore.RESET}")
    logging.addLevelName(logging.ERROR, f"{colorama.Fore.RED}{logging.getLevelName(logging.ERROR)}{colorama.Fore.RESET}")
    logging.addLevelName(logging.CRITICAL, f"{colorama.Fore.RED}{logging.getLevelName(logging.CRITICAL)}{colorama.Fore.RESET}")

    logging.basicConfig(level=logging.INFO, format=f"%(asctime)s | %(levelname)-20s | {colorama.Fore.CYAN}%(name)-20s{colorama.Fore.RESET} | %(message)s")


async def not_implemented(ctx: interactions.SlashContext):
    await ctx.send("Not implemented")


async def preprocess(ctx: interactions.SlashContext) -> bool:
    await ctx.defer()
    b = random.random() < 0.01
    if (b):
        await ctx.send("fuck off")
    return b


def as_choices(choices: list[str]) -> list[interactions.SlashCommandChoice]:
    return [interactions.SlashCommandChoice(x, x) for x in choices]


async def get_guild(ctx: interactions.SlashContext, id: str) -> typing.Optional[interactions.Guild]:
    try:
        gid = int(id)
    except ValueError as e:
        await ctx.send("invalid guild")
        logger.info(e)
        return None
    guild = await ctx.bot.fetch_guild(gid)
    if (guild == None):
        await ctx.send("could not find guild")
    return guild


async def get_message(ctx: interactions.SlashContext, id: str) -> typing.Optional[interactions.Message]:
    try:
        mid = int(id)
    except ValueError as e:
        await ctx.send("invalid message id")
        logger.info(e)
        return None
    msg = await ctx.channel.fetch_message(mid)
    if (msg == None):
        await ctx.send("could not find message")
    return msg


async def get_emojis(ctx: interactions.AutocompleteContext) -> None:
    start = time.time()
    ret = []
    for g in ctx.bot.guilds:
        if (time.time() - start > 2.5 or len(ret) >= 25):
            break
        emojis = await g.fetch_all_custom_emojis()
        for e in emojis:
            if (e.name != None and ctx.input_text.lower() in e.name.lower()):
                ret.append(interactions.SlashCommandChoice(e.name, f"{e.id},{g.id}"))
                if (len(ret) >= 25):
                    break
    await ctx.send(ret)


async def get_emoji(ctx: interactions.SlashContext, ids: str) -> typing.Optional[interactions.CustomEmoji]:
    try:
        eid, gid = ids.split(",")
        eid = int(eid)
        gid = int(gid)
    except (IndexError, ValueError) as err:
        eid = None
        for g in ctx.bot.guilds:
            for e in await g.fetch_all_custom_emojis():
                if (e.name == ids):
                    eid = e.id
                    gid = g.id
        if (eid == None):
            await ctx.send("invalid emoji")
            logger.info(err)
            return None
    emoji = await ctx.bot.fetch_custom_emoji(eid, gid)
    if (emoji == None):
        await ctx.send("could not find emoji")
    return emoji
