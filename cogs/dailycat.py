import discord
from discord.ext import commands, tasks
import sqlite3
import datetime
import aiohttp
import os
from io import BytesIO
from typing import Optional

class DailyCat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('data/MeowMix.db')
        self.cache = {}
        self.update_cache()
        self.daily_cat.start()

    def cog_unload(self):
        self.daily_cat.cancel()

    @commands.command()
    async def setdailycat(self, ctx, channel: Optional[discord.TextChannel] = None, hour: Optional[int] = None, minute: int = 0):
        """Set the channel and time for daily cat posting"""
        if channel is None and hour is None:
            await ctx.send('Please set a channel or time.')
            return
        guild_id = ctx.guild.id
        c = self.conn.cursor()
        c.execute('SELECT * FROM dailycat WHERE guild_id=?', (guild_id,))
        row = c.fetchone()
        if row:
            channel_id, post_time_str = row[1:]
            if channel is None:
                channel = ctx.guild.get_channel(channel_id)
            if hour is None:
                post_time = datetime.datetime.strptime(post_time_str, '%H:%M').time()
                hour = post_time.hour
        else:
            if channel is None or hour is None:
                await ctx.send('Please provide both a channel and an hour for the first time setup.')
                return
        channel_id = channel.id
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            await ctx.send('Invalid hour or minute. Please enter a valid time.')
            return
        post_time = datetime.time(hour, minute)
        c.execute('INSERT OR REPLACE INTO dailycat VALUES (?, ?, ?)', (guild_id, channel_id, post_time.strftime('%H:%M')))
        self.conn.commit()
        self.update_cache()
        await ctx.send(f"Daily cat posting set to {channel.mention} at {post_time.strftime('%H:%M')} server time.")

    @commands.command()
    async def stopdailycat(self, ctx):
        """Stop daily cat posting"""
        guild_id = ctx.guild.id
        c = self.conn.cursor()
        c.execute('DELETE FROM dailycat WHERE guild_id=?', (guild_id,))
        self.conn.commit()
        self.update_cache()
        await ctx.send('Daily cat posting stopped.')

    @tasks.loop(minutes=1)
    async def daily_cat(self):
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
        self.cache = {row[0]: row[1:] for row in rows}

async def setup(bot):
    await bot.add_cog(DailyCat(bot))