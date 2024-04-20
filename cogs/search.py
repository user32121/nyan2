import logging
import re

import interactions

import util
from . import scan

logger = logging.getLogger(__name__)


class Search(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(**util.command_args, name="search", description="search for a substring and get stats")
    async def search(self, ctx: interactions.SlashContext,
                     query: interactions.slash_str_option("text to search for", True),  # type: ignore
                     regex: interactions.slash_bool_option("whether to use regex matching") = False,  # type: ignore
                     count_by: interactions.slash_str_option("how to count occurrences",  # type: ignore
                                                             choices=util.as_choices(["instances", "messages"])) = "instances",
                     reply: interactions.slash_bool_option("whether to reply to the first match") = False,  # type: ignore
                     ) -> None:
        await scan.fill_cache(ctx.bot, ctx.channel, ctx)
        if (regex):
            def matches(s: str) -> int:
                return len(re.findall(query, s))
        else:
            def matches(s: str) -> int:
                return s.lower().count(query.lower())
        match_counts: dict[int, int] = {}
        counts: dict[int, int] = {}
        for message_id, author_id, content in scan.message_cache[ctx.channel_id]:
            match_count = matches(content)
            if (reply and match_count):
                m = await ctx.channel.fetch_message(message_id)
                if (m != None):
                    reply = False
                    await m.reply("found")
            if (count_by == "messages"):
                match_count = int(bool(match_count))
            if (match_count):
                match_counts[author_id] = match_counts.get(author_id, 0) + match_count
            counts[author_id] = counts.get(author_id, 0) + 1
        sorted_counts = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)
        output = f"total matches: {sum(match_counts.values())}/{sum(counts.values())} ({round(sum(match_counts.values())/sum(counts.values()), 3)})"
        for author_id, match_count in sorted_counts:
            user = await ctx.bot.fetch_user(author_id)
            if (user == None):
                output += f"\n{user}: {match_count}/{counts[author_id]} ({round(match_count/counts[author_id], 3)})"
            else:
                output += f"\n{user.display_name}: {match_count}/{counts[author_id]} ({round(match_count/counts[author_id], 3)})"
        await ctx.send(output)
