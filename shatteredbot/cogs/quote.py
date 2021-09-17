from __future__ import annotations
import logging
from os import PathLike
import re
import json

import arrow

from discord.ext import commands
from shatteredbot.lib.utils import sentence_join

logger = logging.getLogger("shatteredbot")

RE_QUOTE = re.compile(r"(?P<quote>(?:>\s.*?\n)+)<@!?\d+\>(?P<customauthor>.*)", re.DOTALL)


class QuoteDB:
    def __init__(self, filepath: PathLike):
        self.filepath = filepath
        self.usermap: dict[int, str] = {}
        self.quotes: list['Quote']

    def get_quote_by_ID(self, qid: int):
        quote = next(quote for quote in self.quotes if quote.qid == qid)
        quote.author_string = quote.get_author_string(self)
        return quote

    def get_quotes_by_author(self, uid):
        quotes = [quote for quote in self.quotes if uid in quote.authors]
        for quote in quotes:
            quote.author_string = quote.get_author_string(self)
        return quotes

    @property
    def nextQID(self):
        return max(q.qid for q in self.quotes) + 1

    @classmethod
    def from_JSON(cls, jsondata):
        qdb = QuoteDB(jsondata["filepath"])
        qdb.usermap = jsondata["usermap"]
        qdb.quotes = [Quote.from_JSON(j) for j in jsondata["quotes"]]
        return qdb

    def to_JSON(self):
        return {
            "filepath": self.filepath,
            "usermap":  self.usermap,
            "quotes":   [q.to_JSON() for q in self.quotes]
        }

    def load(self):
        with open(self.filepath) as f:
            data = json.load(f.read())
            self = self.from_JSON(data)

    def save(self):
        with open(self.filepath, "w+") as f:
            json.dump(self.to_JSON(), f, indent = 4)


class Quote:
    def __init__(self, qid: int, text: str, authors: list[int], *,
                 custom_author: str = None):
        self.qid = qid
        self.text = text
        self.authors = authors
        self.year = arrow.now().year
        self._custom_author = custom_author

    def get_author_string(self, db: QuoteDB) -> str:
        if self._custom_author:
            return self._custom_author
        else:
            users = [db.usermap[k] for k in self.authors]
            return sentence_join(users, oxford = True)


class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def quote(self, ctx):
        await ctx.send("\"")


def setup(bot):
    bot.add_cog(QuoteCog(bot))
