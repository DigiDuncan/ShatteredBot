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

bads = [
    "bad",
    "awful",
    "crummy",
    "unfortunate",
    "terrible",
    "sub-standard",
    "poor",
    "inferior",
    "unpleasant",
    "disagreeable",
    "unfavorable",
    "nasty",
    "dreadful",
    "grim",
    "distressing",
    "regrettable",
    "unsatisfactory",
    "atrocious",
    "lousy",
    "rough",
    "sad",
    "blah",
    "unacceptable",
    "garbage",
    "junky",
    "abominable",
    "crappy",
    "cruddy",
    "defective",
    "faulty",
    "not good",
    "incorrect",
    "shitty"
]

times = [
    "time",
    "experience",
    "juncture",
    "moment",
    "date",
    "hour",
    "minute",
    "week",
    "day",
    "present",
    "duration",
    "occasion",
    "incident",
    "occurrence",
    "circumstance",
    "existence",
    "situation",
    "condition",
    "transaction",
    "accident",
    "instance",
    "affair",
    "adventure",
    "coincidence",
    "event",
    "fate",
    "happening",
    "ceremony",
    "development",
    "mishap",
    "phenomenon"
]


class GeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def battlepass(self, ctx, *, choice = ""):
        if choice == "count":
            await ctx.send(f"There are **{len(battles) * len(passes)}** ways to say Battle Pass.")
            return
        battlepass = random.choice(battles) + " " + random.choice(passes)
        battlepass = battlepass.title()
        if battlepass == "Battle Pass":
            await ctx.send("That shit looks like the... Battle... Pass. Huh.")
            return
        await ctx.send(f"That shit looks like the **{battlepass}**.")

    @commands.command()
    async def badtime(self, ctx, *, choice = ""):
        if choice == "count":
            await ctx.send(f"There are **{len(bads) * len(times)}** ways to say \"bad time\".")
            return
        badtime = random.choice(bads) + " " + random.choice(times)
        badtime = badtime.lower()
        if badtime == "bad time":
            await ctx.send("hey there buddy chum pal friend buddy pal chum bud friend fella brother amigo pal buddy friend chummy chum chum pal i dont mean to be rude my friend pal home slice bread slice dawg but i gotta warn ya if u take one more diddly darn step right there im gonna have to diddly darn snap ur neck and wowza wouldnt that be a crummy juncture huh do u want that do u wish upon yourself to come into physical experience with a crummy juncture because friend buddy chum friend chum pally pal chum friend if u keep this up well gosh diddly darn i just might have to get not so friendly with you my friendly friend friend pal friend buddy chum pally friend chum buddy")
            return
        await ctx.send(f"You feel like you're going to have a **{badtime}**.")


def setup(bot):
    bot.add_cog(GeneratorCog(bot))
