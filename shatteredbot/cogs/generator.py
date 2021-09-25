import logging
import random

from discord.ext import commands

logger = logging.getLogger("shatteredbot")
papyrus_url = "https://www.demirramon.com/gen/undertale_text_box.png?text={prefix}color%3Dorange%20{replace}!&box=undertale&boxcolor=ffffff&character=undertale-papyrus&expression=cool&charcolor=ffffff&font=papyrus&asterisk=null&mode=regular"
sans_url = "https://www.demirramon.com/gen/undertale_text_box.png?text=You%20feel%20like%20you%27re%20going%20to%20have%20a%20color%3Dblue%20{replace}.&box=undertale&boxcolor=ffffff&character=undertale-sans&expression=blue-eye&charcolor=ffffff&font=determination&asterisk=ffffff&mode=regular"

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
    "shitty",
    "fucky",
    "horrible"
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
    "phenomenon",
    "life"
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
            await ctx.send("https://cdn.discordapp.com/attachments/412692184182161414/891054485579890708/undertale_box_stack.png")
            return
        url = sans_url.format(replace = badtime).replace(" ", "%20").replace("'", "%27")
        await ctx.send(url)

    @commands.command(
        hidden = True
    )
    async def badpass(self, ctx):
        badpass = random.choice(bads) + " " + random.choice(passes)
        badpass = badpass.upper()
        custom = badpass
        prefixes = ["THIS SHIT LOOKS LIKE THE ", "YOU FEEL LIKE YOU'RE GOING TO HAVE A "]
        prefix = random.choice(prefixes)
        url = papyrus_url.format(prefix = prefix, replace = custom).replace(" ", "%20").replace("'", "%27")
        await ctx.send(url)

    @commands.command(
        hidden = True
    )
    async def battletime(self, ctx):
        battletime = random.choice(battles) + " " + random.choice(times)
        battletime = battletime.upper()
        custom = battletime
        prefixes = ["THIS SHIT LOOKS LIKE THE ", "YOU FEEL LIKE YOU'RE GOING TO HAVE A "]
        prefix = random.choice(prefixes)
        url = papyrus_url.format(prefix = prefix, replace = custom).replace(" ", "%20").replace("'", "%27")
        await ctx.send(url)


def setup(bot):
    bot.add_cog(GeneratorCog(bot))
