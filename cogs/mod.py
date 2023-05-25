import discord
from discord import app_commands
from typing import Optional

from discord.ext import commands
from utils.data import DiscordBot
from utils import permissions, default
from datetime import timedelta
import re
import asyncpg 
from utils.config import Config

config = Config.from_env()

db_host = config.postgres_host
db_name = config.postgres_name
db_user = config.postgres_user
db_password = config.postgres_password

class ActionReason(commands.Converter):
    async def convert(self, interaction: discord.Interaction, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(
                f"reason is too long ({len(argument)}/{reason_max})"
            )
        return ret
    
class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, target: discord.Member, *, reason: Optional[str] = None):
        """ Kicks a user from the current server. """
        if not await permissions.check_priv(self.bot, interaction, target, {"kick_members": True}):
            return

        try:
            await target.kick(reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("kicked"))
        except Exception as e:
            await print(e)



    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, target: discord.Member, duration: str, *, reason: Optional[str] = None):
        """ Timeouts a user in the current server. """
        if not await permissions.check_priv(self.bot, interaction, target, {"moderate_members": True}):
            return

        match = re.match(r'(\d+)([mhd])?', duration)
        if not match:
            await interaction.response.send_message("Invalid duration format. Use a number followed by m (minutes), h (hours), or d (days).")
            return

        amount, unit = match.groups()
        amount = int(amount)
        unit = unit or 'm'

        if unit == 'm':
            timeout_duration = timedelta(minutes=amount)
        elif unit == 'h':
            timeout_duration = timedelta(hours=amount)
        elif unit == 'd':
            timeout_duration = timedelta(days=amount)

        if timeout_duration > timedelta(days=27):
            await interaction.response.send_message("The maximum timeout duration is 27 days.")
            return

        try:
            await target.timeout(timeout_duration, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("timed out"))
        except Exception as e:
            print(e)


    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def modrole(self, interaction: discord.Interaction, role: discord.Role):
            """ Set the mod role, allows to run all mod commands"""
            if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
                return
            role_id = role.id
            guild_id = interaction.guild_id
            conn = await asyncpg.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            await conn.execute('INSERT INTO mod_role_id (guild_id, role_id) VALUES ($1, $2)'
                               'ON CONFLICT (guild_id) DO UPDATE SET role_id = $2',
                               guild_id, role_id
                                )
            await interaction.response.send_message(f"{role} has been set as mod role")

async def setup(bot):
    await bot.add_cog(Moderator(bot))