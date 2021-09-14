import logging

from discord.ext import commands

logger = logging.getLogger("shatteredbot")


class QuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def quote(self, ctx):
        await ctx.send("\"")


def setup(bot):
    bot.add_cog(QuoteCog(bot))
