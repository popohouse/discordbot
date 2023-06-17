import discord
from discord import app_commands
from discord.ext import commands
import datetime
from datetime import datetime
from typing import Optional
from utils.config import Config
from discord.automod import AutoModRuleActionType
import asyncio
from utils.default import format_time

config = Config.from_env()


class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_settings = {}
        self.cache = {}
        self.pending_executions = {}
        self.action_type_names = {
            AutoModRuleActionType.block_message: "Blocked Message",
            AutoModRuleActionType.timeout: "Timeout"
        }

    async def setup(self):
        await self.update_cache()

    async def update_cache(self, guild_id=None):
        try:
            if guild_id is not None and guild_id in self.cache:
                del self.cache[guild_id]
            async with self.bot.pool.acquire() as conn:
                if guild_id is None:
                    logs = await conn.fetch('SELECT * FROM logging')
                else:
                    logs = await conn.fetch('SELECT * FROM logging WHERE guild_id = $1', guild_id)
                for row in logs:
                    guild_id = row['guild_id']
                    channel_id = row['channel_id']
                    log_deleted_messages = row['log_deleted_messages']
                    log_edited_messages = row['log_edited_messages']
                    log_nickname_changes = row['log_nickname_changes']
                    log_member_join_leave = row['log_member_join_leave']
                    log_member_kick = row['log_member_kick']
                    log_member_ban_unban = row['log_member_ban_unban']
                    modlogchannel_id = row['modlogchannel_id']
                    log_automod_actions = row['log_automod_actions']
                    if guild_id not in self.cache:
                        # Add the retrieved values to the cache dictionary
                        self.cache[guild_id] = {
                            'channel_id': channel_id,
                            'log_deleted_messages': log_deleted_messages,
                            'log_edited_messages': log_edited_messages,
                            'log_nickname_changes': log_nickname_changes,
                            'log_member_join_leave': log_member_join_leave,
                            'log_member_kick': log_member_kick,
                            'log_member_ban_unban': log_member_ban_unban,
                            'modlogchannel_id': modlogchannel_id,
                            'log_automod_actions': log_automod_actions
                        }
        except Exception as e:
            print(f"Failed to update cache: {str(e)}")


    # Log command
    @app_commands.command()
    @commands.guild_only()
    @app_commands.choices(log_type=[
        app_commands.Choice(name="all", value="all"),
        app_commands.Choice(name="deleted_message", value="log_deleted_messages"),
        app_commands.Choice(name="edited_message", value="log_edited_messages"),
        app_commands.Choice(name="nickname", value="log_nickname_changes"),
        app_commands.Choice(name="membership", value="log_member_join_leave"),
        app_commands.Choice(name="member_kick", value="log_member_kick"),
        app_commands.Choice(name="ban_unban", value="log_member_ban_unban"),
        app_commands.Choice(name="automod", value="log_automod_actions")
    ])
    async def log(self, interaction: discord.Interaction, log_type: Optional[app_commands.Choice[str]], disable: Optional[bool] = None):
        """Enable or disable logging type"""
        async with self.bot.pool.acquire() as conn:
            # Disable logging types
            if disable is True:
                if log_type.value == 'all':
                    await conn.execute('UPDATE logging SET log_deleted_messages = false, log_edited_messages = false, log_nickname_changes = false, log_member_join_leave = false, log_member_kick = false, log_member_ban_unban = false, log_automod_actions = false WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_deleted_messages':
                    await conn.execute('UPDATE logging SET log_deleted_messages = false WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_edited_messages':
                    await conn.execute('UPDATE logging SET log_edited_messages = false WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_nickname_changes':
                    conn.execute('UPDATE logging SET log_nickname_changes = false WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_member_join_leave':
                    await conn.execute('UPDATE logging SET log_member_join_leave = false WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_member_kick':
                    await conn.execute('UPDATE logging SET log_member_kick = false WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_member_ban_unban':
                    await conn.execute('UPDATE logging SET log_member_ban_unban = false WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_automod_actions':
                    await conn.execute('UPDATE logging SET log_automod_actions = false WHERE guild_id = $1', interaction.guild.id)
                else:
                    await interaction.response.send_message(f'Invalid log type: {log_type.value}', ephemeral=True)
                    return
                await self.update_cache(interaction.guild.id)
                await interaction.response.send_message(f'Disabled logging for {log_type.value}', ephemeral=True)
            # Enable logging type
            if disable is None:
                if log_type.value == 'all':
                    await conn.execute('UPDATE logging SET log_deleted_messages = true, log_edited_messages = true, log_nickname_changes = true, log_member_join_leave = true, log_member_kick = true, log_member_ban_unban = true, log_automod_actions = true WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_deleted_messages':
                    await conn.execute('UPDATE logging SET log_deleted_messages = true WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_edited_messages':
                    await conn.execute('UPDATE logging SET log_edited_messages = true WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_nickname_changes':
                    await conn.execute('UPDATE logging SET log_nickname_changes = true WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_member_join_leave':
                    await conn.execute('UPDATE logging SET log_member_join_leave = true WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_member_kick':
                    await conn.execute('UPDATE logging SET log_member_kick = true WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_member_ban_unban':
                    await conn.execute('UPDATE logging SET log_member_ban_unban = true WHERE guild_id = $1', interaction.guild.id)
                elif log_type.value == 'log_automod_actions':
                    await conn.execute('UPDATE logging SET log_automod_actions = true WHERE guild_id = $1', interaction.guild.id)
                else:
                    await interaction.response.send_message(f'Invalid log type: {log_type.value}', ephemeral=True)
                    return
                await self.update_cache(interaction.guild.id)
                await interaction.response.send_message(f'Enabled logging for {log_type.value}', ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    async def setlogchannel(self, interaction: discord.Interaction, logchannel: Optional[discord.TextChannel], modchannel: Optional[discord.TextChannel]):
        async with self.bot.pool.acquire() as conn:
            # Set main log channel
            if logchannel is not None:
                row = await conn.fetchrow('SELECT * FROM logging WHERE guild_id = $1', interaction.guild.id)
                if row:
                    await conn.execute('UPDATE logging SET channel_id = $2 WHERE guild_id = $1', interaction.guild.id, logchannel.id)
                else:
                    await conn.execute('INSERT INTO logging (guild_id, channel_id) VALUES ($1, $2)', interaction.guild.id, logchannel.id)
                if interaction.guild.id in self.cache:
                    self.cache[interaction.guild.id]['channel_id'] = logchannel.id
                else:
                    self.cache[interaction.guild.id] = {
                        'channel_id': logchannel.id,
                        'log_deleted_messages': False,
                        'log_edited_messages': False,
                        'log_nickname_changes': False,
                        'log_member_join_leave': False,
                        'log_member_kick': False,
                        'log_member_ban_unban': False,
                        'log_automod_actions': False,
                    }
                await interaction.response.send_message(f'Set logging channel to {logchannel.mention}', ephemeral=True)
            
            # Set mod log channel
            if modchannel is not None:
                row = await conn.fetchrow('SELECT * FROM logging WHERE guild_id = $1', interaction.guild.id)
                if row:
                    await conn.execute('UPDATE logging SET modlogchannel_id = $2 WHERE guild_id = $1', interaction.guild.id, modchannel.id)
                else:
                    await conn.execute('INSERT INTO logging (guild_id, modlogchannel_id) VALUES ($1, $2)', interaction.guild.id, modchannel.id)
                if interaction.guild.id in self.cache:
                    self.cache[interaction.guild.id]['modlogchannel_id'] = modchannel.id
                else:
                    self.cache[interaction.guild.id] = {
                        'channel_id': None,
                        'log_deleted_messages': False,
                        'log_edited_messages': False,
                        'log_nickname_changes': False,
                        'log_member_join_leave': False,
                        'log_member_kick': False,
                        'log_member_ban_unban': False,
                        'log_automod_actions': False,
                        'modlogchannel_id': modchannel.id
                    }
                await interaction.response.send_message(f'Set mod log channel to {modchannel.mention}', ephemeral=True)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild_id = message.guild.id
        if guild_id in self.cache and self.cache[guild_id]['log_deleted_messages']:
            channel_id = self.cache[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            if channel and message.channel.id != channel_id:
                # Check audit log for moderator action
                async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete):
                    if entry.target.id == message.author.id and entry.extra.channel.id == message.channel.id:
                        moderator = entry.user
                        break
                else:
                    moderator = None
                # Update embed description based on whether a moderator deleted the message
                if moderator:
                    description = f"Message sent by {message.author.mention} in {message.channel.mention} was deleted by {moderator.mention}."
                else:
                    description = f"Message sent by {message.author.mention} in {message.channel.mention} was deleted."
                formatted_date = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                embed = discord.Embed(title="Message Deleted", description=description + f"\n\n**Content**\n{message.content}\n\n**Date**\n{formatted_date}", color=discord.Color.red())
                embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        guild_id = before.guild.id
        if guild_id in self.cache and self.cache[guild_id]['log_edited_messages']:
            channel_id = self.cache[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            if before.content == after.content or before.channel.id == channel_id:
                return
            embed = discord.Embed(title="Message Edited", description=f"Message sent by {before.author.mention} in {before.channel.mention} was edited.\n\n**Before**\n{before.content}\n\n**After**\n[{after.content}]({after.jump_url})\n\n**Date**\n<t:{int(after.edited_at.timestamp())}>", color=discord.Color.orange())
            embed.set_author(name=before.author.display_name, icon_url=before.author.avatar.url)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        guild_id = before.guild.id
        if guild_id in self.cache and self.logging.settings[guild_id]['log_nickname_changes'] and before.username is not after.username:
            channel_id = self.cache[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            embed = discord.Embed(title="Username Changed", description=f"{before.mention} changed their username.\n\n**Before**\n{before.username or before.name}\n\n**After**\n{after.username or after.name}\n\n**Date**\n<t:{int(datetime.utcnow().timestamp())}>", color=discord.Color.blue())
            embed.set_author(name=after.nick or after.display_name, icon_url=before.avatar.url)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild_id = before.guild.id
        if guild_id in self.cache and self.cache[guild_id]['log_nickname_changes']:
            if before.nick != after.nick:
                channel_id = self.cache[guild_id]['channel_id']
                channel = self.bot.get_channel(channel_id)
                embed = discord.Embed(title="Nickname Changed", description=f"{before.mention} changed their nickname.\n\n**Before**\n{before.nick or before.name}\n\n**After**\n{after.nick or after.name}\n\n**Date**\n<t:{int(datetime.utcnow().timestamp())}>", color=discord.Color.blue())
                embed.set_author(name=after.nick or after.display_name, icon_url=before.avatar.url)
                await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        if guild_id in self.cache and self.cache[guild_id]['log_member_join_leave']:
            channel_id = self.cache[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            if member.avatar:
                user_avatar_url = member.avatar.url
            else:
                user_avatar_url = member.default_avatar_url
            embed = discord.Embed(title="Member Joined", description=f"{member.mention} joined the server.", color=discord.Color.green())
            embed.set_author(name=member.display_name, icon_url=user_avatar_url)
            embed.add_field(name="Join Date", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="User ID", value=member.id, inline=True)
            embed.add_field(name="Username", value=member.name, inline=True)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = member.guild.id
        if guild_id in self.cache and self.cache[guild_id]['log_member_join_leave']:
            channel_id = self.cache[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            time_threshold = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(seconds=15)
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.ban):
                if entry.target.id == member.id and entry.created_at > time_threshold:
                    return 
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick):
                if entry.target.id == member.id and entry.created_at > time_threshold:
                    kicked_by = entry.user
                    break
            else:
                kicked_by = None
            if kicked_by:
                description = f"{member.mention} was kicked from the server by {kicked_by.mention}."
                embed.add_field(name="Userid", value=member.id, inline=True)
            else:
                description = f"{member.mention} left the server."
            embed = discord.Embed(title="Member Left", description=description, color=discord.Color.red())
            embed.set_author(name=member.display_name, icon_url=member.avatar.url)
            embed.add_field(name="Username", value=member.name, inline=True)
            await channel.send(embed=embed)

    # Log bans
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        guild_id = guild.id
        if guild_id in self.cache and self.cache[guild_id]['log_member_ban_unban']:
            modlog_id = self.cache[guild_id].get('modlog_id', self.cache[guild_id].get('channel_id'))
            channel = self.bot.get_channel(modlog_id)
            if user.avatar:
                user_avatar_url = user.avatar.url
            else:
                user_avatar_url = user.default_avatar_url
            user_id = user.id
            embed = discord.Embed(title="Member Banned", description=f"{user.mention} was banned from the server.", color=discord.Color.red())
            embed.set_author(name=user.display_name, icon_url=user_avatar_url)
            embed.add_field(name="User ID", value=user_id, inline=True)
            embed.add_field(name="Username", value=user.name, inline=True)
            await channel.send(embed=embed)

    # logs unbans
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        guild_id = guild.id
        if guild_id in self.cache and self.cache[guild_id]['log_member_ban_unban']:
            modlog_id = self.cache[guild_id].get('modlog_id', self.cache[guild_id].get('channel_id'))
            channel = self.bot.get_channel(modlog_id)
            embed = discord.Embed(title="Member Unbanned", description=f"**{user.name}** was unbanned from the server.", color=discord.Color.green())
            embed.add_field(name="User ID", value=user.id, inline=True)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_automod_action(self, execution):
        guild_id = execution.guild_id
        if guild_id in self.cache and self.cache[guild_id]['log_automod_actions']:
            message_id = execution.message_id
            if message_id not in self.pending_executions:
                self.pending_executions[message_id] = []
            self.pending_executions[message_id].append(execution)
            await asyncio.sleep(0.3)
            if message_id not in self.pending_executions:
                return
            executions = self.pending_executions.pop(message_id)
            if any(e.action.type == AutoModRuleActionType.send_alert_message for e in executions):
                return
            guild_id = execution.guild_id
            modlog_id = self.cache[guild_id].get('modlog_id', self.cache[guild_id].get('channel_id'))
            channel = self.bot.get_channel(modlog_id)
            action_details = []
            duration = None
            for e in executions:
                action = e.action.type
                action_name = self.action_type_names.get(action, str(action))
                action_details.append(action_name)
                if action == AutoModRuleActionType.timeout:
                    duration = e.action.duration
            embed = discord.Embed(
                title="Automod Action",
                description=f"Actions: {', '.join(action_details)}\n"
                            f"User: {execution.member.mention}\n"
                            f"Reason: {execution.matched_content}",
                color=discord.Color.red()
            )
            if execution.member.avatar:
                user_avatar_url = execution.member.avatar.url
            else:
                user_avatar_url = execution.member.default_avatar_url
            embed.set_author(name=execution.member.display_name, icon_url=user_avatar_url)
            if duration:
                formatted_duration = format_time(duration)
                embed.add_field(name="Duration", value=formatted_duration, inline=False)
            embed.add_field(name="User ID", value=execution.member.id, inline=True)
            await channel.send(embed=embed)


async def setup(bot):
    logging_cog = LoggingCog(bot)
    await logging_cog.setup()
    await bot.add_cog(logging_cog)