import logging
import random
import typing

from discord.ext import commands

from shatteredbot.lib.pokemon import pokemon

logger = logging.getLogger("shatteredbot")


class PokemonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases = ["dex"]
    )
    async def pokedex(self, ctx, pkmn: typing.Union[int, str] = None):
        """Pokemaaaaaaaaans"""
        if isinstance(pkmn, str):
            p = next((m for m in pokemon if m.name.lower() == pkmn.lower()), None)
        elif isinstance(pkmn, int):
            p = next((m for m in pokemon if m.natdex == pkmn), None)
        else:
            p = None

        if p is None:
            p = random.choice(pokemon)

        e = p.stats_embed()
        await ctx.send(embed = e)


def setup(bot):
    bot.add_cog(PokemonCog(bot))
