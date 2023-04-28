import discord


from discord.ext import commands
from discord import File
from io import StringIO


class StoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = None

    @commands.command()
    async def story(self, ctx, channel: discord.TextChannel):
        """Used with one word story to get a text file of all current messages. Usage: !story channelid"""
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            content = message.content
            for mention in message.mentions:
                content = content.replace(f'<@{mention.id}>', mention.name)
                content = content.replace(f'<@!{mention.id}>', mention.name)
            messages.append(content)
        with StringIO(' '.join(messages)) as f:
            await ctx.send(file=File(f, 'story.txt'))

async def setup(bot):
    await bot.add_cog(StoryCog(bot))