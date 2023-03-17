import discord
import asyncio

bars = ['⬛⬛⬛⬛', '⬜⬛⬛⬛', '⬜⬜⬛⬛', '⬜⬜⬜⬛', '⬜⬜⬜⬜']

class Progress:
    def __init__(self, channel):
        self.channel = channel
        self.message = None
        self.progress = None

    async def init(self):
        self.progress = 1
        embed = discord.Embed(color=0x666666)
        embed.add_field(name="Processing", value=bars[self.progress], inline=False)
        file = discord.File("loading.gif", filename="loading.gif")
        embed.set_thumbnail(url="attachment://loading.gif")
        self.message = await self.channel.send(file=file, embed=embed)
    async def increase(self, n = 1):
        self.progress += n
        embed = discord.Embed(color=0x666666)
        embed.add_field(name="Processing", value=bars[self.progress], inline=False)
        file = discord.File("loading.gif", filename="loading.gif")
        embed.set_thumbnail(url="attachment://loading.gif")
        await self.message.edit(embed=embed)
    async def end(self):
        await self.message.delete()
