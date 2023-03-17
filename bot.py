# bot.py
import os

import discord
import requests
from PIL import Image
from discord.ext import commands
from discord_components import ButtonStyle
from nbtschematic import SchematicFile

from armour_analysis import armour_test
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from dotenv import load_dotenv

import embeds
from progress import Progress
from schempic import gen_pic_schem
from ship_stats import Ship

import discord_components

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="/", intents=intents)
slash = SlashCommand(client, sync_commands=True)

sieges = []
with open('sieges.txt') as f:
    for line in f:
        sieges.append(line.split())


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'{client.user} is connected to the following guilds:')
    for guild in client.guilds:
        print(f'- {guild.name}(id: {guild.id})')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('.test'):
        return
    if not message.attachments:
        return
    url = message.attachments[0].url
    if not url.split('.')[-1] == 'schematic':
        return
    if not message.content.startswith('.'):
        return
    if not (message.content.startswith('.pic') or
            message.content.startswith('.specs') or
            message.content.startswith('.firetest') or
            message.content.startswith('.armourtest') or
            message.content.startswith('.holetest')):
        await message.channel.send('Unknown command')
        return
    p = Progress(message.channel)
    await p.init()

    cnt = message.content
    scale = 16
    shade = 10
    light = 0
    if cnt.startswith('.pic'):
        await p.increase()
        parms = cnt.replace('.pic', '', 1)
        parms = parms.strip()
        scale = 16
        shade = 30
        light = 10
        for parm in parms.split(','):
            items = parm.split(':')
            if items[0] == 'scale':
                try:
                    scale = int(items[-1])
                except ValueError:
                    await message.channel.send('Parameter "scale" must be an integer')
                    await p.end()
                    return
            if items[0] == 'shade':
                try:
                    shade = int(items[-1])
                except ValueError:
                    await message.channel.send('Parameter "shade" must be an integer')
                    await p.end()
                    return
            if items[0] == 'light':
                try:
                    light = float(items[-1])
                except ValueError:
                    await message.channel.send('Parameter "light" must be a number')
                    await p.end()
                    return
    file = url.split('/')[-1]
    name = ''.join(file.split('.')[:-1])
    print(str(message.author) + " used " + cnt + "<" + url)
    r = requests.get(url, allow_redirects=True)
    with open('schems/' + file, 'wb') as schemFile:
        schemFile.write(r.content)
    sf = SchematicFile.load('schems/' + file)
    if sf.shape[0] * sf.shape[1] * sf.shape[2] > 8000000:
        await message.channel.send('This schem is too big. Limit is 8000000 blocks.')
        return
    gen_pic_schem(schem=sf, name=name, scale=scale, shade=shade, light=light)
    if cnt.startswith('.pic'):
        await message.channel.send(file=discord.File("pics/" + name + "+y.png"))
        await message.channel.send(file=discord.File("pics/" + name + "-y.png"))
        await message.channel.send(file=discord.File("pics/" + name + "+x.png"))
        await message.channel.send(file=discord.File("pics/" + name + "-x.png"))
        await message.channel.send(file=discord.File("pics/" + name + "+z.png"))
        await message.channel.send(file=discord.File("pics/" + name + "-z.png"))
        await message.channel.send(file=discord.File("pics/" + name + "+dx.png"))
        await message.channel.send(file=discord.File("pics/" + name + "-dx.png"))
        await message.channel.send(file=discord.File("pics/" + name + "+dz.png"))
        await message.channel.send(file=discord.File("pics/" + name + "-dz.png"))
    elif cnt.startswith('.specs'):
        await p.increase(2)
        ss = Ship(path='schems/' + file)
        ss.map()
        embed = discord.Embed(title=ss.name,
                              color=0x666666)
        file = discord.File("pics/" + name + "+y.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        embed.add_field(name="Size", value=str(ss.size()), inline=False)
        embed.add_field(name="Lift", value=str(ss.lift()), inline=False)
        embed.add_field(name="Internal Lift", value=str(ss.internal_lift()), inline=False)
        embed.add_field(name="Engines", value=str(ss.engines()), inline=False)
        await message.channel.send(file=file, embed=embed)
    elif cnt.startswith('.firetest'):
        await p.increase()
        ss = Ship(path='schems/' + file)
        ss.map()
        depth = ss.fire_depth()
        if depth == 0:
            embed = discord.Embed(title='Fire Test',
                                  color=0x00FF00)
            embed.add_field(name="No issues found", value='This is fine', inline=False)
            await message.channel.send(embed=embed)
        else:
            await p.increase()
            embed = discord.Embed(title='Fire Test')
            if depth < 3:
                embed.color = 0xFFA500
                embed.add_field(name="Moderate issues found", value='There appears to be some double exterior flammables',
                                inline=False)
            else:
                embed.color = 0xFF0000
                embed.add_field(name="Severe issues found",
                                value='Some holes appear to be present',
                                inline=False)
            ss.fire_test()
            await message.channel.send(embed=embed)
            for suffix in ['+y', '-y', '+x', '-x', '+z', '-z']:
                new_img = Image.open("pics/" + name + suffix + ".png")
                new_img.putalpha(128)
                new_img.paste(Image.open("pics/" + name + "-firetest" + suffix + ".png"),
                              (0, 0),
                              Image.open("pics/" + name + "-firetest" + suffix + ".png"))
                new_img.save("temp/fireblend.png", "PNG")
                await message.channel.send(file=discord.File("temp/fireblend.png"))
            await message.channel.send(file=discord.File("temp/-firetest.schematic"))
    elif cnt.startswith('.armourtest'):
        await p.increase()
        ss = Ship(path='schems/' + file)
        ss.map()
        await p.increase()
        await armour_test(ss)
        embed = discord.Embed(title='Armour Test')
        embed.color = 0x666666
        file = discord.File("color_armour.png", filename="color_armour.png")
        embed.set_image(url="attachment://color_armour.png")
        await message.channel.send(embed=embed, file=file)
        for suffix in ['x', 'y', 'z']:
            new_img = Image.open("pics/" + name + "+" + suffix + ".png")
            new_img.putalpha(128)
            new_img.paste(Image.open("temp/armour_" + suffix + ".png"),
                          (0, 0),
                          Image.open("temp/armour_" + suffix + ".png"))
            new_img.save("temp/armourblend" + suffix + ".png", "PNG")
            await message.channel.send(file=discord.File("temp/armourblend" + suffix + ".png"))
        await message.channel.send(file=discord.File("temp/-armourtest.schematic"))
    elif cnt.startswith('.holetest'):
        await p.increase()
        ss = Ship(path='schems/' + file)
        ss.map()
        await p.increase()
        hl = ss.hole_test()
        embed = discord.Embed(title='Hole Test',
                              color=0x666666)
        embed.add_field(name="Air blocks found", value=str(hl), inline=False)
        await message.channel.send(embed=embed)
        for suffix in ['+y', '-y', '+x', '-x', '+z', '-z']:
            new_img = Image.open("pics/" + name + suffix + ".png")
            new_img.putalpha(128)
            new_img.paste(Image.open("pics/" + name + "-holetest" + suffix + ".png"),
                          (0, 0),
                          Image.open("pics/" + name + "-holetest" + suffix + ".png"))
            new_img.save("temp/holeblend.png", "PNG")
            await message.channel.send(file=discord.File("temp/holeblend.png"))
        await message.channel.send(file=discord.File("temp/-holetest.schematic"))
    await p.end()

# @client.event
# async def on_message(message):
#    if message.author == client.user:
#        return
#    if "owo" in message.content.lower() or "uwu" in message.content.lower():
#        newmessage = owoify(message.content)
#        await message.delete()
#        await message.channel.send(newmessage)

@slash.slash(name="help",
             description="Bot help.")
async def slashhelp(ctx):
    embed = discord.Embed(title='QuarkBot Help',
                          color=0x666666,)
    embed.set_thumbnail(url=client.user.avatar_url)
    embed.add_field(name="General commands", value='Read command descriptions.', inline=False)
    embed.add_field(name="Schematics",
                    value='Send a .schematic file in any channel typing while you send one of the commands:\n'
                          '   .pic [scale:16,shade:10,light:0] :for a pixel art of the ship\n'
                          "   .specs or .stats :for the ship's specs\n"
                          '   .firetest :to run a fire test\n'
                          '   .armourtest :to run an armour test\n'
                          '   .holetest :to check for air pockets inside the ship', inline=False)
    await ctx.send(embed=embed)


@slash.slash(name="owoify",
             description="Owoify a message.",
             options=[
                 create_option(
                     name="message",
                     description="Message to be owoified.",
                     option_type=3,
                     required=True
                 )
             ])
async def slashowoify(ctx, message: str):
    newmessage = owoify(message)
    await ctx.send(content=newmessage)


@slash.slash(name="siege",
             description="Check siege info.",
             options=[
                 create_option(
                     name="airspace",
                     description="Airspace name.",
                     option_type=3,
                     required=True,
                     choices=[(lambda x: create_choice(name=x[0].replace("_", " "), value=x[0]))(x) for x in sieges]
                 )
             ])
async def slashsiege(ctx, airspace: str):
    arr = []
    for x in sieges:
        if x[0] == airspace:
            arr = x
    await ctx.send(embed=embeds.siegeembed(client, arr))


@slash.slash(name="map",
             description="AP map link.")
async def slashmap(ctx):
    await ctx.send(content="https://docs.google.com/drawings/d/18JdW8zsM-FlOvbtnvhqnfGOEiLBnS7VH0g2clIaK74w/edit")


#@slash.slash(name="tickets",
#             description="Your tickets.")
#async def slashtickets(ctx):
#    await ctx.send(embed=embeds.ticketembed(ctx.author))


def owoify(message: str):
    newmessage = message
    newmessage = newmessage.replace("r", "w")
    newmessage = newmessage.replace("l", "w")
    newmessage = newmessage.replace("i", "iw")
    newmessage = newmessage.replace("ns", "wns")
    newmessage = newmessage.replace("ps", "wps")
    newmessage = newmessage.replace("ms", "wms")
    newmessage = newmessage.replace("vs", "wvs")
    newmessage = newmessage.replace("R", "W")
    newmessage = newmessage.replace("L", "W")
    newmessage = newmessage.replace("I", "IW")
    newmessage = newmessage.replace("NS", "WNS")
    newmessage = newmessage.replace("PS", "WPS")
    newmessage = newmessage.replace("MS", "WMS")
    newmessage = newmessage.replace("VS", "WVS")
    return newmessage


client.run(TOKEN)
