from pathlib import Path

import appdirs


def getDataDir():
    appname = "ShatteredBot"
    appauthor = "DigiDuncan"
    datadir = Path(appdirs.user_data_dir(appname, appauthor))
    return datadir


# File paths
datadir = getDataDir()
confpath = datadir / "shatteredbot.conf"
lorepath = datadir / "lore.json"
