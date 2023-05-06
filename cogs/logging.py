from discord.ext import commands
import sqlite3
import discord

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
        conn = sqlite3.connect('data/MeowMix.db')
        c = conn.cursor()

        c.execute('SELECT guild_id, channel_id, log_deleted_messages, log_edited_messages, log_nickname_changes, log_member_join_leave, log_member_kick, log_member_ban_unban FROM logging')
        rows = c.fetchall()

        for row in rows:
            guild_id = row[0]
            channel_id = row[1]
            log_deleted_messages = row[2]
            log_edited_messages = row[3]
            log_nickname_changes = row[4]
            log_member_join_leave = row[5]
            log_member_kick = row[6]
            log_member_ban_unban = row[7]

            self.logging_settings[guild_id] = {
                'channel_id': channel_id,
                'log_deleted_messages': log_deleted_messages,
                'log_edited_messages': log_edited_messages,
                'log_nickname_changes': log_nickname_changes,
                'log_member_join_leave': log_member_join_leave,
                'log_member_kick': log_member_kick,
                'log_member_ban_unban': log_member_ban_unban
            }

        conn.close()



            #Enable logs type
    @commands.command()
    async def enable_logging(self, ctx, log_type: str):
        conn = sqlite3.connect('data/MeowMix.db')
        c = conn.cursor()

        if log_type == 'all':
            c.execute('UPDATE logging SET log_deleted_messages = 1, log_edited_messages = 1, log_nickname_changes = 1, log_member_join_leave = 1, log_member_kick = 1, log_member_ban_unban = 1 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_deleted_messages'] = True
            self.logging_settings[ctx.guild.id]['log_edited_messages'] = True
            self.logging_settings[ctx.guild.id]['log_nickname_changes'] = True
            self.logging_settings[ctx.guild.id]['log_member_join_leave'] = True
            self.logging_settings[ctx.guild.id]['log_member_kick'] = True
            self.logging_settings[ctx.guild.id]['log_member_ban_unban'] = True
        elif log_type == 'deleted_messages':
            c.execute('UPDATE logging SET log_deleted_messages = 1 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_deleted_messages'] = True
        elif log_type == 'edited_messages':
            c.execute('UPDATE logging SET log_edited_messages = 1 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_edited_messages'] = True
        elif log_type == 'nickname_changes':
            c.execute('UPDATE logging SET log_nickname_changes = 1 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_nickname_changes'] = True
        elif log_type == 'member_join_leave':
            c.execute('UPDATE logging SET log_member_join_leave = 1 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_member_join_leave'] = True
        elif log_type == 'member_kick':
            c.execute('UPDATE logging SET log_member_kick = 1 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_member_kick'] = True
        elif log_type == 'member_ban_unban':
            c.execute('UPDATE logging SET log_member_ban_unban = 1 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_member_ban_unban'] = True
        else:
            await ctx.send(f'Invalid log type: {log_type}')
            return

        conn.commit()
        conn.close()

        await ctx.send(f'Enabled logging for {log_type}')

        #Disable log type
    @commands.command()
    async def disable_logging(self, ctx, log_type: str):
        conn = sqlite3.connect('data/MeowMix.db')
        c = conn.cursor()

        if log_type == 'all':
            c.execute('UPDATE logging SET log_deleted_messages = 0, log_edited_messages = 0, log_nickname_changes = 0, log_member_join_leave = 0, log_member_kick = 0, log_member_ban_unban = 0 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_deleted_messages'] = False
            self.logging_settings[ctx.guild.id]['log_edited_messages'] = False
            self.logging_settings[ctx.guild.id]['log_nickname_changes'] = False
            self.logging_settings[ctx.guild.id]['log_member_join_leave'] = False
            self.logging_settings[ctx.guild.id]['log_member_kick'] = False
            self.logging_settings[ctx.guild.id]['log_member_ban_unban'] = False
        elif log_type == 'deleted_messages':
            c.execute('UPDATE logging SET log_deleted_messages = 0 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_deleted_messages'] = False
        elif log_type == 'edited_messages':
            c.execute('UPDATE logging SET log_edited_messages = 0 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_edited_messages'] = False
        elif log_type == 'nickname_changes':
            c.execute('UPDATE logging SET log_nickname_changes = 0 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_nickname_changes'] = False
        elif log_type == 'member_join_leave':
            c.execute('UPDATE logging SET log_member_join_leave = 0 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_member_join_leave'] = False
        elif log_type == 'member_kick':
            c.execute('UPDATE logging SET log_member_kick = 0 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_member_kick'] = False
        elif log_type == 'member_ban_unban':
            c.execute('UPDATE logging SET log_member_ban_unban = 0 WHERE guild_id = ?', (ctx.guild.id,))
            self.logging_settings[ctx.guild.id]['log_member_ban_unban'] = False
        else:
            await ctx.send(f'Invalid log type: {log_type}')
            return

        conn.commit()
        conn.close()

        await ctx.send(f'Disabled logging for {log_type}')


        #Manages of setting log channel
    @commands.command()
    async def set_logging_channel(self, ctx, channel: discord.TextChannel):
        conn = sqlite3.connect('data/MeowMix.db')
        c = conn.cursor()

        c.execute('SELECT * FROM logging WHERE guild_id = ?', (ctx.guild.id,))
        row = c.fetchone()

        if row:
            c.execute('UPDATE logging SET channel_id = ? WHERE guild_id = ?', (channel.id, ctx.guild.id))
        else:
            c.execute('INSERT INTO logging (guild_id, channel_id) VALUES (?, ?)', (ctx.guild.id, channel.id))

        conn.commit()
        conn.close()

        await ctx.send(f'Set logging channel to {channel.mention}')


            #Message delete listener
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild_id = message.guild.id

        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_deleted_messages']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            embed = discord.Embed(title="Message Deleted", description=f"Message sent by {message.author.mention} in {message.channel.mention} was deleted.", color=discord.Color.red())
            embed.add_field(name="Content", value=message.content)
            await channel.send(embed=embed)


        #Message edit logging
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        guild_id = self.guild.id

        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_edited_messages']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)
            
            embed = discord.Embed(title="Message Edited", description=f"Message sent by {before.author.mention} in {before.channel.mention} was edited.", color=discord.Color.orange())
            embed.add_field(name="Before", value=before.content)
            embed.add_field(name="After", value=after.content)
            await channel.send(embed=embed)


        #nickname logging
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild_id = self.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_nickname_changes']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="Nickname Changed", description=f"{before.mention} changed their nickname.", color=discord.Color.blue())
            embed.add_field(name="Before", value=before.nick)
            embed.add_field(name="After", value=after.nick)

            await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = self.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_member_join_leave']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="Member Left", description=f"{member.mention} left the server.", color=discord.Color.red())
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = self.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_member_join_leave']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="Member Left", description=f"{member.mention} left the server.", color=discord.Color.red())
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, member):
        guild_id = self.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_member_ban_unban']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="Member Banned", description=f"{user.mention} was banned from the server.", color=discord.Color.red())
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, member):
        guild_id = self.guild.id
        
        if guild_id in self.logging_settings and self.logging_settings[guild_id]['log_member_ban_unban']:
            channel_id = self.logging_settings[guild_id]['channel_id']
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(title="Member Banned", description=f"{user.mention} was banned from the server.", color=discord.Color.red())
            await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(LoggingCog(bot))