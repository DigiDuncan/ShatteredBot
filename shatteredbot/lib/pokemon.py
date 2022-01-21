import importlib.resources as pkg_resources
import json

from discord import Embed
from requests_cache import requests

import shatteredbot.data
from shatteredbot.lib.utils import intToRoman

pokemon: list["Pokemon"] = []


class Pokemon:
    def __init__(self, name: str, natdex: int = None, generation: int = None, region: str = None,
                 height: float = None, weight: float = None, types: list[str] = [], color: int = None,
                 flavor_text: str = None, sprite: str = None) -> None:
        self.name = name
        self.natdex = natdex
        self.generation = generation
        self.roman_generation = intToRoman(self.generation)
        self.region = region
        self.height = height
        self.weight = weight
        self.types = types
        self.color = color
        self.flavor_text = flavor_text
        self.sprite = sprite

    def stats_embed(self):
        h = requests.get(f"https://nizebot.bew.by/unit/SV/format?value={self.height}&system=mu").json()['formatted']
        w = requests.get(f"https://nizebot.bew.by/unit/WV/format?value={self.weight}&system=mu").json()['formatted']
        e = Embed()
        e.title = f"#{self.natdex} {self.name}"
        e.description = f"*from Generation {self.roman_generation} ({self.region})*\n\n{self.flavor_text}"
        e.add_field(name = "Height", value = h)
        e.add_field(name = "Weight", value = w)
        e.add_field(name = "Types", value = f"{', '.join(self.types)}")
        e.color = self.color
        e.set_image(url = self.sprite)
        e.set_footer(text = "Data from https://pokeapi.co/.")

        return e

    def __eq__(self, other):
        if isinstance(other, str):
            lowerName = other.lower()
            return lowerName == self.name.lower()
        elif isinstance(other, Pokemon):
            return self.name == other.name

    def __lt__(self, other):
        if isinstance(other, Pokemon):
            return self.natdex < other.natdex

    @classmethod
    def fromJson(cls, obj_json):
        c = cls(**obj_json)
        return c

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return str(self)


def init():
    global pokemon

    pokefile = pkg_resources.read_text(shatteredbot.data, "pokemon.json")
    p = json.loads(pokefile)
    pokemon = [Pokemon.fromJson(j) for j in p]
