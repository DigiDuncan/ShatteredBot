import io
import logging
import random
import requests

import discord
from discord.ext import commands

from shatteredbot.lib.wordlist import get_wordlist

logger = logging.getLogger("shatteredbot")
papyrus_url = "https://www.demirramon.com/gen/undertale_text_box.png?text={prefix}color%3Dorange%20{replace}!&box=undertale&boxcolor=ffffff&character=undertale-papyrus&expression=cool&charcolor=ffffff&font=papyrus&asterisk=null&mode=regular"
sans_url = "https://www.demirramon.com/gen/undertale_text_box.png?text=You%20feel%20like%20you%27re%20going%20to%20have%20a%20color%3Dblue%20{replace}.&box=undertale&boxcolor=ffffff&character=undertale-sans&expression=blue-eye&charcolor=ffffff&font=determination&asterisk=ffffff&mode=regular"
undyne_url = "https://www.demirramon.com/gen/undertale_text_box.png?text=BEHOLD%2C%20THE%20color={color}%20{replace}!&box=undertale&boxcolor=ffffff&character=undertale-undyne&expression=funny&charcolor=ffffff&font=determination&asterisk=ffffff&mode=regular"

bads = get_wordlist("bad")
times = get_wordlist("time")
battles = get_wordlist("battle")
passes = get_wordlist("pass")
weapons = get_wordlist("weapon")
descriptions = get_wordlist("description")


def get_image(url):
    response = requests.get(url)
    return io.BytesIO(response.content)


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
            await ctx.reply("That shit looks like the... Battle... Pass. Huh.", mention_author = False)
            return
        await ctx.reply(f"That shit looks like the **{battlepass}.**", mention_author = False)

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

        if choice == "text":
            await ctx.send(f"You feel like you're going to have a **{badtime}.**")
            return

        temp = await ctx.reply(f"You feel like you're going to have a **{badtime}.**", mention_author=False)
        await temp.delete()

        url = sans_url.format(replace = badtime)
        image = get_image(url)
        await ctx.send("", file = discord.File(image, filename = "badtime.png"))

    @commands.command(
        hidden = True
    )
    async def badpass(self, ctx, choice = ""):
        if choice == "count":
            await ctx.send(f"There are **{len(bads) * len(passes)}** ways to say \"bad pass\".")
            return

        badpass = random.choice(bads + [""]) + " " + random.choice(passes + [""])
        badpass = badpass.upper()
        custom = badpass
        prefixes = ["THIS SHIT LOOKS LIKE THE ", "YOU FEEL LIKE YOU'RE GOING TO HAVE A "]
        prefix = random.choice(prefixes)

        if choice == "text":
            await ctx.send(f"{prefix}{custom}")
            return

        temp = await ctx.reply(f"{prefix}{custom}", mention_author=False)
        await temp.delete()

        url = papyrus_url.format(prefix = prefix, replace = custom)
        image = get_image(url)
        await ctx.send("", file = discord.File(image, filename = "badpass.png"))

    @commands.command(
        hidden = True
    )
    async def battletime(self, ctx, choice = ""):
        if choice == "count":
            await ctx.send(f"There are **{len(battles) * len(times)}** ways to say \"battle time\".")
            return

        battletime = random.choice(battles + [""]) + " " + random.choice(times + [""])
        battletime = battletime.upper()
        custom = battletime
        prefixes = ["THIS SHIT LOOKS LIKE THE ", "YOU FEEL LIKE YOU'RE GOING TO HAVE A "]
        prefix = random.choice(prefixes)

        if choice == "text":
            await ctx.send(f"{prefix}{custom}")
            return

        temp = await ctx.reply(f"{prefix}{custom}", mention_author=False)
        await temp.delete()

        url = papyrus_url.format(prefix = prefix, replace = custom)
        image = get_image(url)
        await ctx.send("", file = discord.File(image, filename = "battletime.png"))

    @commands.command(
        aliases = ["weapon", "spear"]
    )
    async def spearofjustice(self, ctx, *, choice = ""):
        if choice == "count":
            await ctx.send(f"There are **{len(weapons) * len(descriptions)}** ways to say \"Spear of Justice\".")
            return
        weapon = random.choice(weapons)
        color = "green"
        if random.randint(1, 100) == 100:
            weapon += "...?"
        if random.randint(1, 100) == 100:
            weapon = random.choice(["common", "uncommon", "rare", "epic", "legendary", "big", "small", "huge", "tiny", "rusted", "sparkling"]) + " " + weapon
        if random.randint(1, 4096) == 4096:
            weapon = "shiny " + weapon
            color = "purple"
        description = random.choice(descriptions)
        if random.randint(1, 100) == 100:
            description += "-INATOR"
        spear = weapon + " OF " + description
        spear = spear.upper()

        if choice == "text":
            await ctx.send(f"BEHOLD, THE **{spear}!**")
            return

        temp = await ctx.reply(f"BEHOLD, THE **{spear}!**", mention_author=False)
        await temp.delete()

        url = undyne_url.format(replace = spear, color = color)
        image = get_image(url)
        await ctx.send("", file = discord.File(image, filename = "spear.png"))


def setup(bot):
    bot.add_cog(GeneratorCog(bot))
