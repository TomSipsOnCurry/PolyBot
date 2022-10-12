import discord
import json
import aiohttp
import mcstatus
import time
import subprocess
from mcstatus import JavaServer
from decimal import Decimal, ROUND_HALF_UP

from discord import app_commands, Interaction, Client
from discord.ext import tasks

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print("------------------")
    print('| bot is ready!! |')
    print("------------------")


@tasks.loop(seconds=420)
async def statuschannel(self):
    server = JavaServer.lookup("play.thepolygon.tk:25599")
    #server status thingy
    statuscha = client.get_channel(1002095147779117167)
    try:
        status = await server.async_status()
        if statuscha.name != "🟢 Online: {0}/{1}".format(
                status.players.online, status.players.max):
            await statuscha.edit(name="🟢 Online: {0}/{1}".format(
                status.players.online, status.players.max))
    except:
        await statuscha.edit(name="🔴 Offline")

@tree.command(description="Restarts bot and pulls changes")
async def restart(i: Interaction):
    subprocess.call([r'C:\Users\User\Documents\GitHub\PolyBot\run.bat'])
    client.close()

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
async def portalsync(i: Interaction, dimension: int, x: float, y: float,
                     z: float):
    if dimension == 1:
        x = Decimal(x) / Decimal(8)
        z = Decimal(z) / Decimal(8)
        await i.response.send_message(
            f"{str(x.quantize(0, ROUND_HALF_UP))}, {str(y)}, {str(z.quantize(0, ROUND_HALF_UP))}",
            ephemeral=True)
    if dimension == 2:
        x = x * 8
        z = z * 8
        await i.response.send_message(
            f"{str(x.quantize(0, ROUND_HALF_UP))}, {str(y)}, {str(z.quantize(0, ROUND_HALF_UP))}",
            ephemeral=True)


@tree.command(description="Returns the status of the server")
async def serverstatus(int: Interaction):
    try:
        server = JavaServer.lookup("play.thepolygon.tk:25599")
        status = server.status()
        print(status)
        if status.players.online > 0:
            players = status.players.sample
            print(players)
            print(status.players.online)
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
                int.user.display_name))
            await int.response.send_message(embed=embed)
        elif status.players.online == 0:
            embed = discord.Embed(title="Server Status:", color=0x1ABB9B)
            embed.add_field(name="play.thepolygon.tk:25595 ",
                            value="**Version: **" + status.version.name +
                            "\n **Players**: 0/7")
            embed.set_footer(text="Information requested by: {0}".format(
                int.user.display_name))
            await int.response.send_message(embed=embed)
    except:
        embed = discord.Embed(title="Server Status: Offline", color=0xF63E36)
        await int.response.send_message(embed=embed)


@tree.command(description="Returns Minecraft Java skin of argument given.")
@app_commands.describe(version='Dimension to convert to')
@app_commands.choices(version=[
    app_commands.Choice(name='Java', value=1),
    app_commands.Choice(name='Bedrock', value=2),
])
async def skin(int: Interaction, version: int, username: str):
    embed = discord.Embed(title="", color=0x1ABB9B)
    if version == 1:
        embed.set_author(name=username + "'s skin",url='https://namemc.com/profile/' + username, icon_url='https://api.creepernation.xyz/avatar/' + username)
        embed.set_thumbnail(url='https://mc-heads.net/skin/' + username)
        embed.set_image(url="https://api.creepernation.xyz/body/" + username)
        embed.set_footer(text="Information requested by: {}".format(int.user.display_name))
    if version == 2:
        embed.set_author(name=username + "'s skin"+ username, icon_url='https://api.creepernation.xyz/avatar/' + username)
        #embed.set_thumbnail(url='https://mc-heads.net/skin/' + username)
        embed.set_image(url="https://api.creepernation.xyz/body/" + username)
        embed.set_footer(text="Information requested by: {}".format(int.user.display_name))    
    await int.response.send_message(embed=embed)


@tree.command()
async def join(int: Interaction):
    embed = discord.Embed(title="**How to join The Polygon**", color=0x1ABB9B)
    embed.add_field(name="Java IP:",
                    value="```ip: play.thepolygon.tk:25595```",
                    inline=True)
    embed.add_field(name="Bedrock IP:",
                    value="```ip: play.thepolygon.tk ```\n```port:25595```",
                    inline=True)
    await int.response.send_message(embed=embed)


@tree.command(description="About this bot")
async def about(int: Interaction):
    embed = discord.Embed(
        title="**The official bot of The Polygon!**",
        description=
        "A bot loved and developed by <@538126187231313940>, made for The Polygon. Developed using Discord.py.",
        color=0x1ABB9B)
    embed.add_field(name="Command list:", value="```!help```", inline=True)
    embed.add_field(name="Command details:",
                    value="```!help <command>```",
                    inline=True)
    embed.set_author(
        name="Polybot",
        icon_url=
        "https://cdn.discordapp.com/attachments/838602121745268756/846266695449706496/download_1.png"
    )
    embed.set_footer(
        text="Information requested by: {}".format(int.user.display_name))
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
        channel = client.get_channel(id)
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
        embed.set_author(name=author,
                         icon_url="https://mc-heads.net/avatar/" + playername)
        embed.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/841604606743281675/846279752838283264/FAQ.png"
        )
        embed.set_footer(text="Information requested by: {}".format(
            int.author.display_name))
        #sends the embed
        await int.send(embed=embed)
    except:
        embed + discord.Embed(title="Could not find that faq")
        await int.send(embed=embed)
with open("sensitive.json") as j:
    sInfo = json.load(j)
client.run(sInfo["token"])
