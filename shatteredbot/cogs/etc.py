import logging

from discord.ext import commands

logger = logging.getLogger("shatteredbot")


class ETCCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spine(self, ctx, *, victim = "mean"):
        await ctx.send(f"> **Removed {victim}'s spine.**")


def setup(bot):
    bot.add_cog(ETCCog(bot))
