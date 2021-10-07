import logging

from discord.ext import commands
from urllib.parse import quote

logger = logging.getLogger("shatteredbot")


class UndertaleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def box(self, ctx, *, command):
        root_url = "https://www.demirramon.com/gen/undertale_text_box.png?message="
        params = ["box", "boxcolor", "character", "expression", "url", "charcolor", "font", "asterisk", "small", "border", "mode"]
        await ctx.send(f"{root_url}{quote(command)}")


def setup(bot):
    bot.add_cog(UndertaleCog(bot))
