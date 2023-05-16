from discord.ext import commands
import discord
import asyncpg

from utils.config import Config

config = Config.from_env()

db_host = config.postgres_host
db_name = config.postgres_name
db_user = config.postgres_user
db_password = config.postgres_password

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = {}
        self.bot.loop.create_task(self.cache_reaction_roles())

    async def cache_reaction_roles(self):
        conn = await asyncpg.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
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
        await conn.close()

    @commands.hybrid_command(name="reactionrole")
    async def reactionrole_command(self, ctx, message_id: str, emoji: str, role: discord.Role):
        """Create reaction role"""
        if interaction.user.id == self.bot.config.discord_owner_id:
            message_id = int(message_id)
            message = await ctx.channel.fetch_message(message_id)
            await message.add_reaction(emoji)

            conn = await asyncpg.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            try:
                await conn.execute('''
                    INSERT INTO reaction_roles (guild_id, message_id, emoji, role_id)
                    VALUES ($1, $2, $3, $4)
                ''', ctx.guild.id, message_id, str(emoji), role.id)
                await ctx.send('Successful reaction role added')
            except asyncpg.UniqueViolationError:
                await ctx.send('This reaction role already exists!')
            finally:
                await conn.close()

            if ctx.guild.id not in self.reaction_roles:
                self.reaction_roles[ctx.guild.id] = {}
            if message_id not in self.reaction_roles[ctx.guild.id]:
                self.reaction_roles[ctx.guild.id][message_id] = {}
            self.reaction_roles[ctx.guild.id][message_id][str(emoji)] = role.id
        else:
            await ctx.send(f"Sir you are not popo")
            
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


# Cleanup old reaction role from dB
async def cleanup_reaction_roles(self):
    guild_ids = [guild.id for guild in self.bot.guilds]
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    await conn.execute('''
        DELETE FROM reaction_roles
        WHERE guild_id != ALL($1)
    ''', guild_ids)
    await conn.close()

@commands.Cog.listener()
async def on_message_delete(self, message):
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    await conn.execute('''
        DELETE FROM reaction_roles
        WHERE guild_id = $1 AND message_id = $2
    ''', message.guild.id, message.id)
    await conn.close()

    if message.guild.id in self.reaction_roles and message.id in self.reaction_roles[message.guild.id]:
        del self.reaction_roles[message.guild.id][message.id]    


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
