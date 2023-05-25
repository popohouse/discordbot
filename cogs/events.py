import discord
import psutil
import os

from datetime import datetime
from discord.ext import commands
from discord.ext.commands import errors
from utils import default


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        to_send = next((
            chan for chan in guild.text_channels
            if chan.permissions_for(guild.me).send_messages
        ), None)

        if to_send:
            await to_send.send(self.bot.config.discord_join_message)

  
async def setup(bot):
    await bot.add_cog(Events(bot))