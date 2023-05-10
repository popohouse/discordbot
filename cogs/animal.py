import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Animal(commands.Cog):
    def __init__(self, bot: commands.Bot)-> None:
        self.bot = bot
        self.channel_id = None
    
    group = app_commands.Group(name="animal", description="Posts animal type you want")

    @app_commands.command(name="top-command")
    async def my_top_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Please send non empty command", ephemeral=True)
    
    @group.command(name="dog")
    async def dog(self, interaction: discord.Interaction)-> None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random.dog/woof.json') as response:
                dog = await response.json()
                await interaction.response.send_message(dog['url'])

    @group.command(name="fox")
    async def fox(self, interaction: discord.Interaction)-> None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://randomfox.ca/floof/') as response:
                fox = await response.json()
                await interaction.response.send_message(fox['image'])

    @group.command(name="duck")
    async def duck(self, interaction: discord.Interaction)-> None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random-d.uk/api/random') as response:
                duck = await response.json()
                await interaction.response.send_message(duck['url'])
              
async def setup(bot):
    await bot.add_cog(Animal(bot))