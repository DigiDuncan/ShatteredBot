from __future__ import annotations
import logging
from os import PathLike
import re
import json
import random

import arrow
import discord

from discord.ext import commands
from shatteredbot.lib.utils import sentence_join
from shatteredbot.lib import paths

logger = logging.getLogger("shatteredbot")

RE_QUOTE = re.compile(r"(?P<quote>(?:>\s.*?\n)+)<@!?\d+\>(?P<customauthor>.*)", re.DOTALL)

quote_help = """**`?quote` Help**
`?quote <num>`: Pull up a quote by ID.
`?quote author @User`: Pull up a quote by a user.
`?quote random`: Pull up a random quote.

**Adding A Quote**
*Normal*
```
?quote add
> "This is a quote!"
@DigiDuncan
```
becomes...
***Quote 000:***
"This is a quote!" *-- DigiDuncan, 2021*

*Advanced*
```
? quote add
> Digi: "Look at this, Tris!"
> Tris: "I do not care. :whyareyoualllikethis:"
@DigiDuncan @Triston Digi and Tris, working on anything
```
becomes...
***Quote 000:***
Digi: "Look at this!"
Tris: "I do not care. :whyareyoualllikethis:" *-- Digi and Tris, working on anything, 2021*
"""


class QuoteDB:
    def __init__(self, filepath: PathLike):
        self.filepath = filepath
        self.usermap: dict[int, str] = {}
        self.quotes: list[Quote]

    def get_quote_by_ID(self, qid: int) -> Quote:
        quote = next(quote for quote in self.quotes if quote.qid == qid)
        quote.author_string = quote.get_author_string(self)
        return quote

    def get_quotes_by_author(self, uid) -> Quote:
        quotes = [quote for quote in self.quotes if uid in quote.authors]
        for quote in quotes:
            quote.author_string = quote.get_author_string(self)
        return quotes

    def get_random_quote(self) -> Quote:
        return random.choice(self.quotes)

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
        self.date = arrow.now()
        self._custom_author = custom_author

    @property
    def year(self):
        return self.date.year

    def get_author_string(self, db: QuoteDB) -> str:
        if self._custom_author:
            return self._custom_author
        else:
            users = [db.usermap[k] for k in self.authors]
            return sentence_join(users, oxford = True)

    def full_text(self):
        return f"{self.text}\n*-- {self.get_author_string()}, {self.year}*"

    def to_embed(self):
        e = discord.Embed(
            title = f"Quote {self.qid}",
            description = self.full_text,
            timestamp = self.date.datetime
        )
        return e


# Canonical QuoteDB
quotedb = QuoteDB(paths.quotespath)


class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def quote(self, ctx, num: int):
        if ctx.invoked_subcommand is None and num is None:
            await ctx.send(quote_help)
        else:
            q = quotedb.get_quote_by_ID(num)
            await ctx.send(embed = q.to_embed())

    @quote.command()
    async def random(self, ctx):
        q = quotedb.get_random_quote()
        await ctx.send(embed = q.to_embed())

    @quote.command()
    async def author(self, ctx, author: discord.Member):
        q = quotedb.get_quotes_by_author(author.id)
        await ctx.send(embed = q.to_embed())


def setup(bot):
    bot.add_cog(QuoteCog(bot))
