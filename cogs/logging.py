import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime
from typing import Optional

from utils.config import Config

config = Config.from_env()


class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_settings = {}

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_settings = {}

    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.pool.acquire() as conn:


            rows = await conn.fetch('SELECT guild_id, channel_id, log_deleted_messages, log_edited_messages, log_nickname_changes, log_member_join_leave, log_member_kick, log_member_ban_unban FROM logging')


            for row in rows:
                guild_id = row[0]
                channel_id = row[1]
                log_deleted_messages = row[2]
                log_edited_messages = row[3]
                log_nickname_changes = row[4]
                log_member_join_leave = row[5]
                log_member_kick = row[6]
                log_member_ban_unban = row[7]
                mod_channel_id = row[8]

                self.logging_settings[guild_id] = {
                    'channel_id': channel_id,
                    'log_deleted_messages': log_deleted_messages,
                    'log_edited_messages': log_edited_messages,
                    'log_nickname_changes': log_nickname_changes,
                    'log_member_join_leave': log_member_join_leave,
                    'log_member_kick': log_member_kick,
                    'log_member_ban_unban': log_member_ban_unban,
                    'mod_channel_id': mod_channel_id
                }


    #Log command
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
    ])
    async def log(self, interaction: discord.Interaction, log_type: Optional[app_commands.Choice[str]], disable: Optional[bool] = None):
        """Enable or disable logging type"""
        async with self.bot.pool.acquire() as conn:

        #Disable logging types
            if disable == True:
                if log_type.value == 'all':
                    await conn.execute('UPDATE logging SET log_deleted_messages = false, log_edited_messages = false, log_nickname_changes = false, log_member_join_leave = false, log_member_kick = false, log_member_ban_unban = false WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_deleted_messages'] = False
                    self.logging_settings[interaction.guild.id]['log_edited_messages'] = False
                    self.logging_settings[interaction.guild.id]['log_nickname_changes'] = False
                    self.logging_settings[interaction.guild.id]['log_member_join_leave'] = False
                    self.logging_settings[interaction.guild.id]['log_member_kick'] = False
                    self.logging_settings[interaction.guild.id]['log_member_ban_unban'] = False
                elif log_type.value == 'log_deleted_messages':
                    await conn.execute('UPDATE logging SET log_deleted_messages = false WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_deleted_messages'] = False
                elif log_type.value == 'log_edited_messages':
                    await conn.execute('UPDATE logging SET log_edited_messages = false WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_edited_messages'] = False
                elif log_type.value == 'log_nickname_changes':
                    conn.execute('UPDATE logging SET log_nickname_changes = false WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_nickname_changes'] = False
                elif log_type.value == 'log_member_join_leave':
                    await conn.execute('UPDATE logging SET log_member_join_leave = false WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_member_join_leave'] = False
                elif log_type.value == 'log_member_kick':
                    await conn.execute('UPDATE logging SET log_member_kick = false WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_member_kick'] = False
                elif log_type.value == 'log_member_ban_unban':
                    await conn.execute('UPDATE logging SET log_member_ban_unban = false WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_member_ban_unban'] = False
                else:
                    await interaction.response.send_message(f'Invalid log type: {log_type.value}')
                    return

                await interaction.response.send_message(f'Disabled logging for {log_type.value}')
            

        #Enable logging type
            if disable == None:
                if log_type.value == 'all':
                    await conn.execute('UPDATE logging SET log_deleted_messages = true, log_edited_messages = true, log_nickname_changes = true, log_member_join_leave = true, log_member_kick = true, log_member_ban_unban = true WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_deleted_messages'] = True
                    self.logging_settings[interaction.guild.id]['log_edited_messages'] = True
                    self.logging_settings[interaction.guild.id]['log_nickname_changes'] = True
                    self.logging_settings[interaction.guild.id]['log_member_join_leave'] = True
                    self.logging_settings[interaction.guild.id]['log_member_kick'] = True
                    self.logging_settings[interaction.guild.id]['log_member_ban_unban'] = True
                elif log_type.value == 'log_deleted_messages':
                    await conn.execute('UPDATE logging SET log_deleted_messages = true WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_deleted_messages'] = True
                elif log_type.value == 'log_edited_messages':
                    await conn.execute('UPDATE logging SET log_edited_messages = true WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_edited_messages'] = True
                elif log_type.value == 'log_nickname_changes':
                    await conn.execute('UPDATE logging SET log_nickname_changes = true WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_nickname_changes'] = True
                elif log_type.value == 'log_member_join_leave':
                    await conn.execute('UPDATE logging SET log_member_join_leave = true WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_member_join_leave'] = True
                elif log_type.value == 'log_member_kick':
                    await conn.execute('UPDATE logging SET log_member_kick = true WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_member_kick'] = True
                elif log_type.value == 'log_member_ban_unban':
                    await conn.execute('UPDATE logging SET log_member_ban_unban = true WHERE guild_id = $1', interaction.guild.id)
                    self.logging_settings[interaction.guild.id]['log_member_ban_unban'] = True
                else:
                    await interaction.response.send_message(f'Invalid log type: {log_type.value}')
                    return
                await interaction.response.send_message(f'Enabled logging for {log_type.value}')


    @app_commands.command()
    @commands.guild_only()
    async def setlogchannel(self, interaction: discord.Interaction, logchannel: Optional[discord.TextChannel], modchannel: Optional[discord.TextChannel]):
        async with self.bot.pool.acquire() as conn:
            #Set main log channel 
            if logchannel is not None:
                row = await conn.fetch('SELECT * FROM logging WHERE guild_id = $1', interaction.guild.id)
                if row:
                    await conn.execute('UPDATE logging SET channel_id = $2 WHERE guild_id = $1', logchannel.id, interaction.guild.id)
                else:
                    await conn.execute('INSERT INTO logging (guild_id, channel_id) VALUES ($1, $2)', interaction.guild.id, logchannel.id)
                await conn.close()
                if interaction.guild.id in self.logging_settings:
                    self.logging_settings[interaction.guild.id]['channel_id'] = logchannel.id
                else:
                    self.logging_settings[interaction.guild.id] = {
                        'channel_id': logchannel.id,
                        'log_deleted_messages': 0,
                        'log_edited_messages': 0,
                        'log_nickname_changes': 0,
                        'log_member_join_leave': 0,
                        'log_member_kick': 0,
                        'log_member_ban_unban': 0
                }
                await interaction.response.send_message(f'Set logging channel to {logchannel.mention}')

            #Set mod log channel
                if modchannel is not None:
                    row = await conn.fetch('SELECT * FROM logging WHERE guild_id = $1', interaction.guild.id)
                    if row:
                        await conn.execute('UPDATE logging SET modlog_id = $2 WHERE guild_id = $1', modchannel.id, interaction.guild.id)
                    else:
                        await conn.execute('INSERT INTO logging (guild_id, modlog_id) VALUES ($1, $2)', interaction.guild.id, modchannel.id)
                    await conn.close()
                    if interaction.guild.id in self.logging_settings:
                        self.logging_settings[interaction.guild.id]['modlog_id'] = modchannel.id
                    else:
                        self.logging_settings[interaction.guild.id] = {
                            'modlog_id': modchannel.id,
                            'log_deleted_messages': 0,
                            'log_edited_messages': 0,
                            'log_nickname_changes': 0,
                            'log_member_join_leave': 0,
                            'log_member_kick': 0,
                            'log_member_ban_unban': 0
                    }
                    await interaction.response.send_message(f'Set logging channel to {modchannel.mention}')





    ###Event listeners for all logging types below###


    #Message delete listener(should be in finished state)
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild_id = message.guild.id
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_deleted_messages']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            
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
            
            embed = discord.Embed(title="Message Deleted", description=description + f"\n\n**Content**\n{message.content}\n\n**Date**\n<t:{int(message.created_at.timestamp())}>", color=discord.Color.red())
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
            await channel.send(embed=embed)




    #Message edit logging(should be in finished state)
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        guild_id = before.guild.id

        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_edited_messages']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            if before.content == after.content:
                return
            embed = discord.Embed(title="Message Edited", description=f"Message sent by {before.author.mention} in {before.channel.mention} was edited.\n\n**Before**\n{before.content}\n\n**After**\n[{after.content}]({after.jump_url})\n\n**Date**\n<t:{int(after.edited_at.timestamp())}>", color=discord.Color.orange())
            embed.set_author(name=before.author.display_name, icon_url=before.author.avatar.url)
            await channel.send(embed=embed)
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        guild_id = before.guild.id

        if guild_id in self.logging_settings and self.logging.settings[guild_id]['log_nickname_changes']:
                if before.username != after.username:
                    channel_id = self.logging_settings[guild_id]['channel_id']
                    channel = self.bot.get_channel(channel_id)

                    embed = discord.Embed(title="Username Changed", description=f"{before.mention} changed their username.\n\n**Before**\n{before.username or before.name}\n\n**After**\n{after.username or after.name}\n\n**Date**\n<t:{int(datetime.utcnow().timestamp())}>", color=discord.Color.blue())
                    embed.set_author(name=before.display_name, icon_url=before.avatar.url)
                    await channel.send(embed=embed)


    #Currently only logs nickname change, could be user for avatar as well. 
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild_id = before.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_nickname_changes']:
            # Check if the nickname changed
            if before.nick != after.nick:
                channel_id = self.logging_settings[guild_id]['channel_id']
                channel = self.bot.get_channel(channel_id)

                embed = discord.Embed(title="Nickname Changed", description=f"{before.mention} changed their nickname.\n\n**Before**\n{before.nick or before.name}\n\n**After**\n{after.nick or after.name}\n\n**Date**\n<t:{int(datetime.utcnow().timestamp())}>", color=discord.Color.blue())
                embed.set_author(name=before.display_name, icon_url=before.avatar.url)
                await channel.send(embed=embed)

    #Logs user join, note the prejoin state of community servers will be run on on_member_remove
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("member joined")
        guild_id = member.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_member_join_leave']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="Member Left", description=f"{member.mention} left the server.", color=discord.Color.red())
            await channel.send(embed=embed)


    #Logs user leaves a guild, note the prejoin state of community servers will be run on on_member_remove
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print("member removed")
        guild_id = member.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_member_join_leave']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            embed = discord.Embed(title="Member Left", description=f"{member.mention} left the server.", color=discord.Color.red())
            await channel.send(embed=embed)


    #Log bans
    @commands.Cog.listener()
    async def on_member_ban(self, member):
        guild_id = member.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['modlog_id']:
            modlog_id = self.logging_settings[guild_id]['modlog_id']
            channel = self.bot.get_channel(modlog_id)
            embed = discord.Embed(title="Member Banned", description=f"{member.mention} was banned from the server.", color=discord.Color.red())
            await channel.send(embed=embed)


    #logs unbans
    @commands.Cog.listener()
    async def on_member_unban(self, member):
        guild_id = member.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_member_ban_unban']:
            modlog_id = self.logging_settings[guild_id]['modlog_id']
            channel = self.bot.get_channel(modlog_id)
            embed = discord.Embed(title="Member Unbanned", description=f"{member.mention} was unbanned from the server.", color=discord.Color.red())
            await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(LoggingCog(bot))