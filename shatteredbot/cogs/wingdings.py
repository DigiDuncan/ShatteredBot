import logging

from discord.ext import commands

english = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvqxyz1234567890,./?!-=_+;:'*"
wingdings = "✌👌👍👎☜☞☝☟✋☺😐☹💣☠⚐🏱✈☼💧❄🕆✞🕈✠✡☪♋♌♍♎♏♐♑♒♓j&●❍■□◻❑❒⬧⧫◆❖❑⌧⍓⌘📂📄🗏🗐🗄⌛🖮🖰🖲📁📪📬📭✍✏📫🖬♉🖃🖴🖳🕯🖂"

logger = logging.getLogger("shatteredbot")


class WingdingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        usage = "<message...>"
    )
    async def togaster(self, ctx, *, m):
        m = m.upper()
        out = ""
        for c in m:
            try:
                i = english.index(c)
            except ValueError:
                i = None
            if i:
                out += wingdings[i]
            else:
                out += c
        await ctx.send(f"`{out}`")

    @commands.command(
        usage = "<message...>"
    )
    async def towingdings(self, ctx, *, m):
        out = ""
        for c in m:
            try:
                i = english.index(c)
            except ValueError:
                i = None
            if i:
                out += wingdings[i]
            else:
                out += c
        await ctx.send(f"`{out}`")

    @commands.command(
        usage = "<message...>"
    )
    async def fromwingdings(self, ctx, *, m):
        out = ""
        for c in m:
            try:
                i = wingdings.index(c)
            except ValueError:
                i = None
            if i:
                out += english[i]
            else:
                out += c
        await ctx.send(out)


def setup(bot):
    bot.add_cog(WingdingsCog(bot))
