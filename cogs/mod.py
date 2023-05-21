import discord
from discord import app_commands
from typing import Optional

from discord.ext import commands
from utils.data import DiscordBot
from utils import permissions, default

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
        print(f"Kick command called by {interaction.user} with arguments: {target}, {reason}")
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
    @permissions.has_permissions(manage_server=True)
    async def modrole(self, interaction: discord.Interaction, role: discord.Role):
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