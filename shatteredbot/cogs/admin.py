import logging

from discord.ext import commands

logger = logging.getLogger("shatteredbot")


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        hidden = True
    )
    @commands.is_owner()
    async def stop(self, ctx):
        """RIP ShatteredBot."""
        logger.critical(f"Help, {ctx.author.display_name} is closing me!")
        await ctx.send("Stopping ShatteredBot. ☠️")
        await ctx.bot.close()


def setup(bot):
    bot.add_cog(AdminCog(bot))
