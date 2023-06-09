import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import aiohttp
import os
from io import BytesIO
from typing import Optional
from utils.config import Config
from utils import permissions

config = Config.from_env()


class dailycat(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.conn = None
        self.cache = {}
        self.daily_cat.start()

    async def setup(self):
        await self.update_cache()

    async def cog_unload(self):
        self.daily_cat.cancel()

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def dailycat(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, hour: Optional[int] = None, minute: int = 0, stop: Optional[bool] = None) -> None:
        """Set channel and time or stop cat posting"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        if stop is not None:
            guild_id = interaction.guild_id
            async with self.bot.pool.acquire() as conn:
                await conn.execute('DELETE FROM dailycat WHERE guild_id=$1', guild_id)
                await self.update_cache()
                await interaction.response.send_message('Daily cat posting stopped.', ephemeral=True)
                return
        if channel is None and hour is None and stop is False:
            await interaction.response.send_message('Please set a channel or time.', ephemeral=True)
            return
        guild_id = interaction.guild_id
        async with self.bot.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM dailycat WHERE guild_id= $1', guild_id)
            if row:
                channel_id, post_time_str = row['channel_id'], row['post_time']
                if channel is None:
                    channel = interaction.guild.get_channel(channel_id)
                if hour is None:
                    post_time = datetime.datetime.strptime(post_time_str, '%H:%M').time()
                    hour = post_time.hour
            else:
                if channel is None or hour is None:
                    await interaction.response.send_message('Please provide both a channel and an hour for the first time setup.', ephemeral=True)
                    return
                channel_id = channel.id
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                await interaction.response.send_message('Invalid hour or minute. Please enter a valid time.', ephemeral=True)
                return
            post_time = datetime.time(hour, minute)
            channel_id = channel.id
            await conn.execute(
                'INSERT INTO dailycat (guild_id, channel_id, post_time) VALUES ($1, $2, $3) '
                'ON CONFLICT (guild_id) DO UPDATE SET channel_id = $2, post_time = $3',
                guild_id, channel_id, post_time.strftime('%H:%M')
            )
            await self.update_cache()
            await interaction.response.send_message(f"Daily cat posting set to {channel.mention} at {post_time.strftime('%H:%M')} server time.", ephemeral=True)

    @tasks.loop(minutes=1)
    async def daily_cat(self) -> None:
        now = datetime.datetime.utcnow()
        for guild_id, data in self.cache.items():
            channel_id, post_time_str = data
            post_time = datetime.datetime.strptime(post_time_str, '%H:%M').time()
            if now.time().replace(second=0, microsecond=0) == post_time:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                channel = guild.get_channel(channel_id)
                if not channel:
                    continue
                async with aiohttp.ClientSession() as session, session.get('https://api.thecatapi.com/v1/images/search') as response:
                    cat = await response.json()
                    cat_url = cat[0]['url']
                    file_ext = os.path.splitext(cat_url)[1]
                    async with session.get(cat_url) as resp:
                        img_data = await resp.read()
                        img_file = discord.File(BytesIO(img_data), filename=f'cat{file_ext}')
                        await channel.send("Daily cat posting", file=img_file)

    async def update_cache(self):
        async with self.bot.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM dailycat')
            self.cache = {}
            for row in rows:
                guild_id, channel_id, post_time_str = row['guild_id'], row['channel_id'], row['post_time']
                if channel_id is not None and post_time_str is not None:
                    self.cache[guild_id] = (channel_id, post_time_str)


async def setup(bot):
    cat_cog = dailycat(bot)
    await cat_cog.setup()
    await bot.add_cog(cat_cog)