import logging
import importlib.resources as pkg_resources
import os
from pathlib import Path
import toml

import shatteredbot.data
from shatteredbot.lib import paths
from shatteredbot.lib.attrdict import AttrDict
from shatteredbot.lib.pathdict import PathDict

logger = logging.getLogger("shatteredbot")

SENTINEL = object()


class ConfigError(Exception):
    pass


class ConfLoadException(Exception):
    pass


class ConfigField:
    def __init__(self, var, path, *, type=lambda v: v, default=SENTINEL, initdefault=SENTINEL):
        self.var = var
        self.path = path
        self.default = default
        self.initdefault = initdefault
        self.type = type

    def load(self, config, configDict):
        if self.default is not SENTINEL:
            val = configDict.get(self.path, SENTINEL)
            if val is SENTINEL:
                val = self.default
            else:
                val = self.type(val)
            config[self.var] = val
        else:
            config[self.var] = self.type(configDict[self.path])

    def init(self, configDict):
        if self.initdefault is not SENTINEL:
            configDict[self.path] = self.initdefault


class Config(AttrDict):
    def __init__(self, fields):
        super().__init__()
        # This avoids an infinite recursion issue with __getattr__()
        super(AttrDict, self).__setattr__("_fields", fields)

    def load(self):
        configDict = PathDict(toml.load(paths.confpath))

        try:
            for f in self._fields:
                f.load(self, configDict)
        except KeyError as e:
            raise ConfigError(f"Required configuration field not found: {e.path}")

    def init(self):
        if paths.confpath.exists():
            raise FileExistsError(f"Configuration file already exists: {paths.confpath}")
        paths.confpath.parent.mkdir(parents=True, exist_ok=True)

        configDict = PathDict()
        for f in self._fields:
            f.init(configDict)
        with open(paths.confpath, "w") as f:
            toml.dump(configDict.toDict(), f)


conf = Config([
    ConfigField("prefix", "shatteredbot.prefix", default="?"),
    ConfigField("name", "shatteredbot.name", default="The Librarian"),
    ConfigField("activity", "shatteredbot.activity", default="with realities"),
    ConfigField("authtoken", "discord.authtoken", initdefault="INSERT_BOT_TOKEN_HERE")
])


def load_conf() -> None:
    try:
        conf.load()
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e.filename}")
        confpath = Path(e.filename)
        logger.warn("Writing default settings file...")
        default_settings = pkg_resources.read_text(shatteredbot.data, "settings.ini")
        confpath.parent.mkdir(parents = True, exist_ok = True)
        with open(confpath, "w") as f:
            f.write(default_settings)
        os.startfile(confpath.parent)
        logger.info("Please reload the bot.")
        raise ConfLoadException()
