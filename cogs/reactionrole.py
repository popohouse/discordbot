from discord.ext import commands
import discord
from discord import app_commands
import asyncpg
from utils.config import Config
from utils import permissions

config = Config.from_env()


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = {}
        self.bot.loop.create_task(self.cache_reaction_roles())

    async def cache_reaction_roles(self):
        async with self.bot.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM reaction_roles')
            for row in rows:
                guild_id = row['guild_id']
                message_id = row['message_id']
                emoji = row['emoji']
                role_id = row['role_id']
                if guild_id not in self.reaction_roles:
                    self.reaction_roles[guild_id] = {}
                if message_id not in self.reaction_roles[guild_id]:
                    self.reaction_roles[guild_id][message_id] = {}
                self.reaction_roles[guild_id][message_id][emoji] = role_id

    @app_commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def reactionrole(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        """Create reaction role"""
        if not await permissions.check_priv(self.bot, interaction, None, {"manage_guild": True}):
            return
        async with self.bot.pool.acquire() as conn: 
            total_rr = await conn.fetchval("SELECT COUNT(*) FROM reaction_roles WHERE guild_id = $1", interaction.guild.id)
        if total_rr >= 20:
            await interaction.response.send_message('You can only have 20 reaction roles per guild.', ephemeral=True)
            return
        message_id = int(message_id)
        try:
            message = await interaction.channel.fetch_message(message_id)
        except discord.NotFound:
            try:
                message = await interaction.channel.fetch_message(message_id)
            except discord.NotFound:
                await interaction.response.send_message('The specified message was not found.', ephemeral=True)
                return

        await message.add_reaction(emoji)
        async with self.bot.pool.acquire() as conn:
            try:
                await conn.execute('''
                    INSERT INTO reaction_roles (guild_id, message_id, emoji, role_id)
                    VALUES ($1, $2, $3, $4)
                ''', interaction.guild.id, message_id, str(emoji), role.id)
                await interaction.response.send_message('Successful reaction role added', ephemeral=True)
            except asyncpg.UniqueViolationError:
                await interaction.response.send_message('This reaction role already exists!', ephemeral=True)
            if interaction.guild.id not in self.reaction_roles:
                self.reaction_roles[interaction.guild.id] = {}
            if message_id not in self.reaction_roles[interaction.guild.id]:
                self.reaction_roles[interaction.guild.id][message_id] = {}
            self.reaction_roles[interaction.guild.id][message_id][str(emoji)] = role.id

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        guild_id = payload.guild_id
        message_id = payload.message_id
        emoji = str(payload.emoji)
        if guild_id in self.reaction_roles and message_id in self.reaction_roles[guild_id] and emoji in self.reaction_roles[guild_id][message_id]:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(message_id)
            await message.remove_reaction(emoji, payload.member)
            role_id = self.reaction_roles[guild_id][message_id][emoji]
            role = payload.member.guild.get_role(role_id)
            await payload.member.add_roles(role)
        elif guild_id in self.reaction_roles and message_id in self.reaction_roles[guild_id] and emoji not in self.reaction_roles[guild_id][message_id]:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(message_id)
            await message.remove_reaction(emoji, payload.member)

    @commands.Cog.listener()
    async def on_ready(bot):
        await bot.cache_reaction_roles()


@commands.Cog.listener()
async def on_message_delete(self, message):
    async with self.bot.pool.acquire() as conn:
        await conn.execute('''
            DELETE FROM reaction_roles
            WHERE guild_id = $1 AND message_id = $2
        ''', message.guild.id, message.id)
    if message.guild.id in self.reaction_roles and message.id in self.reaction_roles[message.guild.id]:
        del self.reaction_roles[message.guild.id][message.id]


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))