import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import aiohttp
import os
from io import BytesIO
from typing import Optional
import psycopg2

from utils.config import Config

config = Config.from_env()

db_host = config.postgres_host
db_name = config.postgres_name
db_user = config.postgres_user
db_password = config.postgres_password



class CatCog(commands.Cog):
    def __init__(self, bot)-> None:
        self.bot = bot
        self.conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
        )
        self.cache = {}
        self.update_cache()
        self.daily_cat.start()

    def cog_unload(self):
        self.daily_cat.cancel()

    @app_commands.command()
    async def cat(self, interaction: discord.Interaction)-> None:
        """ Post random cat image"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                cat = await response.json()
                await interaction.response.send_message(cat[0]['url'])


    @app_commands.command()
    async def dailycat(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, hour: Optional[int] = None, minute: int = 0)-> None:
        """Set the channel and time for daily cat posting"""
        if channel is None and hour is None:
            await interaction.response.send_message('Please set a channel or time.')
            return
        guild_id = interaction.guild_id
        c = self.conn.cursor()
        c.execute('SELECT * FROM dailycat WHERE guild_id= %s', (guild_id,))
        row = c.fetchone()
        if row:
            channel_id, post_time_str = row[1:]
            if channel is None:
                channel = interaction.guild_id.get_channel(channel_id)
            if hour is None:
                post_time = datetime.datetime.strptime(post_time_str, '%H:%M').time()
                hour = post_time.hour
        else:
            if channel is None or hour is None:
                await interaction.response.send_message('Please provide both a channel and an hour for the first time setup.')
                return
        channel_id = channel.id
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            await interaction.response.send_message('Invalid hour or minute. Please enter a valid time.')
            return
        post_time = datetime.time(hour, minute)
        c.execute(
            'INSERT INTO dailycat (guild_id, channel_id, post_time) VALUES (%s, %s, %s) '
            'ON CONFLICT (guild_id) DO UPDATE SET channel_id = %s, post_time = %s',
            (guild_id, channel_id, post_time.strftime('%H:%M'), channel_id, post_time.strftime('%H:%M'))
        )
        self.conn.commit()
        self.update_cache()
        await interaction.response.send_message(f"Daily cat posting set to {channel.mention} at {post_time.strftime('%H:%M')} server time.")

    @app_commands.command()
    async def stopdailycat(self, interaction: discord.Interaction)-> None:
        """Stop daily cat posting"""
        guild_id = interaction.guild_id
        c = self.conn.cursor()
        c.execute('DELETE FROM dailycat WHERE guild_id=%s', (guild_id,))
        self.conn.commit()
        self.update_cache()
        await interaction.response.send_message('Daily cat posting stopped.')

    @tasks.loop(minutes=1)
    async def daily_cat(self)-> None:
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
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                        cat = await response.json()
                        cat_url = cat[0]['url']
                        file_ext = os.path.splitext(cat_url)[1]
                        async with session.get(cat_url) as resp:
                            img_data = await resp.read()
                            img_file = discord.File(BytesIO(img_data), filename=f'cat{file_ext}')
                            await channel.send("Daily cat posting", file=img_file)


    def update_cache(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM dailycat')
        rows = c.fetchall()
        self.cache = {}
        for row in rows:
            guild_id, channel_id, post_time_str = row
            if channel_id is not None and post_time_str is not None:
                self.cache[guild_id] = (channel_id, post_time_str)

async def setup(bot):
    await bot.add_cog(CatCog(bot))