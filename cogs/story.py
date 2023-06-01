import discord
from discord import app_commands
from discord.ext import commands

from discord import File
from io import StringIO


class StoryCog(commands.Cog):
    def __init__(self, bot)-> None:
        self.bot = bot
        self.channel_id = None

    @app_commands.command()
    @commands.guild_only()
    async def story(self, interaction: discord.Interaction, channel: discord.TextChannel)-> None:
        """Used with one word story to get a text file of all current messages. Usage: !story channelid"""
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            content = message.content
            for mention in message.mentions:
                content = content.replace(f'<@{mention.id}>', mention.name)
                content = content.replace(f'<@!{mention.id}>', mention.name)
            messages.append(content)
        with StringIO(' '.join(messages)) as f:
            await interaction.response.send_message(file=File(f, 'story.txt'))


async def setup(bot)-> None:
    await bot.add_cog(StoryCog(bot))