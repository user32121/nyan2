import logging
import typing

import colorama
import interactions

import config

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


def as_choices(choices: list[str]) -> list[interactions.SlashCommandChoice]:
    return [interactions.SlashCommandChoice(x, x) for x in choices]
