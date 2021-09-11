import logging
import random
import discord

from discord.ext import commands

from shatteredbot.lib import paths
from shatteredbot.lib.filelist import UniqueFileList
from shatteredbot.lib.shatteredutils import is_dm

logger = logging.getLogger("shatteredbot")

charades_help = """
`s!charades help`: Get this help.
`s!charades add <phrase...>`: Add a word to the Charades list.
`s!charades get`: Get a new Charades word DMed to you.
"""

phrases = UniqueFileList(paths.charadespath)


class CharadesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def charades(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(charades_help)

    @charades.command()
    async def help(self, ctx):
        await ctx.send(charades_help)

    @charades.command(
        usage = "<phrase...>"
    )
    async def add(self, ctx, *, phrase):
        try:
            phrases.append(phrase)
        except ValueError:
            await ctx.send(f"Phrase `{phrase}` already in the list!")
            return

        await ctx.send(f"Phrase `{phrase}` added to the list!")

    @charades.command(
        hidden = True
    )
    async def remove(self, ctx, *, phrase):
        if is_dm(ctx.author) is False:
            return

        try:
            phrases.remove(phrase)
        except ValueError:
            await ctx.send(f"Phrase `{phrase}` not in the list!")
            return

        await ctx.send(f"Phrase `{phrase}` removed from the list!")

    @charades.command()
    async def get(self, ctx, *, user: discord.Member = None):
        p = random.choice(phrases.items)
        if user:
            if is_dm(ctx.author) is True:
                await user.send(f"Your phrase is:\n> {p}")
                return
            else:
                await ctx.send("Only admins can send charades to users other than them!")
                return
        await ctx.message.author.send(f"Your phrase is:\n> {p}")

    @charades.command(
        hidden = True
    )
    async def getall(self, ctx):
        if is_dm(ctx.author) is False:
            return
        await ctx.message.author.send("**All the phrases are:**\n" + ", ".join(phrases.items))


def setup(bot):
    bot.add_cog(CharadesCog(bot))
