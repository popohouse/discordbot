import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from typing import List
import io
import mimetypes

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
        app_commands.Choice(name="hamster", value="hamster"),
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
                async with session.get('https://api.popo.house/cat') as response:
                    image_data = await response.read()
                    content_type = response.headers.get('Content-Type')

                    if content_type is None:
                        # Handle the case where Content-Type is None
                        await interaction.response.send_message("Failed to retrieve the image.")
                    else:
                        extension = mimetypes.guess_extension(content_type)
                        if extension is None:
                            extension = '.jpg'  # Default extension if mimetype is not recognized
                        image_file = discord.File(io.BytesIO(image_data), filename=f"cat{extension}")
                        await interaction.response.send_message(file=image_file)



        elif choice.value == ("hamster"):
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.popo.house/hamster') as response:
                    image_data = await response.read()
                    content_type = response.headers['Content-Type']
                    extension = mimetypes.guess_extension(content_type)
                    image_file = discord.File(io.BytesIO(image_data), filename=f"hamster{extension}")
                    await interaction.response.send_message(file=image_file)

async def setup(bot):
    await bot.add_cog(Animal(bot))