import discord
import json
import aiohttp
import asyncio
import mcstatus
import base64
import importlib
from mcstatus import JavaServer
from decimal import Decimal, ROUND_HALF_UP

from discord import app_commands, Interaction
from discord.ext import tasks, commands
from mcstatus import JavaServer

with open("info.json") as j:
    info = json.load(j)

class Polybot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('jishaku')
        print("bot is starting")
        statuschannel.start()
        
intents = discord.Intents.default()
bot = Polybot(intents=intents, command_prefix=[])
tree = bot.tree
server = JavaServer.lookup(info["ip"])


@tasks.loop(seconds=420)
async def statuschannel():
    statuscha = bot.get_channel(1002095147779117167)
    status = server.status()
    #gets the channel to change
    if statuscha.name != "🟢 Online: {0}/7".format(status.players.online):
        await statuscha.edit(name="🟢 Online: {0}/7".format(status.players.online))
        print("done")
        
@statuschannel.before_loop
async def before_statLoop():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print("------------------")
    print('| bot is ready!! |')
    print("------------------")

@tree.command(description="Restarts bot and pulls changes")
async def restart(i: Interaction):
    importlib.reload(discord)

@tree.command(description="Syncs tree (ADMINS ONLY)")
async def sync(i: Interaction):
    try:
        await tree.sync()
        await i.response.send_message("Successfully synced tree!")
    except:
        await i.response.send_message("Could not sync tree.")


@tree.command(description="Returns nether or overworld equivalent of coords")
@app_commands.describe(dimension='Dimension to convert to')
@app_commands.choices(dimension=[
    app_commands.Choice(name='Nether', value=1),
    app_commands.Choice(name='Overworld', value=2),
])
async def portalsync(i: Interaction, dimension: int, x: float, y: float, z: float):
    if dimension == 1:
        x = Decimal(x) / Decimal(8)
        z = Decimal(z) / Decimal(8)
    if dimension == 2:
        x = x * 8
        z = z * 8
    await i.response.send_message(f"{str(x.quantize(0, ROUND_HALF_UP))}, {str(y)}, {str(z.quantize(0, ROUND_HALF_UP))}", ephemeral=True)


@tree.command(description="Returns the status of the server")
async def serverstatus(i: Interaction):
    status = server.status()
    print(f"[INFO] {i.user.display_name} requested server status.")
    try:
        if status.players.online > 0:
            players = status.players.sample
            playerlist = []
            for x in range(len(players)):
                playerlist.append(players[x].name)
            playerlist = "\n    ".join(playerlist)
            embed = discord.Embed(title="Server Status:", color=0x1ABB9B)
            embed.add_field(name="play.thepolygon.tk:25595 ",
                            value="**Version: **" + status.version.name +
                            "\n **Players**: {0}/{1}".format(
                                status.players.online, status.players.max) +
                            "\n **Player List**:\n {0}".format(playerlist))
            embed.set_footer(text="Information requested by: {0}".format(
                i.user.display_name))
            await i.response.send_message(embed=embed)
        elif status.players.online == 0:
            embed = discord.Embed(title="Server Status:", color=0x1ABB9B)
            embed.add_field(name="play.thepolygon.tk:25595 ",
                            value="**Version: **" + status.version.name +
                            "\n **Players**: 0/10")
            embed.set_footer(text="Information requested by: {0}".format(
                i.user.display_name))
            await i.response.send_message(embed=embed)
    except:
        embed = discord.Embed(title="Server Status: Offline", color=0xF63E36)
        await i.response.send_message(embed=embed)

@tree.command(description="Returns Minecraft Java skin of argument given.")
@app_commands.describe(version='Skin you want')
@app_commands.choices(version=[
    app_commands.Choice(name='Java', value=1),
    app_commands.Choice(name='Bedrock', value=2),
])
async def skin(i: Interaction, version: int, username: str):
    embed = discord.Embed(title="", color=0x1ABB9B)
    if version == 1:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.mojang.com/users/profiles/minecraft/' + username) as resp:
                mApi = await resp.json()
                UUID = mApi['id']
            async with session.get('https://sessionserver.mojang.com/session/minecraft/profile/' + UUID) as resp:
                resp = await resp.json()
                texture = resp["properties"][0]["value"]
                texture = base64.b64decode(texture)
                a = json.loads(texture)
                id = a["textures"]["SKIN"]["url"][38:]
                try:
                    isSlim = a["textures"]["SKIN"]["metadata"]["model"]
                except:
                    isSlim = ""
                if isSlim == "slim":
                    isSlim = "?alex"
                else:
                    isSlim = ""

        embed.set_author(
            name = username + "'s skin",
            url='https://namemc.com/profile/' + username, 
            icon_url=f'https://visage.surgeplay.com/face/{id}'
        )
        embed.set_thumbnail(
            url=f'https://visage.surgeplay.com/skin/{id}'
        )
        embed.set_image(
            url=f"https://visage.surgeplay.com/full/512/{id}{isSlim}"
        )
        embed.set_footer(
            text=f"Information requested by: {i.user.display_name}"
        )
    if version == 2:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.geysermc.org/v2/xbox/xuid/' + username) as resp:
                fApi = await resp.json()
                XUID = fApi['xuid']
                async with session.get('https://api.geysermc.org/v2/skin/' + str(XUID)) as resp:
                    tApi = await resp.json()
                    tId = tApi['texture_id']
                    isAlex = tApi['is_steve']
                    if isAlex:
                        isAlex = ""
                    else:
                        isAlex = "?alex"

        embed.set_author(
            name=username + "'s skin",
            icon_url='https://visage.surgeplay.com/face/' + tId
        )
        embed.set_thumbnail(
            url='https://visage.surgeplay.com/skin/' + tId
        )
        embed.set_image(
            url="https://visage.surgeplay.com/full/512/" + tId + isAlex
        )
        embed.set_footer(
            text=f"Information requested by: {i.user.display_name}"
        )
    try:
        if len(username) < 3:
            raise ValueError('Username too short')
        await i.response.send_message(embed=embed)
    except:
        embed = discord.Embed(title="🛑 Skin does not exist or invalid syntax. If you believe this is an issue please contact admins.", color=0xF63E36)
        await i.response.send_message(embed=embed)
        



@tree.command()
async def join(int: Interaction):
    embed = discord.Embed(title="**How to join The Polygon**", color=0x1ABB9B)
    embed.add_field(
        name="Java IP:",
        value="```ip: play.thepolygon.tk```",
        inline=True
    )    
    embed.add_field(
        name="Bedrock IP:",
        value="```ip: play.thepolygon.tk ```\n```port:25599```",
        inline=True
    )
    await int.response.send_message(embed=embed)


@tree.command(description="About this bot")
async def about(int: Interaction):
    embed = discord.Embed(
        title="**The official bot of The Polygon!**",
        description=
        "A bot loved and developed by <@538126187231313940>, made for The Polygon. Developed using Discord.py.",
        color=0x1ABB9B
    )
    embed.add_field(
        name="Command list:", value="```/help```",
        inline=True
    )
    embed.add_field(
        name="Command details:",
        value="```/help <command>```",
        inline=True
    )
    embed.set_author(
        name="Polybot",
        icon_url="https://cdn.discordapp.com/attachments/838602121745268756/846266695449706496/download_1.png"
    )
    embed.set_footer(
        text="Information requested by: {}".format(int.user.display_name)
    )
    await int.response.send_message(embed=embed)


@tree.command(description="Returns FAQs in #faq")
async def faq(int: Interaction, arg: str):
    try:
        #opens the faq.json file
        with open("faq.json") as faq:
            data = json.load(faq)
        #grabs the url of the faq message with the argument
        faqurl = data[arg][0]["url"]
        #fetches everything after the last / which is the message id
        faqid = faqurl[faqurl.rfind("/") + 1:]
        #gets the channel with the id
        faqid = int(faqid)
        id = 840471544739135499
        channel = bot.get_channel(id)
        #gets the message with the id
        faqmsg = await channel.fetch_message(faqid)

        #grabs the author of the faq message
        author = faqmsg.author
        #grabs the title of the message which will be between ** and ** and grabs the title along with the **s
        faqtitle = faqmsg.content[faqmsg.content.
                                  find("**"):faqmsg.content.rfind("**") + 2]
        #grabs the answer which is everything after the last **
        answer = faqmsg.content[faqmsg.content.rfind("**") + 4:]
        #opens the json which converts the user id of me, sham and siraj and converts it to our minecraft uuid
        with open("playername.json") as i:
            playernamejson = json.load(i)


#stores the user id as a variable
        authorid = author.id
        #converts the user id to the ingame uuid using 	the json file
        playername = playernamejson[str(authorid)]

        #creates a embed with the data
        embed = discord.Embed(title=faqtitle,
                              url=faqurl,
                              description=answer,
                              color=0x1ABB9B)
        embed.set_author(
            name=author,
            icon_url="https://mc-heads.net/avatar/" + playername
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/841604606743281675/846279752838283264/FAQ.png"
        )
        embed.set_footer(
            text=f"Information requested by: {int.author.display_name}"
        )
        #sends the embed
        await int.send(embed=embed)
    except:
        embed + discord.Embed(title="Could not find that faq")
        await int.send(embed=embed)

bot.run(info["token"])