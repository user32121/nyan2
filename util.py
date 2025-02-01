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


class PreprocessingError(Exception):
    pass


async def preprocess(ctx: interactions.SlashContext) -> None:
    await ctx.defer()
    if random.random() < 0.01:
        raise PreprocessingError("fuck off")


def as_choices(choices: list[str]) -> list[interactions.SlashCommandChoice]:
    return [interactions.SlashCommandChoice(x, x) for x in choices]


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


async def get_emoji(ctx: interactions.SlashContext, ids: str) -> interactions.CustomEmoji:
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
            raise interactions.errors.BadArgument(f"invalid emoji: {ids}")
    emoji = await ctx.bot.fetch_custom_emoji(eid, gid)
    if (emoji == None):
        raise interactions.errors.BadArgument(f"could not find emoji {ids}")
    return emoji


class PsuedoContext:
    """A class with a send method. Minimally imitates a SlashContext. For commands where the context expires before it finishes."""

    def __init__(self, ctx: interactions.Message | interactions.SlashContext) -> None:
        self.ctx = ctx

    async def send(self, **kwargs) -> interactions.Message:
        if (isinstance(self.ctx, interactions.SlashContext)):
            self.ctx = await self.ctx.send(**kwargs)
        else:
            self.ctx = await self.ctx.reply(**kwargs)
        return self.ctx

    async def edit(self, **kwargs) -> interactions.Message:
        return await self.ctx.edit(**kwargs)


all_commands: list[tuple[str, str, str]] = []


def filter_description(s:  str) -> typing.Optional[str]:
    if s == "No Description Set":
        return None
    return s


def store_command(keyword: str = "") -> typing.Callable[[interactions.SlashCommand], interactions.SlashCommand]:
    def store(sc: interactions.SlashCommand) -> interactions.SlashCommand:
        name = sc.resolved_name
        kw = str(keyword or sc.sub_cmd_name or sc.group_name or sc.name)
        description = filter_description(str(sc.sub_cmd_description)) or filter_description(str(sc.group_description)) or filter_description(str(sc.description)) or "Error"
        all_commands.append((name, kw, description))
        return sc
    return store
