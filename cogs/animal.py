import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Animal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None

    @app_commands.command(name="dog", description="Post random dog image") 
    async def dog(self, interaction: discord.Interaction)-> None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random.dog/woof.json') as response:
                dog = await response.json()
                await interaction.response.send_message(dog['url'])

    @app_commands.command(name="fox", description="Post random fox image")
    async def fox(self, interaction: discord.Interaction)-> None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://randomfox.ca/floof/') as response:
                fox = await response.json()
                await interaction.response.send_message(fox['image'])

    @app_commands.command(name="duck", description="Post random duck image")
    async def duck(self, interaction: discord.Interaction)-> None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random-d.uk/api/random') as response:
                duck = await response.json()
                await interaction.response.send_message(duck['url'])
              
async def setup(bot):
    await bot.add_cog(Animal(bot))