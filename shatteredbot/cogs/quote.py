from __future__ import annotations
import logging
from os import PathLike
import re
import json
import random

import arrow
import discord

from discord.ext import commands
from shatteredbot import conf
from shatteredbot.lib.utils import sentence_join
from shatteredbot.lib import paths

logger = logging.getLogger("shatteredbot")

RE_QUOTE = re.compile(r"(?s)(?P<quote>(?:>\s.*?\n)+)(?:<@!?\d+\>\s?)*(?P<customauthor>.*)", re.DOTALL)

quote_help = """**`?quote` Help**
`?quote read <num>`: Pull up a quote by ID.
`?quote author @User`: Pull up a quote by a user.
`?quote random`: Pull up a random quote.
`?quote name <@user> <name>`: Assign a canon name.

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
?quote add
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

    def add_quote(self, text: str, authors: list[int], custom_author: str = None):
        new_qid = self.nextQID
        self.quotes.append(
            Quote(new_qid, text, authors, custom_author = custom_author)
        )
        self.save()

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
    async def quote(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(quote_help)

    @quote.command()
    async def read(self, ctx, num: int):
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

    @quote.command(
        multiline = True
    )
    async def add(self, ctx, *, quote):
        if m := re.search(RE_QUOTE, quote):
            text = m.group("text")
            custom_author = m.group("customauthor")
        else:
            await ctx.send("This quote is incorrectly formatted! See the help for info.")
            return

        textlines = text.splitlines()
        for line in textlines:
            line.removeprefix(">")
            line = line.strip()
        text = "\n".join(textlines)

        if custom_author.strip() == "":
            custom_author = None

        authors = [m.id for m in ctx.message.mentions]

        quotedb.add_quote(text, authors, custom_author)

        for author in authors:
            if author not in quotedb.usermap:
                await ctx.send(f"<@!{author}> does not have a canon name! Please run `{conf.prefix}quote name <@!{author}> <name>` to assign them one.")

    @quote.command()
    async def name(self, ctx, user: discord.Member, *, name):
        if user.id in quotedb.usermap:
            await ctx.send("That user already has a canon name.")
            return
        else:
            quotedb.usermap[user.id] = name
            await ctx.send(f"Name \"{name}\" assigned.")

    @quote.command()
    async def help(self, ctx):
        await ctx.send(quote_help)

    @commands.command()
    async def qoute(self, ctx):
        await ctx.send("Come on man, it's not that hard.")


def setup(bot):
    bot.add_cog(QuoteCog(bot))
