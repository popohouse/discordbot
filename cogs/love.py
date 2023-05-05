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
        """ Get kissed, or kiss a user"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/kiss') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'kiss{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} gets kissed!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} kisses {target.mention}!', file=image_file)

    @commands.command()
    async def hug(self, ctx, *, target: discord.Member=None):
        """ Get hugged, or hug a user"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/hug') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'hug{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} gets hugged!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} hugs {target.mention}!', file=image_file)

    @commands.command()
    async def cuddle(self, ctx, *, target: discord.Member=None):
        """ Get cuddled, or cuddle a user"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/cuddle') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'cuddle{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} gets cuddled!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} cuddles {target.mention}!', file=image_file)

    @commands.command()
    async def bonk(self, ctx, *, target: discord.Member=None):
        """ Bonk, or bonk a user"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/bonk') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'bonk{file_ext}')
        if target is None:
            await ctx.send(f'BONK!', file=image_file)
        else:
            await ctx.send(f'BONK! {target.mention}!', file=image_file)            
            
    @commands.command()
    async def slap(self, ctx, *, target: discord.Member=None):
        """ Get slapped, or slap a user"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/slap') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'slaps{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} gets slapped!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} slaps {target.mention}!', file=image_file)

    @commands.command()
    async def wink(self, ctx, *, target: discord.Member=None):
        """ Wink, or wink at a user"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/wink') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'wink{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} winks!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} winks at {target.mention}!', file=image_file)

    @commands.command()
    async def pat(self, ctx, *, target: discord.Member=None):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/pat') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'pat{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} gets headpats!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} gives headpats to {target.mention}!', file=image_file)

    @commands.command()
    async def blow(self, ctx, *, target: discord.Member=None):
        """ Owner only meme command"""
        UserBlowId = '178753677278838785'
        async with aiohttp.ClientSession() as session:
            if str(ctx.author.id) != UserBlowId:
                await ctx.send("Try being popo lmfao")
                return
            
            async with session.get('https://api.waifu.pics/nsfw/blowjob') as response:
                data = await response.json()
                image_url = data['url']
                file_ext = os.path.splitext(image_url)[1]
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
                    image_file = discord.File(BytesIO(image_data), filename=f'blowjob{file_ext}')
        if target is None:
            await ctx.send(f'{ctx.author.mention} gets blowjob!', file=image_file)
        else:
            await ctx.send(f'{ctx.author.mention} gives blowjob to {target.mention}!', file=image_file)

async def setup(bot):
    await bot.add_cog(Love(bot))