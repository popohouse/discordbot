import discord
from discord.ext import commands
import os

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        guild = self.bot.get_guild( payload.guild_id)
        if not guild:
            return
        if not self.is_logging_enabled(guild.id, "message_delete"):
            return
        log_channel = self.get_log_channel(guild.id)
        if not log_channel:
            return
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        try:
            message = payload.cached_message
        except discord.NotFound:
            return
        embed = discord.Embed(title="Message Deleted", description=f"Message sent by {message.author.mention} in {channel.mention} was deleted.", color=discord.Color.red())
        embed.add_field(name="Content", value=message.content)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild:
            return
        if not self.is_logging_enabled(before.guild.id, "message_edit"):
            return
        log_channel = self.get_log_channel(before.guild.id)
        if not log_channel:
            return
        embed = discord.Embed(title="Message Edited", description=f"Message sent by {before.author.mention} in {before.channel.mention} was edited.", color=discord.Color.orange())
        embed.add_field(name="Before", value=before.content)
        embed.add_field(name="After", value=after.content)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.guild:
            return
        if before.nick != after.nick:
            if not self.is_logging_enabled(before.guild.id, "nick_change"):
                return
            log_channel = self.get_log_channel(before.guild.id)
            if not log_channel:
                return
            embed = discord.Embed(title="Nickname Changed", description=f"{before.mention} changed their nickname.", color=discord.Color.blue())
            embed.add_field(name="Before", value=before.nick)
            embed.add_field(name="After", value=after.nick)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.guild:
            return
        if not self.is_logging_enabled(member.guild.id, "member_join"):
            return
        log_channel = self.get_log_channel(member.guild.id)
        if not log_channel:
            return
        embed = discord.Embed(title="Member Joined", description=f"{member.mention} joined the server.", color=discord.Color.green())
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.guild:
            return
        if not self.is_logging_enabled(member.guild.id, "member_remove"):
            return
        log_channel = self.get_log_channel(member.guild.id)
        if not log_channel:
            return
        embed = discord.Embed(title="Member Left", description=f"{member.mention} left the server.", color=discord.Color.red())
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not guild:
            return
        if not self.is_logging_enabled(guild.id, "guild_join"):
            return
        log_channel = self.get_log_channel(guild.id)
        if not log_channel:
            return
        embed = discord.Embed(title="Bot Joined Server", description=f"Bot was added to {guild.name}.", color=discord.Color.green())
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not guild:
            return
        if not self.is_logging_enabled(guild.id, "member_ban"):
            return
        log_channel = self.get_log_channel(guild.id)
        if not log_channel:
            return
        embed = discord.Embed(title="Member Banned", description=f"{user.mention} was banned from the server.", color=discord.Color.red())
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if not guild:
            return
        if not self.is_logging_enabled(guild.id, "member_unban"):
            return
        log_channel = self.get_log_channel(guild.id)
        if not log_channel:
            return
        embed = discord.Embed(title="Member Unbanned", description=f"{user.mention} was unbanned from the server.", color=discord.Color.green())
        await log_channel.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def setlog(self, ctx):
        await ctx.send("Use this command to enable or disable individual logging types and set the logging channel. Use `setlog types` to see a list of logging types and `setlog channel #channel` to set the logging channel.")

    @setlog.command()
    async def types(self, ctx):
        log_types = ["message_delete", "message_edit", "nick_change", "member_join", "member_remove", "guild_join", "member_ban", "member_unban"]
        await ctx.send(f"Available log types: {', '.join(log_types)}")

    @setlog.command()
    async def enable(self, ctx, log_type: str):
        if not self.is_valid_log_type(log_type):
            await ctx.send(f"Invalid log type. Use `setlog types` to see a list of valid log types.")
            return
        self.set_logging(ctx.guild.id, log_type, True)
        await ctx.send(f"Enabled logging for {log_type}.")

    @setlog.command()
    async def disable(self, ctx, log_type: str):
        if not self.is_valid_log_type(log_type):
            await ctx.send(f"Invalid log type. Use `setlog types` to see a list of valid log types.")
            return
        self.set_logging(ctx.guild.id, log_type, False)
        await ctx.send(f"Disabled logging for {log_type}.")

    @setlog.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        self.set_log_channel(ctx.guild.id, channel.id)
        await ctx.send(f"Set logging channel to {channel.mention}.")

    @setlog.command()
    async def enableall(self, ctx):
        log_types = ["message_delete", "message_edit", "nick_change", "member_join", "member_remove", "guild_join", "member_ban", "member_unban"]
        for log_type in log_types:
            self.set_logging(ctx.guild.id, log_type, True)
        await ctx.send(f"Enabled logging for all log types.")

    @setlog.command()
    async def disableall(self, ctx):
        log_types = ["message_delete", "message_edit", "nick_change", "member_join", "member_remove", "guild_join", "member_ban", "member_unban"]
        for log_type in log_types:
            self.set_logging(ctx.guild.id, log_type, False)
        await ctx.send(f"Disabled logging for all log types.")

    def is_valid_log_type(self, log_type):
        return log_type in ["message_delete", "message_edit", "nick_change", "member_join", "member_remove", "guild_join", "member_ban", "member_unban"]

    def is_logging_enabled(self, guild_id, log_type):
        if not os.path.exists(f"GuildLogs/{guild_id}"):
            os.makedirs(f"GuildLogs/{guild_id}")
        if not os.path.exists(f"GuildLogs/{guild_id}/{log_type}.txt"):
            with open(f"GuildLogs/{guild_id}/{log_type}.txt", "w") as f:
                f.write("False")
            return False
        with open(f"GuildLogs/{guild_id}/{log_type}.txt", "r") as f:
            return f.read().strip() == "True"

    def set_logging(self, guild_id, log_type, enabled):
        if not os.path.exists(f"GuildLogs/{guild_id}"):
            os.makedirs(f"GuildLogs/{guild_id}")
        with open(f"GuildLogs/{guild_id}/{log_type}.txt", "w") as f:
            f.write(str(enabled))

    def get_log_channel(self, guild_id):
        if not os.path.exists(f"GuildLogs/{guild_id}/channel.txt"):
            return None
        with open(f"GuildLogs/{guild_id}/channel.txt", "r") as f:
            channel_id = int(f.read().strip())
            return self.bot.get_channel(channel_id)

    def set_log_channel(self, guild_id, channel_id):
        if not os.path.exists(f"GuildLogs/{guild_id}"):
            os.makedirs(f"GuildLogs/{guild_id}")
        with open(f"GuildLogs/{guild_id}/channel.txt", "w") as f:
            f.write(str(channel_id))

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))