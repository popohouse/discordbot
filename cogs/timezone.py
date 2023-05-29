import discord
from discord import app_commands
from discord.ext import commands


import pytz
from datetime import datetime
from typing import Optional

from utils.config import Config

config = Config.from_env()



class TimezoneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @app_commands.command()
    @commands.guild_only()
    async def settime(self, interaction: discord.Interaction, timezone: str):
        """Set your timezone"""
        if timezone not in pytz.all_timezones:
            await interaction.response.send_message(f"Invalid timezone. Please choose one from this list: https://bin.ffm.best/popo/19e444b71b134847b1a11e4903989d6a", ephemeral=True)
            return
    
        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO timezones (user_id, timezone) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET timezone = $2",
                interaction.user.id,
                timezone
            )

            await interaction.response.send_message(f"Timezone set to {timezone}", ephemeral=True)

            # Update the timezone cache
            cog = self.bot.get_cog("BirthdayCog")
            if cog:
                await cog.update_timezone_cache(interaction.user.id, timezone)

    @app_commands.command()
    @commands.guild_only()
    async def time(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Get the time of a member"""
        if member is None:
            member = interaction.user
        if member is interaction.user:
            await interaction.response.send_message(f"Please set your timezone first", ephemeral=True)
        async with self.bot.pool.acquire() as conn:
        
            record = await conn.fetchrow("SELECT timezone FROM timezones WHERE user_id = $1", member.id)
            if member is interaction.user and not record: 
                await interaction.response.send_message(f"Please set your timezone first", ephemeral=True)
            elif not record:
                await interaction.response.send_message(f"{member.display_name} has not set their timezone", ephemeral=True)
            else:
                timezone_name = record['timezone']
                timezone = pytz.timezone(timezone_name)
                now = datetime.now(timezone)
                time_str = now.strftime('%H:%M')
                await interaction.response.send_message(f"The current time for {member.display_name} is {time_str}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    async def deltime(self, interaction: discord.Interaction):
        """Remove your timezone from the database"""
        async with self.bot.pool.acquire() as conn:
        
            await conn.execute("DELETE FROM timezones WHERE user_id = $1", interaction.user.id)
            await interaction.response.send_message("Your timezone has been removed", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TimezoneCog(bot))
