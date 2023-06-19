import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import re
import datetime
from datetime import timedelta
from utils import permissions, default
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
    @permissions.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, target: discord.Member, *, reason: Optional[str] = None):
        """Warns a user in the current server."""
        if not await permissions.check_priv(self.bot, interaction, target, {"manage_messages": True}):
            return
        if reason is None:
            reason = "No reason provided"
        try:
            async with self.bot.pool.acquire() as conn:
                timestamp = datetime.datetime.now()
                mod_id = interaction.user.id
                await conn.execute('INSERT INTO warnings (guild_id, user_id, mod_id, reason, timestamp) VALUES ($1, $2, $3, $4, $5)', interaction.guild_id, target.id, mod_id, reason, timestamp)
                dm_channel = await target.create_dm()
                await dm_channel.send(f"You have been warned in {interaction.guild.name}. Reason: {reason}")
        except discord.Forbidden:
            print("Unable to send a direct message to the user.")
        await interaction.response.send_message(f"Warned **{target.name}**. Reason: {reason}")

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def checkwarns(self, interaction: discord.Interaction, target: discord.Member):
        """Checks user warns"""
        if not await permissions.check_priv(self.bot, interaction, target, {"manage_messages": True}):
            return
        try:
            async with self.bot.pool.acquire() as conn:
                warnings = await conn.fetch('SELECT * FROM warnings WHERE guild_id = $1 AND user_id = $2', interaction.guild_id, target.id)
                total_warnings = len(warnings)  # Total number of warnings
                if total_warnings == 0:
                    await interaction.response.send_message(f"{target.name} has no warnings")
                    return
                embed = discord.Embed(title=f"Warnings for {target.name}", color=0x00ff00)
                embed.add_field(name="Total Warnings", value=str(total_warnings), inline=False)  # Add total warnings field
                for warning in warnings:
                    mod = self.bot.get_user(warning['mod_id'])
                    if mod:
                        mod_username = mod.name
                    else:
                        mod_username = str(warning['mod_id'])
                    timestamp = warning['timestamp']
                    formatted_timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
                    embed.add_field(name=f"Warning ID: {warning['id']}", value=f"Reason: {warning['reason']}\nModerator: {mod_username}\nTime: {formatted_timestamp}", inline=False)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def unwarn(self, interaction: discord.Interaction, target: discord.Member, warning_id: int):
        """Removes a warning from a user"""
        if not await permissions.check_priv(self.bot, interaction, target, {"manage_messages": True}):
            return
        try:
            async with self.bot.pool.acquire() as conn:
                warning = await conn.fetchrow('SELECT * FROM warnings WHERE guild_id = $1 AND user_id = $2 AND id = $3', interaction.guild_id, target.id, warning_id)
                if warning is None:
                    await interaction.response.send_message(f"Warning ID {warning_id} does not exist for {target.name}")
                    return
                await conn.execute('DELETE FROM warnings WHERE guild_id = $1 AND user_id = $2 AND id = $3', interaction.guild_id, target.id, warning_id)
                await interaction.response.send_message(f"Removed warning ID {warning_id} for {target.name}")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def notes(self, interaction: discord.Interaction, target: discord.Member, note: str):
        if not await permissions.check_priv(self.bot, interaction, target, {"manage_messages": True}):
            return
        try:
            async with self.bot.pool.acquire() as conn:
                timestamp = datetime.datetime.now()
                await conn.execute('INSERT INTO notes (guild_id, user_id, mod_id, note, timestamp) VALUES ($1, $2, $3, $4, $5)', interaction.guild_id, target.id, interaction.user.id, note, timestamp)
        except Exception as e:
            print(e)
        await interaction.response.send_message(f"Added note for {target.name}", ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def checknotes(self, interaction: discord.Interaction, target: discord.Member):
        """Checks user notes"""
        if not await permissions.check_priv(self.bot, interaction, target, {"manage_messages": True}):
            return
        try:
            async with self.bot.pool.acquire() as conn:
                notes = await conn.fetch('SELECT * FROM notes WHERE guild_id = $1 AND user_id = $2', interaction.guild_id, target.id)
                if len(notes) == 0:
                    await interaction.response.send_message(f"{target.name} has no notes")
                    return
                embed = discord.Embed(title=f"Warnings for {target.name}", color=0x00ff00)
                for note in notes:
                    mod = self.bot.get_user(note['mod_id'])
                    if mod:
                        mod_username = mod.name
                    else:
                        mod_username = str(note['mod_id'])
                    timestamp = note['timestamp']
                    formatted_timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
                    embed.add_field(name=f"Note ID: {note['id']}", value=f"Note: {note['note']}\nModerator: {mod_username}\nTime: {formatted_timestamp}", inline=False)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def setreportchannel(self, interaction: discord.Interaction, channel: discord.TextChannel, role: Optional[discord.Role] = None):
        """Sets the channel where reports will be sent"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        try:
            async with self.bot.pool.acquire() as conn:
                await conn.execute('INSERT INTO reportchannel (guild_id, channel_id, role_id) VALUES ($1, $2, $3)' 'ON CONFLICT (guild_id) DO UPDATE SET channel_id = $2', interaction.guild_id, channel.id, role.id)
                await interaction.response.send_message(f"Set report channel to {channel.mention}")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    async def report(self, interaction: discord.Interaction, target: discord.Member, reason: str):
        """Reports a user to the moderation team of the server"""
        try:
            async with self.bot.pool.acquire() as conn:
                report_channel_id = await conn.fetchval('SELECT channel_id FROM reportchannel WHERE guild_id = $1', interaction.guild_id)
                pingrole = await conn.fetchval('SELECT role_id FROM reportchannel WHERE guild_id = $1', interaction.guild_id)
                if pingrole is not None:
                    role = interaction.guild.get_role(pingrole)
                report_channel = self.bot.get_channel(report_channel_id)
                if report_channel is None:
                    await interaction.response.send_message("No report channel set, please bug staff", ephemeral=True)
                    return
                embed = discord.Embed(title="Report", color=0x00ff00)
                embed.add_field(name="Reported User", value=target.mention, inline=False)
                embed.add_field(name="Reported By", value=interaction.user.mention, inline=False)
                if role is not None:
                    content = role.mention
                embed.add_field(name="Reason", value=reason, inline=False)
                await report_channel.send(content, embed=embed)
                await interaction.response.send_message("Report sent", ephemeral=True)
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, target: discord.Member, *, reason: Optional[str] = None):
        """Kicks a user from the current server."""
        if not await permissions.check_priv(self.bot, interaction, target, {"kick_members": True}):
            return
        if reason is None:
            reason = "No reason provided"
        try:
            dm_channel = await target.create_dm()
            try:
                await dm_channel.send(f"You have been kicked from {interaction.guild.name}. Reason: {reason}")
            except discord.Forbidden:
                print("Unable to send a direct message to the user.")
            await target.kick(reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(f"Kicked **{target.name}** from the server. Reason: {reason}")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, target: discord.Member, duration: str, *, reason: Optional[str] = None):
        """Timeouts a user in the current server."""
        if not await permissions.check_priv(self.bot, interaction, target, {"moderate_members": True}):
            return
        if reason is None:
            reason = "No reason provided"
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
        except discord.Forbidden:
            print("Unable to send a direct message to the user.")
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
            await interaction.response.send_message(f"Added **{target.name}** to **{role.name}** role")
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
            await interaction.response.send_message(f"Removed **{target.name}** from **{role.name}** role")
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
            await interaction.response.send_message(f"Added every user to {role.name} role")
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
            await interaction.response.send_message(f"Removed every user to {role.name} role")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int, channel: Optional[discord.TextChannel], reason: Optional[str] = None):
        """Purges a specified amount of messages in the current channel"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_messages": True}):
            return
        if reason is None:
            reason = "No reason provided"
        channel = channel or interaction.channel or interaction.guild.system_channel
        try:
            messages_to_delete = []
            async for message in channel.history(limit=amount + 1):
                messages_to_delete.append(message)
            await channel.delete_messages(messages_to_delete)
            await interaction.response.send_message(f"Will purge {amount} messages")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, slowmode: int, channel: Optional[discord.TextChannel], reason: Optional[str] = None):
        """Toggles slowmode in the current channel"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_channels": True}):
            return
        if reason is None:
            reason = "No reason provided"
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
    @permissions.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, target: discord.Member, *, reason: Optional[str] = None):
        """Kicks a user from the current server."""
        if not await permissions.check_priv(self.bot, interaction, target, {"ban_members": True}):
            return
        if reason is None:
            reason = "No reason provided"
        try:
            dm_channel = await target.create_dm()
            try:
                await dm_channel.send(f"You have been banned from {interaction.guild.name}. Reason: {reason}")
            except discord.Forbidden:
                print("Unable to send a direct message to the user.")
            await target.ban(reason=default.responsible(interaction.user, reason))
            await interaction.response.send_message(f"Banned **{target.name}** from the server. Reason: {reason}")
        except Exception as e:
            print(e)

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, target: str, *, reason: Optional[str] = None):
        """Unbans a user from the current server."""
        target_id = int(target)
        if not await permissions.check_priv(self.bot, interaction, None, {"ban_members": True}):
            return
        if reason is None:
            reason = "No reason provided"
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