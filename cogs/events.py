import discord
import psutil
import os
from discord.ext import commands
from utils import config
import random
import asyncio

config = config.Config.from_env(".env")
cooldown_duration = 3600 # In seconds

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())
        self.user_cooldowns = {}

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        to_send = next((
            chan for chan in guild.text_channels
            if chan.permissions_for(guild.me).send_messages
        ), None)

        if to_send:
            await to_send.send(config.discord_join_message)

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        # Check if the user is a bot or already in cooldown
        if user.bot or user.id in self.user_cooldowns:
            return
        # Set the chance of the bot responding to typing events (1 in 10,000)
        chance = 0.0001
        # Generate a random number between 0 and 1
        random_number = random.random()
        # Check if the random number is within the defined chance range
        if random_number < chance:
            # Generate a random message to send
            messages = ["You're typing so slow!", "I see you typing...", "Can't wait to see what you're typing!"]
            random_message = random.choice(messages)
            await channel.send(f"{user.mention} {random_message}")
            self.user_cooldowns[user.id] = True
            await asyncio.sleep(cooldown_duration)
            del self.user_cooldowns[user.id]
        if random_number > chance:
            self.user_cooldowns[user.id] = True
            await asyncio.sleep(cooldown_duration)
            del self.user_cooldowns[user.id]


async def setup(bot):
    await bot.add_cog(Events(bot))