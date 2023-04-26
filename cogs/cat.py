import discord
from discord.ext import commands, tasks
import aiohttp
import os
import json

class CatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_cat.start()
        self.channel_id = None
        self.load_data()

    def cog_unload(self):
        self.daily_cat.cancel()

    @commands.group(invoke_without_command=True)
    async def cat(self, ctx, *, subcommand=None):
        if subcommand is None:
            url = 'https://cataas.com/cat'
        else:
            url = f'https://cataas.com/cat/{subcommand}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not get cat image :(')
                data = await resp.read()
                content_type = resp.headers['Content-Type']
                extension = content_type.split('/')[-1]
                filename = f'cat.{extension}'
                with open(filename,'wb') as f:
                    f.write(data)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)

    @commands.command()
    async def dailycat(self, ctx, channel_id: int):
        self.channel_id = channel_id
        self.save_data()
        await ctx.send(f"Daily cat posting enabled in channel {channel_id}")

    @tasks.loop(hours=24)
    async def daily_cat(self):
        if self.channel_id is not None:
            channel = self.bot.get_channel(self.channel_id)
            if channel is not None:
                url = 'https://cataas.com/cat'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            return await channel.send('Could not get cat image :(')
                        data = await resp.read()
                        content_type = resp.headers['Content-Type']
                        extension = content_type.split('/')[-1]
                        filename = f'cat.{extension}'
                        with open(filename,'wb') as f:
                            f.write(data)
                await channel.send("Daily cat posting", file=discord.File(filename))
                os.remove(filename)

    def save_data(self):
        with open("cat_data.json", "w") as f:
            json.dump({"channel_id": self.channel_id}, f)

    def load_data(self):
        try:
            with open("cat_data.json", "r") as f:
                data = json.load(f)
                self.channel_id = data["channel_id"]
        except FileNotFoundError:
            pass

async def setup(bot):
    await bot.add_cog(CatCog(bot))