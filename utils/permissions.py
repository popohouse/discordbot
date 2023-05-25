import discord

from discord.ext import commands


from utils.config import Config
import asyncpg

config = Config.from_env()

db_host = config.postgres_host
db_name = config.postgres_name
db_user = config.postgres_user
db_password = config.postgres_password

async def check_permissions(interaction: discord.Interaction, perms, *, check=all) -> bool:
    """ Checks if author has permissions to a permission """
    if interaction.user.id == config.discord_owner_id:
        return True

    # Check if user has required permissions
    resolved = interaction.channel.permissions_for(interaction.user)
    if check(getattr(resolved, name, None) == value for name, value in perms.items()):
        return True

    # Check if user belongs to mod role
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    mod_role_id = await conn.fetchval('SELECT role_id FROM mod_role_id WHERE guild_id = $1', interaction.guild_id)
    await conn.close()
    if mod_role_id is not None:
        member = interaction.guild.get_member(interaction.user.id)
        if any(role.id == mod_role_id for role in member.roles):
            return True

    return False


def has_permissions(*, check=all, **perms) -> bool:
    """ discord.Commands method to check if author has permissions """
    async def pred(interaction: discord.Interaction):
        return await check_permissions(interaction, perms, check=check)
    return commands.check(pred)

async def check_priv(bot, interaction: discord.Interaction, target: discord.Member, perms) -> bool:
    if target is None:
        member = interaction.guild.get_member(interaction.user.id)
        has_required_permission = all(getattr(member.guild_permissions, name, None) == value for name, value in perms.items())

        if has_required_permission:
            return True
        else:
            await interaction.response.send_message(f"Not a mod sadchamp")
            return False

    bot_member = interaction.guild.get_member(bot.user.id)
    # Self checks
    if target.id == interaction.user.id:
        await interaction.response.send_message(f"You can't {interaction.command.name} yourself")
        return False
    elif target.id == bot.user.id:
        await interaction.response.send_message("So that's what you think of me huh..? sad ;-;")
        return False

    # Check if user has mod role or required permission
    has_mod_role = False
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    mod_role_id = await conn.fetchval('SELECT role_id FROM mod_role_id WHERE guild_id = $1', interaction.guild_id)
    await conn.close()
    if mod_role_id is not None:
        member = interaction.guild.get_member(interaction.user.id)
        if any(role.id == mod_role_id for role in member.roles):
            has_mod_role = True

    has_required_permission = all(getattr(interaction.channel.permissions_for(interaction.user), name, None) == value for name, value in perms.items())

    if has_mod_role or has_required_permission:
        # Check if target user is above user in role hierarchy
        if interaction.user.top_role <= target.top_role:
            await interaction.response.send_message(f"Nope, you can't {interaction.command.name} someone higher than yourself.")
            return False
        else:
            return True
    else:
        await interaction.response.send_message(f"Not a mod sadchamp")
        return False




def can_handle(interaction: discord.Interaction, permission: str) -> bool:
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(interaction.channel, discord.DMChannel) or \
        getattr(interaction.channel.permissions_for(interaction.guild.me), permission)