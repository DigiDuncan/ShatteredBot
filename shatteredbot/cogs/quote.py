import logging

import arrow

from discord.ext import commands
from shatteredbot.lib.utils import sentence_join

logger = logging.getLogger("shatteredbot")


class Quote:
    def __init__(self, qid: int, text: str, authors: list[str], *,
                 custom_author: str = None):
        self.qid = qid
        self.text = text
        self._authors = authors
        self.year = arrow.now().year
        self._custom_author = custom_author

    @property
    def authors(self):
        if self._custom_author:
            return self._custom_author
        else:
            return sentence_join(self._authors, oxford = True)


class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def quote(self, ctx):
        await ctx.send("\"")


def setup(bot):
    bot.add_cog(QuoteCog(bot))
