import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from io import BytesIO


###todo
#Use pool version of aiohttp
class Love(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def kiss(self, interaction: discord.Interaction, *, target: discord.Member=None):
        """Get kissed, or kiss a user"""
        async with aiohttp.ClientSession() as session, session.get('https://api.waifu.pics/sfw/kiss') as response:
            data = await response.json()
            image_url = data['url']
            file_ext = os.path.splitext(image_url)[1]
            async with session.get(image_url) as resp:
                image_data = await resp.read()
                image_file = discord.File(BytesIO(image_data), filename=f'kiss{file_ext}')
        if target is None:
            await interaction.response.send_message(f'{interaction.user.mention} gets kissed!', file=image_file)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} kisses {target.mention}!', file=image_file)

    @app_commands.command()
    async def hug(self, interaction: discord.Interaction, *, target: discord.Member=None):
        """Get hugged, or hug a user"""
        async with aiohttp.ClientSession() as session, session.get('https://api.waifu.pics/sfw/hug') as response:
            data = await response.json()
            image_url = data['url']
            file_ext = os.path.splitext(image_url)[1]
            async with session.get(image_url) as resp:
                image_data = await resp.read()
                image_file = discord.File(BytesIO(image_data), filename=f'hug{file_ext}')
        if target is None:
            await interaction.response.send_message(f'{interaction.user.mention} gets hugged!', file=image_file)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} hugs {target.mention}!', file=image_file)

    @app_commands.command()
    async def cuddle(self, interaction: discord.Interaction, *, target: discord.Member=None):
        """Get cuddled, or cuddle a user"""
        async with aiohttp.ClientSession() as session, session.get('https://api.waifu.pics/sfw/cuddle') as response:
            data = await response.json()
            image_url = data['url']
            file_ext = os.path.splitext(image_url)[1]
            async with session.get(image_url) as resp:
                image_data = await resp.read()
                image_file = discord.File(BytesIO(image_data), filename=f'cuddle{file_ext}')
        if target is None:
            await interaction.response.send_message(f'{interaction.user.mention} gets cuddled!', file=image_file)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} cuddles {target.mention}!', file=image_file)

    @app_commands.command()
    async def bonk(self, interaction: discord.Interaction, *, target: discord.Member=None):
        """Bonk, or bonk a user"""
        async with aiohttp.ClientSession() as session, session.get('https://api.waifu.pics/sfw/bonk') as response:
            data = await response.json()
            image_url = data['url']
            file_ext = os.path.splitext(image_url)[1]
            async with session.get(image_url) as resp:
                image_data = await resp.read()
                image_file = discord.File(BytesIO(image_data), filename=f'bonk{file_ext}')
        if target is None:
            await interaction.response.send_message('BONK!', file=image_file)
        else:
            await interaction.response.send_message('BONK! {target.mention}!', file=image_file)            
            
    @app_commands.command()
    async def slap(self, interaction: discord.Interaction, *, target: discord.Member=None):
        """Get slapped, or slap a user"""
        async with aiohttp.ClientSession() as session, session.get('https://api.waifu.pics/sfw/slap') as response:
            data = await response.json()
            image_url = data['url']
            file_ext = os.path.splitext(image_url)[1]
            async with session.get(image_url) as resp:
                image_data = await resp.read()
                image_file = discord.File(BytesIO(image_data), filename=f'slaps{file_ext}')
        if target is None:
            await interaction.response.send_message(f'{interaction.user.mention} gets slapped!', file=image_file)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} slaps {target.mention}!', file=image_file)

    @app_commands.command()
    async def wink(self, interaction: discord.Interaction, *, target: discord.Member=None):
        """Wink, or wink at a user"""
        async with aiohttp.ClientSession() as session, session.get('https://api.waifu.pics/sfw/wink') as response:
            data = await response.json()
            image_url = data['url']
            file_ext = os.path.splitext(image_url)[1]
            async with session.get(image_url) as resp:
                image_data = await resp.read()
                image_file = discord.File(BytesIO(image_data), filename=f'wink{file_ext}')
        if target is None:
            await interaction.response.send_message(f'{interaction.user.mention} winks!', file=image_file)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} winks at {target.mention}!', file=image_file)

    @app_commands.command()
    async def pat(self, interaction: discord.Interaction, *, target: discord.Member=None):
        """Get headpats, or give headpats to a user"""
        async with aiohttp.ClientSession() as session, session.get('https://api.waifu.pics/sfw/pat') as response:
            data = await response.json()
            image_url = data['url']
            file_ext = os.path.splitext(image_url)[1]
            async with session.get(image_url) as resp:
                image_data = await resp.read()
                image_file = discord.File(BytesIO(image_data), filename=f'pat{file_ext}')
        if target is None:
            await interaction.response.send_message(f'{interaction.user.mention} gets headpats!', file=image_file)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} gives headpats to {target.mention}!', file=image_file)

async def setup(bot):
    await bot.add_cog(Love(bot))