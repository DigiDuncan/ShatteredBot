import re
import requests
import importlib.resources as pkg_resources

from bs4 import BeautifulSoup
import difflib

import discord
from discord.ext import commands

import shatteredbot.data

hdr = {'User-Agent': 'Mozilla/5.0'}
loadingemoji = "<a:loading:650449888684933166>"
gamecubelogo = "https://media.discordapp.net/attachments/650460192009617433/650460502933241876/gamecubeicon.png"
wiilogo = "https://media.discordapp.net/attachments/650460192009617433/650460511070060574/wiiicon.png"
homebrewlogo = "https://media.discordapp.net/attachments/650460192009617433/650475421439229953/homebrewicon.jpg"
gametdblogo = "https://media.discordapp.net/attachments/650460192009617433/650460504644517926/gametdb.png"
vclogo = "https://media.discordapp.net/attachments/650460192009617433/650475423343575080/vcicon.png"
qmark = "https://media.discordapp.net/attachments/650460192009617433/650476654669594635/questionmark.png"


def getWiiAttribute(soup, attr):
    # Find the GameData table, then it's first table data to match the attribute.
    lookup = soup.find("table", class_="GameData").find("td", string=attr)
    # Attributes sometimes have "\n"s because this HTML is dumb.
    if lookup is None:
        lookup = soup.find("table", class_="GameData").find("td", string=attr + "\n")
    # If we still can't find it, the attribute doesn't exist. Return a Unknown.
    if lookup is None:
        return "Unknown"
    # The attributes value is in the next sibling,
    returnattr = lookup.next_sibling
    # If the the value doesn't exist, return a Unknown.
    if returnattr is None:
        return "Unknown"

    # Get rid of "\n"s in the raw HTML for this chunk (which should include the value we want.)
    attrstring = str(returnattr).replace("\n", "")
    # Parse HTML with regex ;)
    if re.search(">(.*?)<", attrstring) is not None:
        return re.search(">(.*?)<", attrstring).group(1)
    # If we STILL can't find it, return a Unknown.
    return "Unknown"


def getWiiAttributes(GAMEID):
    # Get the soup for the page of the game we want.
    response = requests.get(f"https://www.gametdb.com/Wii/{GAMEID}", headers=hdr)
    soup = BeautifulSoup(response.content, "html.parser")

    # Build a dictionary of arrtibutes.

    attrdict = {}
    for key in ("ID", "name", "region", "type", "langauges", "synopsis", "developer", "publisher",
                "date", "genre", "rating", "cover", "icon", "color"):
        attrdict[key] = "Unknown"

    attrdict['ID'] = GAMEID
    attrdict['name'] = getWiiAttribute(soup, "title (EN)")
    if attrdict['name'] == "Unknown":
        attrdict['name'] = getWiiAttribute(soup, "title (JA)")  # Fallback to the JP title.
    attrdict['region'] = getWiiAttribute(soup, "region")
    attrdict['type'] = getWiiAttribute(soup, "type")
    attrdict['languages'] = getWiiAttribute(soup, "languages")
    attrdict['synopsis'] = getWiiAttribute(soup, "synopsis (EN)")
    if attrdict['synopsis'] == "Unknown":
        attrdict['synopsis'] = getWiiAttribute(soup, "synopsis (JA)")  # Fallback to the JP synposis.
    attrdict['developer'] = getWiiAttribute(soup, "developer")
    attrdict['publisher'] = getWiiAttribute(soup, "publisher")
    attrdict['date'] = getWiiAttribute(soup, "release date")
    attrdict['genre'] = getWiiAttribute(soup, "genre")
    attrdict['rating'] = getWiiAttribute(soup, "rating")
    attrdict['cover'] = f"https://art.gametdb.com/wii/cover/US/{GAMEID}.png"

    # Set the color and console icon of this game (purple for GameCube, "azurish white" for Wii,
    # black for custom/homebrew, cyan for VC, red for other.)
    if attrdict['type'].lower() == "gamecube":
        attrdict['icon'] = gamecubelogo
        attrdict['color'] = discord.Color.from_rgb(100, 80, 151)
    elif attrdict['type'].lower() == "wii":
        attrdict['icon'] = wiilogo
        attrdict['color'] = discord.Color.from_rgb(219, 233, 244)
    elif attrdict['type'].lower() == "homebrew" or attrdict['type'].lower() == "custom":
        attrdict['icon'] = homebrewlogo
        attrdict['color'] = discord.Color.from_rgb(0, 0, 0)
    elif attrdict['type'].lower() == "virtual console" or attrdict['type'].lower().startswith("vc"):
        attrdict['icon'] = vclogo
        attrdict['color'] = discord.Color.from_rgb(27, 183, 235)
    else:
        attrdict['icon'] = qmark
        attrdict['color'] = discord.Color.from_rgb(200, 0, 0)

    for k in attrdict:
        if attrdict[k] == "":
            attrdict[k] = "Unknown"

    return attrdict


def getPriorityGame(gameidmatches):
    matchregions = {}
    for game in gameidmatches:
        matchattrs = getWiiAttributes(game)
        if matchattrs['region'] == "PAL":
            if "EN" in matchattrs['languages']:
                matchregions[game] = "PAL-EN"
            else:
                matchregions[game] = "PAL"
        elif matchattrs['region'] == "NTSC-U":
            matchregions[game] = "US"
        elif matchattrs['region'] == "NTSC-J":
            matchregions[game] = "JP"
        else:
            matchregions[game] = "OTHER"
    for region in ('US', 'PAL-EN', 'NTSC-J', 'PAL', 'OTHER'):
        for k, v in matchregions.items():
            if v == region:
                return k
    return None  # Should never happen.


# Make a dictionary of all game IDs and their corrosponding titles.
wiidictionary = {}
wiidb = pkg_resources.read_text(shatteredbot.data, "wiidb.txt")
lines = wiidb.splitlines()
for line in lines:
    splitline = line.split(" = ")
    wiidictionary[splitline[0]] = splitline[1].strip()


class WiiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wiisearch(self, ctx, *, searchterm: str):
        initialmessage = await ctx.send(f"{loadingemoji} Processing {ctx.message.author.name}'s Wii search...")

        gameid = ""
        if searchterm.upper() in wiidictionary.keys():
            # The searchterm is a Game ID.
            # Format the game ID.
            gameid = searchterm.upper()
        else:
            # The searchterm is a game name (or approximant.)
            if searchterm in wiidictionary.values():
                gametosearch = searchterm
            else:
                gametosearch = difflib.get_close_matches(searchterm, wiidictionary.values(), cutoff = 0.001)[0]
            if gametosearch is None:
                await ctx.send("That Wii or GameCube title doesn't seem to exist. (This search is being improved.)")
                return
            gameidmatches = []
            for k, v in wiidictionary.items():
                if v == gametosearch:
                    gameidmatches.append(k)
            gameid = getPriorityGame(gameidmatches)

        # Get the attributes of the game based on its ID.
        gameattrs = getWiiAttributes(gameid)
        print(gameattrs)

        # Build the embed.
        embed = discord.Embed(title = f"{gameattrs['name']} [{gameid}]", description = gameattrs["synopsis"], color = gameattrs["color"])
        embed.set_author(name = f"{self.bot.user.name} - $wiisearch", icon_url = gameattrs["icon"])
        embed.set_footer(text = ctx.message.author.name, icon_url = ctx.message.author.avatar_url)
        embed.set_image(url = gameattrs["cover"])
        embed.set_thumbnail(url = gametdblogo)
        embed.add_field(name = "Console", value = gameattrs["type"], inline = True)
        embed.add_field(name = "Region", value = gameattrs["region"])
        embed.add_field(name = "Languages", value = gameattrs["languages"])
        embed.add_field(name = "Developer", value = gameattrs["developer"])
        embed.add_field(name = "Publisher", value = gameattrs["publisher"])
        embed.add_field(name = "Genre", value = gameattrs["genre"])
        embed.add_field(name = "ESRB/PEGI Rating", value = gameattrs["rating"])
        embed.add_field(name = "Release Date", value = gameattrs["date"])

        # Delete the loading message.
        await initialmessage.delete()
        # Send the embed.
        await ctx.send(f"<@{ctx.message.author.id}>", embed = embed)


def setup(bot):
    bot.add_cog(WiiCog(bot))
