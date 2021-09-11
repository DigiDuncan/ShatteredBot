import importlib.resources as pkg_resources
import os
import logging
import sys
from datetime import datetime
from pathlib import Path

import discord
from discord.ext.commands import Bot

from digiformatter import styles, logger as digilogger

import shatteredbot.data
from shatteredbot import __version__
from shatteredbot import discordplus
from shatteredbot.conf import conf
from shatteredbot.lib import paths
from shatteredbot.lib.loglevels import BANNER, LOGIN, CMD
from shatteredbot.lib.utils import truncate
from shatteredbot.plugins import pinglistener

logging.basicConfig(level=CMD)
dfhandler = digilogger.DigiFormatterHandler()
dfhandler.setLevel(CMD)

logger = logging.getLogger("shatteredbot")
logger.setLevel(CMD)
logger.handlers = []
logger.propagate = False
logger.addHandler(dfhandler)

initial_cogs = ["admin", "atsomeone", "lore", "dumb"]
initial_extensions = []

discordplus.patch()


def initConf():
    print("Initializing configuration file")
    try:
        conf.init()
        print(f"Configuration file initialized: {paths.confpath}")
    except FileExistsError as e:
        print(e)
        pass
    os.startfile(paths.confpath.parent)


def main():
    try:
        conf.load()
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e.filename}")
        logger.warn("Writing default settings file...")
        default_settings = pkg_resources.read_text(shatteredbot.data, "settings.ini")
        Path(e.filename).parent.mkdir(parents = True, exist_ok = True)
        with open(e.filename, "w") as f:
            f.write(default_settings)
        logger.info("Please reload the bot.")
        return

    launchtime = datetime.now()

    bot = Bot(command_prefix = conf.prefix, intents=discord.Intents.all())

    for extension in initial_extensions:
        bot.load_extension("shatteredbot.extensions." + extension)
    for cog in initial_cogs:
        bot.load_extension("shatteredbot.cogs." + cog)

    @bot.event
    async def on_first_ready():
        # Set the bots name to what's set in the config.
        try:
            await bot.user.edit(username = conf.name)
        except discord.errors.HTTPException:
            logger.warn("We can't change the username this much!")

        # Print the splash screen.
        # Obviously we need the banner printed in the terminal
        banner = ("shatteredbot " + __version__)
        logger.log(BANNER, banner)
        logger.log(LOGIN, f"Logged in as: {bot.user.name} ({bot.user.id})\n------")

        # Add a special message to bot status if we are running in debug mode
        activity = discord.Game(name = "traversing realities")
        if sys.gettrace() is not None:
            activity = discord.Activity(type=discord.ActivityType.listening, name = "DEBUGGER 🔧")

        # More splash screen.
        await bot.change_presence(activity = activity)
        print(styles)
        logger.info(f"Prefix: {conf.prefix}")
        launchfinishtime = datetime.now()
        elapsed = launchfinishtime - launchtime
        logger.debug(f"shatteredbot launched in {round((elapsed.total_seconds() * 1000), 3)} milliseconds.\n")

    @bot.event
    async def on_reconnect_ready():
        logger.error("shatteredbot has been reconnected to Discord.")

    @bot.event
    async def on_command(ctx):
        guild = truncate(ctx.guild.name, 20) if hasattr(ctx, "guild") else "DM"
        logger.log(CMD, f"G {guild}, U {ctx.message.author.name}: {ctx.message.content}")

    @bot.event
    async def on_message(message):
        # F*** smart quotes.
        message.content = message.content.replace("“", "\"")
        message.content = message.content.replace("”", "\"")
        message.content = message.content.replace("’", "'")
        message.content = message.content.replace("‘", "'")

        await pinglistener.on_ping(bot, message)

        await bot.process_commands(message)

    @bot.event
    async def on_message_edit(before, after):
        if before.content == after.content:
            return
        await bot.process_commands(after)

    def on_disconnect():
        logger.error("shatteredbot has been disconnected from Discord!")

    if not conf.authtoken:
        logger.error("Authentication token not found!")
        return

    bot.run(conf.authtoken)
    on_disconnect()


if __name__ == "__main__":
    main()
