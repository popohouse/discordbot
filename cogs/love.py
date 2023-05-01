import discord
from discord.ext import commands
import aiohttp
import os
from io import BytesIO

class Love(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kiss(self, ctx, *, target: discord.Member=None):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/kiss') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'kiss{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} kissed themself!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} kisses {target.mention}!', file=image_file)

    @commands.command()
    async def hug(self, ctx, *, target: discord.Member=None):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/hug') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'kiss{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} hugs themself!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} hugs {target.mention}!', file=image_file)

async def setup(bot):
    await bot.add_cog(Love(bot))