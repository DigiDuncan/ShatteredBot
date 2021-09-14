import logging

from digiformatter import logger as digilogger


BANNER = None
LOGIN = None
EGG = None
CMD = None


def init_logging():
    logging.basicConfig(level=CMD)
    dfhandler = digilogger.DigiFormatterHandler()
    dfhandler.setLevel(CMD)

    logger = logging.getLogger("schedulebot")
    logger.setLevel(CMD)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(dfhandler)

    discordlogger = logging.getLogger("discord")
    discordlogger.setLevel(logging.WARN)
    discordlogger.handlers = []
    discordlogger.propagate = False
    discordlogger.addHandler(dfhandler)


def create_log_levels():
    global BANNER, LOGIN, EGG, CMD
    BANNER = digilogger.addLogLevel("banner", fg="orange_red_1", bg="deep_sky_blue_4b", attr="bold", showtime = False)
    LOGIN = digilogger.addLogLevel("login", fg="cyan")
    EGG = digilogger.addLogLevel("egg", fg="magenta_2b", bg="light_yellow", attr="bold", prefix="EGG")
    CMD = digilogger.addLogLevel("cmd", fg="grey_50", base="DEBUG", prefix="CMD")


create_log_levels()
