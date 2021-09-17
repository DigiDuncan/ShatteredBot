
import sys
import logging
import digiformatter.styles

import discord
from discord.ext.commands import Bot

import discordn

from shatteredbot import __version__
from shatteredbot.conf import ConfLoadException, conf, load_conf
from shatteredbot.lib.logger import init_logging, BANNER, CMD, LOGIN
from shatteredbot.lib.utils import truncate

init_logging()

discordn.patch()

logger = logging.getLogger(__package__)


class ScheduleBot(Bot):
    async def on_first_ready(self):
        await super().on_first_ready()

        # Print the splash screen.
        # Obviously we need the banner printed in the terminal
        banner = ("ShatteredBot " + __version__)
        logger.log(BANNER, banner)
        logger.log(LOGIN, f"Logged in as: {self.user.name} ({self.user.id})\n------")

        # More splash screen.
        print(digiformatter.styles)
        logger.info(f"Prefix: {conf.prefix}")
        logger.debug(f"ShatteredBot launched in {round((self.load_time.total_seconds() * 1000), 3)} milliseconds.\n")

    async def on_reconnect_ready(self):
        logger.error("ShatteredBot has been reconnected to Discord.")

    async def on_command(self, ctx):
        guild = truncate(ctx.guild.name, 20) if (hasattr(ctx, "guild") and ctx.guild is not None) else "DM"
        logger.log(CMD, f"G {guild}, U {ctx.message.author.name}: {ctx.message.content}")

    def on_disconnect(self):
        logger.error("ShatteredBot has been disconnected from Discord!")


def main():
    try:
        load_conf()
    except ConfLoadException:
        return

    extensions = []
    cogs = ["admin", "atsomeone", "lore", "generator", "charades", "etc", "quote"]
    extension_paths = [f"{__package__}.cogs.{c}" for c in cogs] + [f"{__package__}.extension.{e}" for e in extensions]

    # Add a special message to bot status if we are running in debug mode
    # todo: add to discordn
    activity = discord.Game(name = "with the timeline")
    if sys.gettrace() is not None:
        activity = discord.Activity(type=discord.ActivityType.listening, name = "DEBUGGER 🔧")

    bot = ScheduleBot(command_prefix = conf.prefix, extensions=extension_paths, username=conf.name, activity=activity)

    if not conf.authtoken:
        logger.error("Authentication token not found!")
        return

    bot.run(conf.authtoken)


if __name__ == "__main__":
    main()
