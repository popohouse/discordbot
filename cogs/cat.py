import discord
import aiohttp
import os
import json
from io import BytesIO
from discord.ext import commands, tasks
from datetime import datetime, timedelta


class CatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_cat.start()
        self.channel_id = None

    def cog_unload(self):
        self.daily_cat.cancel()


    @commands.command()
    async def cat(self, ctx):
        """ Post random cat image"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                cat = await response.json()
                await ctx.send(cat[0]['url'])

    @commands.command()
    async def dailycat(self, ctx, channel_id: int):
        """ Post cat daily at 5 utc in a specific channel, usage: !dailycat channelid"""
        self.channel_id = channel_id
        self.save_data(ctx.guild.id)
        await ctx.send(f"Daily cat posting enabled in channel {channel_id}")

    @commands.command()
    async def removedailycat(self, ctx):
        """ Remove daily cat posting for this guild"""
        # Load existing data
        with open("data/cat_data.json", "r") as f:
            data = json.load(f)
        # Remove data for this guild
        del data[str(ctx.guild.id)]
        # Save updated data
        with open("data/cat_data.json", "w") as f:
            json.dump(data, f)
        await ctx.send(f"Daily cat posting disabled for this guild")

    @tasks.loop(minutes=1)
    async def daily_cat(self):
        now = datetime.utcnow()
        if now.hour == 20 and now.minute == 56:
            if self.channel_id is not None:
                channel = self.bot.get_channel(self.channel_id)
                if channel is not None:
                    async with aiohttp.ClientSession() as session:
                        async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                            cat = await response.json()
                            cat_url = cat[0]['url']
                            file_ext = os.path.splitext(cat_url)[1]
                            async with session.get(cat_url) as resp:
                                img_data = await resp.read()
                                img_file = discord.File(BytesIO(img_data), filename=f'cat{file_ext}')
                                await channel.send("Daily cat posting", file=img_file)
    
    def save_data(self, guild_id):
        try:
            # Load existing data
            with open("data/cat_data.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create new file with empty data
            data = {}
        # Update data for this guild
        data[str(guild_id)] = {"channel_id": self.channel_id}
        # Save updated data
        with open("data/cat_data.json", "w") as f:
            json.dump(data, f)


async def setup(bot):
    await bot.add_cog(CatCog(bot))