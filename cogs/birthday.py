import discord
from discord import app_commands
from discord.ext import commands
import pytz


from discord.ext import tasks
from datetime import datetime

from utils.config import Config
from utils import permissions

config = Config.from_env()



class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_cache = {}
        self.birthday_channel_cache = {}
        self.birthday_role_cache = {}
        self.timezone_cache = {}
        self.check_birthdays.start()
        self.cleanup_birthday_roles.start()

    async def cog_unload(self):
        self.check_birthdays.cancel()
        self.cleanup_birthday_roles.cancel()

    async def setup(self):
        await self.update_cache()

    async def update_cache(self):
        print("yo waddup cache updating")
        async with self.bot.pool.acquire() as conn:
            birthdays = await conn.fetch("SELECT * FROM birthdays")
            birthday_extras = await conn.fetch("SELECT * FROM birthday_extras")
            user_timezones = await conn.fetch("SELECT * FROM timezones")

        # Update the caches
        self.birthday_cache = {(birthday['guild_id'], birthday['user_id']): birthday['date'] for birthday in birthdays}
        self.birthday_channel_cache = {extra['guild_id']: extra['channel_id'] for extra in birthday_extras if extra['channel_id']}
        self.birthday_role_cache = {extra['guild_id']: extra['role_id'] for extra in birthday_extras if extra['role_id']}
        self.timezone_cache = {row['user_id']: row['timezone'] for row in user_timezones}


    async def update_timezone_cache(self, user_id: int, timezone: str):
        """Update the timezone cache"""
        print("Timezone cached")
        self.timezone_cache[user_id] = timezone

    @commands.Cog.listener()
    async def on_ready(self):
        print("Yo waddup its ya boy onready birthday")
        await self.update_cache()

    @app_commands.command()
    @commands.guild_only()
    async def setbirthday(self, interaction: discord.Interaction, date: str):
        """Sets the user's birthday in the guild"""
        # Define the accepted date formats
        date_formats = ["%Y-%m-%d", "%B %d", "%b %d", "%m/%d"]
        
        # Convert the date string to a date object
        date_obj = None
        for date_format in date_formats:
            try:
                date_obj = datetime.strptime(date, date_format).date()
                break
            except ValueError:
                pass
        
        # Check if the conversion was successful
        if not date_obj:
            await interaction.response.send_message("Invalid date format. Please use one of the following formats: YYYY-MM-DD, Month DD, Mon DD, MM/DD.", ephemeral=True)
            return
        
        # Add a default year if the user didn't provide one
        if "%Y" not in date_format:
            now = datetime.utcnow()
            date_obj = date_obj.replace(year=now.year)
        
        async with self.bot.pool.acquire() as conn:
            guild_id = interaction.guild.id
            user_id = interaction.user.id
            await conn.execute("INSERT INTO birthdays (guild_id, user_id, date) VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id) DO UPDATE SET date = $3", guild_id, user_id, date_obj)
            await interaction.response.send_message(f"Birthday set as {date_obj} in this guild!", ephemeral=True)
        
            # Update the cache
            await self.update_cache()

    @app_commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def birthday_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Sets the birthday channel for the guild"""
        async with self.bot.pool.acquire() as conn:
            
            if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
                return
            
            guild_id = interaction.guild.id
            await conn.execute("INSERT INTO birthday_extras (guild_id, channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET channel_id = $2", guild_id, channel.id)
            await interaction.response.send_message("Birthday channel set")

    @app_commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def birthdayrole(self, interaction: discord.Interaction, role: discord.Role):
        """Sets the birthday role for the guild"""
        async with self.bot.pool.acquire() as conn:

            if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
                return

            guild_id = interaction.guild.id
            await conn.execute("INSERT INTO birthday_extras (guild_id, role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET role_id = $2", guild_id, role.id)
            await interaction.response.send_message("Birthday role set")

    @tasks.loop(seconds=10)
    async def cleanup_birthday_roles(self):
        print("Cleaning up birthday roles")
        # Get the current time in UTC
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        # Check if it's no longer the user's birthday
        for guild_id, role_id in self.birthday_role_cache.items():
            guild = self.bot.get_guild(guild_id)
            if guild:
                role = guild.get_role(role_id)
                if role:
                    for member in role.members:
                        user_id = member.id
                        user_timezone = self.timezone_cache.get(user_id)
                        birthday = self.birthday_cache.get((guild_id, user_id))
                        if birthday:
                            if user_timezone:
                                tz = pytz.timezone(user_timezone)
                                now_user = now_utc.astimezone(tz)
                                if now_user.month != birthday.month or now_user.day != birthday.day:
                                    await member.remove_roles(role)
                            else:
                                if now_utc.month != birthday.month or now_utc.day != birthday.day:
                                    await member.remove_roles(role)
                        else:
                            await member.remove_roles(role)



            


    @tasks.loop(seconds=10)
    async def check_birthdays(self):
        print("Checking birthdays")
        # Get the current time in UTC
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        
        # Check if it's midnight in the user's timezone
        for (guild_id, user_id), birthday in self.birthday_cache.items():
            user_timezone = self.timezone_cache.get(user_id)
            if user_timezone:
                tz = pytz.timezone(user_timezone)
                now_user = now_utc.astimezone(tz)
                if now_user.hour == 12 and now_user.minute == 0:
                    channel_id = self.birthday_channel_cache.get(guild_id)
                    role_id = self.birthday_role_cache.get(guild_id)
                    if channel_id:
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            await channel.send(f"Happy Birthday <@{user_id}>!")
                    if role_id:
                        guild = self.bot.get_guild(guild_id)
                        if guild:
                            member = guild.get_member(user_id)
                            role = guild.get_role(role_id)
                            if member and role:
                                await member.add_roles(role)
            else:
                if now_utc.hour == 0 and now_utc.minute == 0:
                    channel_id = self.birthday_channel_cache.get(guild_id)
                    role_id = self.birthday_role_cache.get(guild_id)
                    if channel_id:
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            await channel.send(f"Happy Birthday <@{user_id}>!")
                    if role_id:
                        guild = self.bot.get_guild(guild_id)
                        if guild:
                            member = guild.get_member(user_id)
                            role = guild.get_role(role_id)
                            if member and role:
                                await member.add_roles(role)


async def setup(bot):
    birthday_cog = BirthdayCog(bot)
    await birthday_cog.setup()
    await bot.add_cog(birthday_cog)