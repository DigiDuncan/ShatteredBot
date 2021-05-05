import json
import logging
from collections import UserDict

import toml

from discord.ext import commands
from discord import Embed

from shatteredbot.lib import paths
from shatteredbot.lib.pathdict import PathDict
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
        self._color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, int):
            self._color = value
        elif isinstance(value, str):
            value = value.removeprefix("#")
            self._color = int(value, 16)

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

    def to_json(self):
        {
            "title": self.title,
            "description": self.description,
            "fields": self.fields,
            "image": self.image,
            "color": self._color
        }

    @classmethod
    def from_json(cls, jsondata: dict) -> "LoreItem":
        title = jsondata["title"]
        desc = jsondata["description"]
        fields = jsondata["fields"]
        image = jsondata["image"]
        color = jsondata["color"]

        return LoreItem(title, description=desc, fields=fields, image=image, color=color)


class LoreBook(UserDict):
    def add(self, loreitem: LoreItem):
        if loreitem.key in self.data:
            raise ValueError("This lore item already exists in this lorebook!")
        self.data[loreitem.key] = loreitem

    def remove(self, key):
        if key not in self.data:
            raise ValueError("This lore item doesn't exist in this lorebook!")

    @classmethod
    def load(cls):
        try:
            lorejson = PathDict(toml.load(paths.lorepath))
            lorejson = json.load(lorejson)
            return LoreBook(lorejson)
        except FileNotFoundError:
            logger.warn("Lore not found, creating blank lore...")
            return LoreBook()

    def save(self):
        savepath = PathDict(toml.load(paths.lorepath))
        with open(savepath) as f:
            json.dump(self.data, f)


book = LoreBook.load()


class LoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def lore(self, ctx, subcommand, name, *, args):
        """
        lore
        ├── create
        │   └── "<name>"
        ├── delete
        │   └── "<name>"
        ├── read
        │   └── "<name>"
        ├── addfield
        │   └── "<name>" "<fieldname>" [description...]
        ├── removefield
        │   └── "<name>" "<fieldname>"
        └── edit
            ├── name
            │   └── "<oldname>" "<newname>"
            ├── description
            │   └── "<name>" <new description...>
            ├── field
            │   └── "<name>" "<fieldname>" <new description...>
            ├── image
            │   └── "<name>" <url...|remove>
            └── color
                └── "<name>" <color>
        """
        await ctx.send(self.lore.__doc__)

    async def create(self, ctx, *, name):
        """Create a new lore item."""
        book.add(name)
        await ctx.send(f"{name} added.")

    async def delete(self, ctx, *, name):
        """Delete a lore item."""
        book.remove(name)
        await ctx.send(f"{name} removed.")

    async def read(self, ctx, *, name):
        """Read a lore item."""
        e = book[name].to_embed()
        await ctx.send(embed = e)

    @lore.group()
    async def edit(self, ctx):
        await ctx.send("Edit what? :sweat_smile:")

    @edit.command()
    async def name(self, ctx, oldname, newname):
        book[oldname] = book[newname]
        del book[oldname]
        book.save()
        await ctx.send(f"{oldname} is now called {newname}.")

    @edit.command(
        aliases = ["desc"]
    )
    async def description(self, ctx, name, *, value):
        book[name].description = value
        book.save()
        await ctx.send(f"{name}'s description updated.")

    @edit.command()
    async def color(self, ctx, name, *, value):
        book[name].color = value
        book.save()
        await ctx.send(f"{name}'s color updated.")


def setup(bot):
    bot.add_cog(LoreCog(bot))
