import logging
import random

from discord.ext import commands

logger = logging.getLogger("shatteredbot")

battles = [
    "battle",
    "fight",
    "altercation",
    "confrontation",
    "scuffle",
    "combat",
    "conflict",
    "skirmish",
    "struggle",
    "war",
    "feud",
    "crusade",
    "dispute",
    "strife",
    "contention",
    "attack",
    "encounter",
    "tussle",
    "melee",
    "warfare",
    "hostility",
    "competition",
    "toil",
    "rainbow 🌈",
    "la lucha"
]

passes = [
    "pass",
    "ticket",
    "license",
    "passport",
    "permit",
    "visa",
    "warrant",
    "certificate",
    "coupon",
    "voucher",
    "warrant",
    "authentication",
    "go-ahead",
    "document",
    "bus pass",
    "rainbow 🌈",
    "admission",
    "permiso"
]


class GeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def battlepass(self, ctx):
        battlepass = random.choice(battles) + " " + random.choice(passes)
        battlepass = battlepass.title()
        if battlepass == "Battle Pass":
            await ctx.send("That shit looks like the... Battle... Pass. Huh.")
            return
        await ctx.send(f"That shit looks like the **{battlepass}**.")


def setup(bot):
    bot.add_cog(GeneratorCog(bot))
