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
        counts: dict[int, int] = {}
        for message_id, author_id, content in scan.message_cache[ctx.channel_id]:
            count = matches(content)
            if (reply and count):
                m = await ctx.channel.fetch_message(message_id)
                if(m != None):
                    reply = False
                    await m.reply("found")
            if (count_by == "messages"):
                count = int(bool(count))
            if (count):
                counts[author_id] = counts.get(author_id, 0) + count
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        output = f"total matches: {sum(counts.values())}"
        for author_id, count in sorted_counts:
            user = await ctx.bot.fetch_user(author_id)
            if (user == None):
                output += f"\n{user}: {count}"
            else:
                output += f"\n{user.display_name}: {count}"
        await ctx.send(output)
