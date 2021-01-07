import logging

from discord.ext import commands

logger = logging.getLogger("atsomeone")


class TheCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        hidden = True
    )
    @commands.is_owner()
    async def someone(self, ctx, *, message):
        await ctx.send("PING")


def setup(bot):
    bot.add_cog(TheCog(bot))
