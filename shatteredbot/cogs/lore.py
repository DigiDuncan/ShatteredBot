import logging
from collections import UserDict

from discord.ext import commands
from discord import Embed

from shatteredbot.lib.utils import truncate

logger = logging.getLogger("shatteredbot")

SHATTERED_PURPLE = 0x4F23B4


class LoreItem:
    def __init__(self, title, description, *, fields = {}, image = None, color = SHATTERED_PURPLE):
        self.title = title
        self.key = title.casefold.replace(" ", "_")
        self.description = description
        self.fields = fields
        self.image = image
        self.color = color

    @property
    def embed_length(self):
        return (sum([len(k) + len(v) for k, v in self.fields.items()])
                + (len(self.description) if len(self.description) < 1000 else 1000)
                + len(self.title))

    @property
    def description_chunks(self):
        chunks = []
        desc = self.description
        while len(desc) > 0:
            chunks.append("..." + truncate(desc, 1000))
            desc = desc[1000:]

        chunks[0] = chunks[0][3:]
        return chunks

    def add_field(self, title, description):
        if title in self.fields:
            raise ValueError("This field already exists!")
        if len(self.fields) >= 20:
            raise ValueError("This lore item has too many fields!")
        if self.embed_length + len(title) + len(description) >= 6000:
            raise ValueError("This lore item's embed is (or would be) too thicc!")
        if len(description) > 1024:
            raise ValueError("This field is too long!")
        self.fields[title] = description

    def to_embed(self) -> Embed:
        e = Embed(title = self.title, description = self.description_chunks[0])
        for t, d in self.fields.items():
            e.add_field(name = t, value = d)
        if self.image is not None:
            e.set_image(self.image)
        e.color = self.color
        return e


class LoreBook(UserDict):
    def add(self, loreitem: LoreItem):
        if loreitem.key in self.data:
            raise ValueError("This lore item already exists in this lorebook!")
        self.data[loreitem.key] = loreitem

    def remove(self, key):
        if key not in self.data:
            raise ValueError("This lore item doesn't exist in this lorebook!")


class LoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def lore(self, ctx, subcommand, *, args):
        subcommands = ["add", "delete", "edit", "read"]

        if subcommand not in subcommands:
            await ctx.send(f"Invalid subcommand for `lore`: `{subcommand}`")
            return


def setup(bot):
    bot.add_cog(LoreCog(bot))
