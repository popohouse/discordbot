import discord
from discord.ext import commands
from utils.config import Config

config = Config.from_env()


async def check_permissions(self, interaction: discord.Interaction, perms, *, check=all) -> bool:
    """Checks if author has permissions to a permission"""
    # Check if user has required permissions
    if 'manage_guild' in perms:
        resolved = interaction.guild_permissions_for(interaction.user)
    else:
        resolved = interaction.channel.permissions_for(interaction.user)
    if check(getattr(resolved, name, None) == value for name, value in perms.items()):
        return True
    # Check if user belongs to mod role, but only if 'manage_guild' is not being checked
    if 'manage_guild' not in perms:
        async with self.bot.pool.acquire() as conn:
            mod_role_id = await conn.fetchval('SELECT role_id FROM mod_role_id WHERE guild_id = $1', interaction.guild_id)
            if mod_role_id is not None:
                member = interaction.guild.get_member(interaction.user.id)
                if any(role.id == mod_role_id for role in member.roles):
                    return True
    return False


def has_permissions(*, check=all, **perms) -> bool:
    """discord.Commands method to check if author has permissions"""
    async def pred(interaction: discord.Interaction):
        return await check_permissions(interaction, perms, check=check)
    return commands.check(pred)


async def check_priv(bot, interaction: discord.Interaction, target: discord.Member, perms, skip_self_checks=False) -> bool:
    # mod role check :)
    has_mod_role = False
    async with bot.pool.acquire() as conn:
        mod_role_id = await conn.fetchval('SELECT role_id FROM mod_role_id WHERE guild_id = $1', interaction.guild_id)
        if mod_role_id is not None:
            member = interaction.guild.get_member(interaction.user.id)
            if any(role.id == mod_role_id for role in member.roles):
                has_mod_role = True
        if 'manage_guild' in perms:
            member = interaction.guild.get_member(interaction.user.id)
            has_required_permission = all(getattr(member.guild_permissions, name, None) == value for name, value in perms.items())
            if has_required_permission:
                return True
            if has_mod_role is True and has_required_permission is False:
                await interaction.response.send_message("Lack permissions")
                return False
            await interaction.response.send_message("Not a mod sadchamp")
            return False
        if 'manage_messages' in perms:
            member = interaction.guild.get_member(interaction.user.id)
            has_required_permission = all(getattr(member.guild_permissions, name, None) == value for name, value in perms.items())
            if has_required_permission or has_mod_role:
                return True
            await interaction.response.send_message("Not a mod sadchamp")
            return False
        if 'manage_channels' in perms:
            member = interaction.guild.get_member(interaction.user.id)
            has_required_permission = all(getattr(member.guild_permissions, name, None) == value for name, value in perms.items())
            if has_required_permission or has_mod_role:
                return True
            await interaction.response.send_message("Not a mod sadchamp")
            return False
        # Self checks
        if not skip_self_checks:
            if target.id == interaction.user.id:
                await interaction.response.send_message(f"You can't {interaction.command.name} yourself", ephemeral=True)
                return False
            elif target.id == bot.user.id:
                await interaction.response.send_message("So that's what you think of me huh..? sad ;-;", ephemeral=True)
                return False
        # Has Req perm check before following block
        has_required_permission = all(getattr(interaction.channel.permissions_for(interaction.user), name, None) == value for name, value in perms.items())
        if has_mod_role or has_required_permission and skip_self_checks:
            return True
        if has_mod_role or has_required_permission:
            # Check if target user is above user in role hierarchy
            if interaction.user.top_role <= target.top_role:
                await interaction.response.send_message(f"Nope, you can't {interaction.command.name} someone higher than yourself.")
                return False
            return True
        await interaction.response.send_message("Not a mod sadchamp")
        return False


def can_handle(interaction: discord.Interaction, permission: str) -> bool:
    """Checks if bot has permissions or is in DMs right now"""
    return isinstance(interaction.channel, discord.DMChannel) or \
        getattr(interaction.channel.permissions_for(interaction.guild.me), permission)