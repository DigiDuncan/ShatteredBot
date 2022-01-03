import importlib.resources as pkg_resources
import shatteredbot.data.wordlists as wordlists


def get_wordlist(name):
    text = pkg_resources.read_text(wordlists, f"{name}.txt")
    l = text.split("\n")
    l.remove("")
    return l
