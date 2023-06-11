import discord
from discord import app_commands
from typing import Optional
from discord.ext import commands
from utils import permissions, default
from datetime import timedelta
import re
from utils.config import Config

config = Config.from_env()


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
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, target: discord.Member, *, reason: Optional[str] = None):
        """Kicks a user from the current server."""
        if not await permissions.check_priv(self.bot, interaction, target, {"kick_members": True}):
            return
        try:
            dm_channel = await target.create_dm()
            await dm_channel.send(f"You have been kicked from {interaction.guild.name}. Reason: {reason}")
            await target.kick(reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("kicked"))
        except Exception as e:
            await print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, target: discord.Member, duration: str, *, reason: Optional[str] = None):
        """Timeouts a user in the current server."""
        if not await permissions.check_priv(self.bot, interaction, target, {"moderate_members": True}):
            return
        match = re.match(r'(\d+)([mhd])?', duration)
        if not match:
            await interaction.response.send_message("Invalid duration format. Use a number followed by m (minutes), h (hours), or d (days).", ephemeral=True)
            return
        amount, unit = match.groups()
        amount = int(amount)
        unit = unit or 'm'
        unit_names = {
            'm': ('minute', 'minutes'),
            'h': ('hour', 'hours'),
            'd': ('day', 'days')
        }
        if unit == 'm':
            timeout_duration = timedelta(minutes=amount)
        elif unit == 'h':
            timeout_duration = timedelta(hours=amount)
        elif unit == 'd':
            timeout_duration = timedelta(days=amount)

        if timeout_duration > timedelta(days=27):
            await interaction.response.send_message("The maximum timeout duration is 27 days.", ephemeral=True)
            return
        try:
            await target.timeout(timeout_duration, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage("timed out"))
            unit_name = unit_names[unit][1] if amount > 1 else unit_names[unit][0]
            dm_channel = await target.create_dm()
            await dm_channel.send(f"You have been timed out in {interaction.guild.name} for {amount} {unit_name}. Reason: {reason}")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def modrole(self, interaction: discord.Interaction, role: discord.Role):
        """Set the mod role, allows to run all mod commands"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        role_id = role.id
        guild_id = interaction.guild_id
        async with self.bot.pool.acquire() as conn:
            await conn.execute('INSERT INTO mod_role_id (guild_id, role_id) VALUES ($1, $2)' 'ON CONFLICT (guild_id) DO UPDATE SET role_id = $2', guild_id, role_id)
            await interaction.response.send_message(f"{role} has been set as mod role")

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def addrole(self, interaction: discord.Interaction, target: discord.Member, role: discord.Role):
        """Adds user to role"""
        if not await permissions.check_priv(self.bot, interaction, target, {"manage_roles": True}):
            return
        if role >= interaction.user.top_role:
            await interaction.response.send_message("You can't give a role that is higher or equal to your current highest role.")
            return
        try:

            await target.add_roles(role, reason=default.responsible(interaction.user, "Added role"))
            await interaction.response.send_message(default.actionmessage("added to {role}"))
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def delrole(self, interaction: discord.Interaction, target: discord.Member, role: discord.Role):
        """Removes role from user"""
        if not await permissions.check_priv(self.bot, interaction, target, {"manage_roles": True}):
            return
        if role >= interaction.user.top_role:
            await interaction.response.send_message("You can't remove a role that is higher or equal to your current highest role.")
            return
        try:
            await target.remove_roles(role, reason=default.responsible(interaction.user, "Removed role"))
            await interaction.response.send_message(default.actionmessage("removed from {role}"))
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def massrole(self, interaction: discord.Interaction, role: discord.Role):
        """Adds every user in the guild to the specified role"""
        if not await permissions.check_priv(self.bot, interaction, interaction.user, {"manage_roles": True}, skip_self_checks=True):
            return
        if role >= interaction.user.top_role:
            await interaction.response.send_message("You can't give a role that is higher or equal to your current highest role.")
            return
        try:
            for member in interaction.guild.members:
                await member.add_roles(role, reason=default.responsible(interaction.user, "Added role"))
            await interaction.response.send_message(default.actionmessage(f"added every user to {role}"))
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def massunrole(self, interaction: discord.Interaction, role: discord.Role):
        """Removes every user in the guild from the specified role"""
        if not await permissions.check_priv(self.bot, interaction, interaction.user, {"manage_roles": True}, skip_self_checks=True):
            return
        if role >= interaction.user.top_role:
            await interaction.response.send_message("You can't remove a role that is higher or equal to your current highest role.")
            return
        try:
            for member in interaction.guild.members:
                await member.remove_roles(role, reason=default.responsible(interaction.user, "Removed role"))
            await interaction.response.send_message(default.actionmessage(f"removed every user from {role}"))
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int, channel: Optional[discord.TextChannel], reason: Optional[str] = None):
        """Purges a specified amount of messages in the current channel"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_messages": True}):
            return
        channel = channel or interaction.channel or interaction.guild.system_channel 
        try:
            await channel.purge(limit=amount + 1, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(default.actionmessage(f"Will purge {amount} messages"))
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, slowmode: int, channel: Optional[discord.TextChannel], reason: Optional[str] = None):
        """Toggles slowmode in the current channel"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_channels": True}):
            return
        channel = channel or interaction.channel or interaction.guild.system_channel 
        if slowmode > 21600:
            await interaction.response.send_message("Slowmode can't be longer than 6 hours", ephemeral=True)
            return
        if slowmode < 0:
            await interaction.response.send_message("Slowmode can't be negative", ephemeral=True)
            return
        if slowmode == 0:
            await channel.edit(slowmode_delay=slowmode, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message("Disabled slowmode")
            return
        try:
            await channel.edit(slowmode_delay=slowmode, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message("Slowmode now set to {slowmode} seconds")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_channels=True)
    async def unban(self, interaction: discord.Interaction, target: str, *, reason: Optional[str] = None):
        """Unbans a user from the current server."""
        target_id = int(target)
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_channels": True}):
            return
        try:
            target_user = await self.bot.fetch_user(target_id)
            await interaction.guild.unban(target_user, reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(f"{target_user} has been unbanned")
        except discord.NotFound:
            await interaction.response.send_message("User not found", ephemeral=True)
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Moderator(bot))