import discord

from io import BytesIO
from utils import default
from utils.default import CustomContext
from discord.ext import commands
from utils.data import DiscordBot


class Discord_Info(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.command(aliases=["av", "pfp"])
    @commands.guild_only()
    async def avatar(self, ctx: CustomContext, *, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        user = user or ctx.author

        avatars_list = []

        def target_avatar_formats(target):
            formats = ["JPEG", "PNG", "WebP"]
            if target.is_animated():
                formats.append("GIF")
            return formats

        if not user.avatar and not user.guild_avatar:
            return await ctx.send(f"**{user}** has no avatar set, at all...")

        if user.avatar:
            avatars_list.append("**Account avatar:** " + " **-** ".join(
                f"[{img_format}]({user.avatar.replace(format=img_format.lower(), size=1024)})"
                for img_format in target_avatar_formats(user.avatar)
            ))

        embed = discord.Embed(colour=user.top_role.colour.value)

        if user.guild_avatar:
            avatars_list.append("**Server avatar:** " + " **-** ".join(
                f"[{img_format}]({user.guild_avatar.replace(format=img_format.lower(), size=1024)})"
                for img_format in target_avatar_formats(user.guild_avatar)
            ))
            embed.set_thumbnail(url=user.avatar.replace(format="png"))

        embed.set_image(url=f"{user.display_avatar.with_size(256).with_static_format('png')}")
        embed.description = "\n".join(avatars_list)

        await ctx.send(f"🖼 Avatar to **{user}**", embed=embed)

    @commands.command()
    @commands.guild_only()
    async def mods(self, ctx: CustomContext):
        """ Check which mods are online on current guild """
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"

        await ctx.send(f"Mods in **{ctx.guild.name}**\n{message}")

async def setup(bot):
    await bot.add_cog(Discord_Info(bot))