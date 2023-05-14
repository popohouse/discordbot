import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from typing import List


class Inspire(commands.Cog):
    def __init__(self, bot):
        self.bot: bot = bot

    @app_commands.command()
    async def inspire(self, interaction: discord.Interaction):
        """Be inspired"""
        async with aiohttp.ClientSession() as session:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://inspirobot.me/api?generate=true') as response:
                    link = await response.text()
                    await interaction.response.send_message(link)

async def setup(bot):
    await bot.add_cog(Inspire(bot))