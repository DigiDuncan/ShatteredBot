import json
import logging
from collections import UserDict
from pathlib import Path
from typing import Dict

from discord.ext import commands
from discord import Embed

from shatteredbot.lib import paths
from shatteredbot.lib.utils import truncate
from shatteredbot.lib.shatteredutils import is_dm

logger = logging.getLogger("shatteredbot")

SHATTERED_PURPLE = 0x4F23B4

ok_roles = ["Owner And plant.", "Digimon", "TW"]

user_help = """**Lore Help**
`s!lore read <name>`: Reads the lore of that entry.
`s!lore all`: See a list of all entries."""

dm_help = user_help + """
`s!lore create <name>`: Adds an entry to the book.
`s!lore delete <name>`: Removes an entry from the book.
`s!lore edit name "<oldname>" <newname>`: Changes the name of an entry.
`s!lore edit description "<name>" <desc...>`: Changes the description of an entry.
`s!lore edit field "name>" "<fieldname>" <desc...>`: Changes the description of an entry's field of the name `fieldname`.
`s!lore edit color "<name>" <color>`: Changes the color of an entry.
`s!lore edit image "<name>" <url>`: Changes the image of an entry.
`s!lore edit hidden "<name>" <y/n>`: Hides an entry.
`s!lore addfield "<name>" "<fieldname>" <desc...>`: Adds a field to an entry.
`s!lore removefield "<name>" <fieldname>`: Removes a field from an entry.
"""


class LoreItem:
    def __init__(self, title, *, description = "", fields = {}, image = None, color = SHATTERED_PURPLE, hidden = False):
        self._title = title
        self.key = title.casefold().replace(" ", "_")
        self.description = description
        self.fields = fields
        self.image = image
        self._color = color
        self.hidden = hidden

    @property
    def title(self):
        return self._title if not self.hidden else self._title + " 🔒"

    @title.setter
    def title(self, value):
        self._title = value

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
        if len(desc) == 0:
            return [desc]

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
            e.set_image(url=self.image)
        e.color = self.color
        return e

    def to_json(self) -> Dict:
        return {
            "title": self._title,
            "description": self.description,
            "fields": self.fields,
            "image": self.image,
            "color": self._color,
            "hidden": self.hidden
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
        key = key.casefold().replace(" ", "_")
        if key not in self.data:
            raise ValueError("This lore item doesn't exist in this lorebook!")
        del self.data[key]

    def __getitem__(self, key):
        key = key.casefold().replace(" ", "_")
        return self.data[key]

    def __setitem__(self, key, item) -> None:
        key = key.casefold().replace(" ", "_")
        self.data[key] = item

    @classmethod
    def from_json(self, jsondata):
        return LoreBook({k: LoreItem.from_json(i) for k, i in jsondata.items()})

    @classmethod
    def load(cls):
        try:
            lorepath = Path(paths.lorepath)
            with open(lorepath, "r") as f:
                lorejson = json.load(f)
            return LoreBook.from_json(lorejson)
        except FileNotFoundError:
            logger.warn("Lore not found, creating blank lore...")
            return LoreBook()

    def save(self):
        savepath = Path(paths.lorepath)
        with open(savepath, "w") as f:
            json.dump({k: i.to_json() for k, i in self.data.items()}, f)


book = LoreBook.load()


class LoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def lore(self, ctx):
        """
        lore
        ├── create
        │   └── <name>
        ├── delete
        │   └── <name>
        ├── read
        │   └── <name>
        ├── addfield
        │   └── "<name>" "<fieldname>" [description...]
        ├── removefield
        │   └── "<name>" "<fieldname>"
        └── edit
            ├── name
            │   └── "<oldname>" <newname>
            ├── description
            │   └── "<name>" <new description...>
            ├── field
            │   └── "<name>" "<fieldname>" <new description...>
            ├── image
            │   └── "<name>" <url...|remove>
            └── color
                └── "<name>" <color>
        """
        if ctx.invoked_subcommand is None:
            if is_dm(ctx.author) is False:
                await ctx.send(user_help)
                return
            await ctx.send(dm_help)

    @lore.command(
        aliases = ["add"]
    )
    async def create(self, ctx, *, name):
        """Create a new lore item."""
        if is_dm(ctx.author) is False:
            return
        try:
            book.add(LoreItem(name))
        except ValueError:
            await ctx.send(f"Lore item `{name}` already in book!")
            return
        book.save()
        await ctx.send(f"`{name}` added.")

    @lore.command(
        aliases = ["remove"]
    )
    async def delete(self, ctx, *, name):
        """Delete a lore item."""
        if is_dm(ctx.author) is False:
            return
        try:
            book.remove(name)
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        book.save()
        await ctx.send(f"`{name}` removed.")

    @lore.command()
    async def read(self, ctx, *, name):
        """Read a lore item."""
        try:
            e = book[name].to_embed()
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        await ctx.send(embed = e)

    @lore.command(
        aliases = ["list"]
    )
    async def all(self, ctx):
        """List all lore items."""
        li = [i.title for i in book.values() if i.hidden is False]
        await ctx.send(
            "**Current Lore Entries**:\n"
            f"{', '.join(li)}"
        )

    @lore.group()
    async def edit(self, ctx):
        if is_dm(ctx.author) is False:
            return
        if ctx.invoked_subcommand is None:
            await ctx.send("Edit what? :sweat_smile:")

    @edit.command()
    async def name(self, ctx, oldname, newname):
        if is_dm(ctx.author) is False:
            return
        try:
            book[newname] = book[oldname]
        except KeyError:
            await ctx.send(f"Lore item `{oldname}` not in the book!")
            return
        del book[oldname]
        book[newname].title = newname
        book.save()
        await ctx.send(f"`{oldname}` is now called `{newname}`.")

    @edit.command(
        aliases = ["desc"]
    )
    async def description(self, ctx, name, *, value):
        if is_dm(ctx.author) is False:
            return
        try:
            book[name].description = value
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        book.save()
        await ctx.send(f"`{name}`'s description updated.")

    @edit.command()
    async def image(self, ctx, name, *, value):
        if is_dm(ctx.author) is False:
            return
        try:
            book[name].image = value
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        book.save()
        await ctx.send(f"`{name}`'s image updated.")

    @edit.command()
    async def field(self, ctx, name, fieldname, *, value):
        if is_dm(ctx.author) is False:
            return
        try:
            book[name].fields[fieldname] = value
        except KeyError:
            await ctx.send(f"Lore item `{name}` (or field name `{fieldname}`) not in the book!")
            return
        book.save()
        await ctx.send(f"`{name}`'s field `{fieldname}` updated.")

    @edit.command()
    async def color(self, ctx, name, *, value):
        if is_dm(ctx.author) is False:
            return
        try:
            book[name].color = value
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        book.save()
        await ctx.send(f"`{name}`'s color updated.")

    @edit.command()
    async def hidden(self, ctx, name, *, value: bool):
        if is_dm(ctx.author) is False:
            return
        try:
            book[name].hidden = value
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        book.save()
        await ctx.send(f"`{name}`'s hidden status updated.")

    @lore.command()
    async def addfield(self, ctx, name, fieldname, *, desc):
        """Add a field to an item."""
        if is_dm(ctx.author) is False:
            return
        try:
            book[name].add_field(fieldname, desc)
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        await ctx.send(f"Field `{fieldname}` added to item `{name}`.")
        book.save()

    @lore.command()
    async def removefield(self, ctx, name, *, fieldname):
        """Add a field to an item."""
        if is_dm(ctx.author) is False:
            return
        try:
            del book[name].fields[fieldname]
        except KeyError:
            await ctx.send(f"Lore item `{name}` not in the book!")
            return
        await ctx.send(f"Field `{fieldname}` removed from item `{name}`.")
        book.save()

    @lore.command()
    async def help(self, ctx):
        """Add a field to an item."""
        if is_dm(ctx.author) is False:
            await ctx.send(user_help)
            return
        await ctx.send(dm_help)


def setup(bot):
    bot.add_cog(LoreCog(bot))
