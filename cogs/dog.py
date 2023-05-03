import discord
import aiohttp
import os
import json
from io import BytesIO
from discord.ext import commands, tasks
from datetime import datetime, timedelta


class AnimalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None

    @commands.command()
    async def dog(self, ctx):
        """ Post random dog image"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random.dog/woof.json') as response:
                dog = await response.json()
                await ctx.send(dog['url'])

    @commands.command()
    async def fox(self, ctx):
        """ Post random fox image"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://randomfox.ca/floof/') as response:
                fox = await response.json()
                await ctx.send(fox['image'])

    @commands.command()
    async def duck(self, ctx):
        """ Post random duck image"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random-d.uk/api/random') as response:
                duck = await response.json()
                await ctx.send(duck['url'])

async def setup(bot):
    await bot.add_cog(AnimalCog(bot))