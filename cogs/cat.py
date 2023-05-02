import discord
import aiohttp
import os
import json

from discord.ext import commands, tasks
from datetime import datetime, timedelta

class CatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_cat.start()
        self.channel_id = None
        self.load_data()

    def cog_unload(self):
        self.daily_cat.cancel()


    @commands.command()
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                cat = await response.json()
                await ctx.send(cat[0]['url'])

    @commands.command()
    async def dailycat(self, ctx, channel_id: int):
        self.channel_id = channel_id
        await ctx.send(f"Daily cat posting enabled in channel {channel_id}")

    @tasks.loop(minutes=1)
    async def daily_cat(self):
        now = datetime.utcnow()
        if now.hour == 17 and now.minute == 00:
            if self.channel_id is not None:
                channel = self.bot.get_channel(self.channel_id)
                if channel is not None:
                    async with aiohttp.ClientSession() as session:
                        async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                            cat = await response.json()
                            await channel.send(f"Daily cat posting\n{cat[0]['url']}")

    def save_data(self):
        with open("data/cat_data.json", "w") as f:
            json.dump({"channel_id": self.channel_id}, f)

    def load_data(self):
        try:
            with open("data/cat_data.json", "r") as f:
                data = json.load(f)
                self.channel_id = data["channel_id"]
        except FileNotFoundError:
            pass

async def setup(bot):
    await bot.add_cog(CatCog(bot))