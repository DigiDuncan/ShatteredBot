import random

import logging

from atsomeone.conf import conf

logger = logging.getLogger("atsomeone")


def dont_want_pings(u):
    return any(True for r in u.roles if r.name == conf.blacklist_role)


async def on_ping(bot, m):
    """Ping listener."""
    if m.author.bot:
        return
    if bot.user in m.mentions:
        pingables = [u for u in m.guild.members if u.bot is False and not dont_want_pings(u) and u not in m.mentions]
        randomuser = random.choice(pingables)
        await m.channel.send(randomuser.mention)
        logger.info(f"Pinged {randomuser.display_name}, blame {m.author.display_name}.")
        if randomuser == m.author:
            await m.channel.send("Congratulations. You played yourself.")
            logger.info("You played yourself.")
