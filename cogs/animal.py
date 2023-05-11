import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from typing import List

class Animal(commands.Cog):
    def __init__(self, bot: commands.Bot)-> None:
        self.bot = bot
        self.channel_id = None

    @app_commands.command()
    @app_commands.choices(choice=[
        app_commands.Choice(name="dog", value="dog"),
        app_commands.Choice(name="fox", value="fox"),
        app_commands.Choice(name="duck", value="duck"),
        app_commands.Choice(name="cat", value="cat"),
    ])

    async def animal(self, interaction: discord.Interaction, choice: app_commands.Choice[str])-> None:
        """Send animal"""
        if choice.value == ("dog"):
            async with aiohttp.ClientSession() as session:
                async with session.get('https://random.dog/woof.json') as response:
                    dogimg = await response.json()
                    await interaction.response.send_message(dogimg['url']) 

        elif choice.value == ("fox"):
            async with aiohttp.ClientSession() as session:
                async with session.get('https://randomfox.ca/floof/') as response:
                    foximg = await response.json()
                    await interaction.response.send_message(foximg['image'])

        elif choice.value == ("duck"):
            async with aiohttp.ClientSession() as session:
                async with session.get('https://random-d.uk/api/random') as response:
                    duckimg = await response.json()
                    await interaction.response.send_message(duckimg['url'])

        elif choice.value == ("cat"):
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                    cat = await response.json()
                    await interaction.response.send_message(cat[0]['url'])

async def setup(bot):
    await bot.add_cog(Animal(bot))