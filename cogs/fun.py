import random
import discord
from discord import app_commands
from discord.ext import commands
import secrets
import aiohttp
import mimetypes
import io

from io import BytesIO
from utils import permissions, http



class Fun_Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def rate(self, interaction: discord.Interaction, *, thing: str):
        """Rates what you desire"""
        rate_amount = random.uniform(0.0, 100.0)
        await interaction.response.send_message(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")


    @app_commands.command()
    async def f(self, interaction: discord.Interaction, *, text: str):
        """Press F to pay respect"""
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""
        await interaction.response.send_message(f"**{interaction.user.name}** has paid their respect {reason}{random.choice(hearts)}")


    @app_commands.command()
    async def eightball(self, interaction: discord.Interaction, *, question: str):
        """Consult 8ball to receive an answer"""
        ballresponse = [
            "Yes", "No", "Take a wild guess...", "Very doubtful",
            "Sure", "Without a doubt", "Most likely", "Might be possible",
            "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",
            "senpai, pls no ;-;"
        ]

        answer = random.choice(ballresponse)
        await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    @app_commands.command()
    async def catmeme(self, interaction: discord.Interaction) -> None:
        """Return cat meme"""
        async with aiohttp.ClientSession() as session, session.get('https://api.popo.house/catmeme') as response:
            image_data = await response.read()
            content_type = response.headers['Content-Type']
            extension = mimetypes.guess_extension(content_type)
            image_file = discord.File(io.BytesIO(image_data), filename=f"catmeme{extension}")
            await interaction.response.send_message(file=image_file)

    @app_commands.command()
    async def coffee(self, interaction: discord.Interaction) -> None:
        """Return coffee releated image"""
        async with aiohttp.ClientSession() as session, session.get('https://api.popo.house/coffee') as response:
            image_data = await response.read()
            content_type = response.headers['Content-Type']
            extension = mimetypes.guess_extension(content_type)
            image_file = discord.File(io.BytesIO(image_data), filename=f"coffee{extension}")
            await interaction.response.send_message(file=image_file)

    @app_commands.command()
    async def urban(self, interaction: discord.Interaction, *, search: str):
        """Find the 'best' definition to your words"""
        async with interaction.channel.typing():
            try:
                r = await http.get(f"https://api.urbandictionary.com/v0/define?term={search}", res_method="json")
            except Exception:
                return await interaction.response.send_message("Urban API returned invalid data... might be down atm.")

            if not r.response:
                return await interaction.response.send_message("I think the API broke...")

            result = sorted(r.response["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            await interaction.response.send_message(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")

    @app_commands.command()
    async def coinflip(self, interaction: discord.Interaction):
        """Coinflip!"""
        coinsides = ["Heads", "Tails"]
        await interaction.response.send_message(f"**{interaction.user.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @app_commands.command()
    async def reverse(self, interaction: discord.Interaction, *, text: str):
        """Everything you type after reverse will of course, be reversed"""
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await interaction.response.send_message(
            f"🔁 {t_rev}",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @app_commands.command()
    async def password(self, interaction: discord.Interaction, nbytes: int = 18):
        """Generates a random password string for you"""
        if nbytes not in range(3, 1401):
            return await interaction.response.send_message("I only accept any numbers between 3-1400")
        await interaction.response.send_message(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}", ephemeral=True)

    @app_commands.command()
    async def hotcalc(self, interaction: discord.Interaction, *, user: discord.Member = None):
        """Returns a random percent for how hot is a discord user"""
        user = user or interaction.user
        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        match hot:
            case x if x > 75:
                emoji = "💞"
            case x if x > 50:
                emoji = "💖"
            case x if x > 25:
                emoji = "❤"
            case _:
                emoji = "💔"

        await interaction.response.send_message(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @app_commands.command()
    async def noticeme(self, interaction: discord.Interaction):
        """Notice me senpai! owo"""
        if not permissions.can_handle(interaction, "attach_files"):
            return await interaction.response.send_message("I cannot send images here ;-;")

        r = await http.get("https://i.alexflipnote.dev/500ce4.gif", res_method="read")
        bio = BytesIO(r.response)
        await interaction.response.send_message(file=discord.File(bio, filename="noticeme.gif"))

    @app_commands.command()
    async def dice(self, interaction: discord.Interaction):
        """Dice game. Good luck"""
        bot_dice, player_dice = [random.randint(1, 6) for g in range(2)]

        results = "\n".join([
            f"**{self.bot.user.display_name}:** 🎲 {bot_dice}",
            f"**{interaction.user.display_name}** 🎲 {player_dice}"
        ])

        match player_dice:
            case x if x > bot_dice:
                final_message = "Congrats, you won 🎉"
            case x if x < bot_dice:
                final_message = "You lost, try again... 🍃"
            case _:
                final_message = "It's a tie 🎲"

        await interaction.response.send_message(f"{results}\n> {final_message}")
        
    @app_commands.command()
    async def inspired(self, interaction: discord.Interaction):
        """Be inspired"""
        async with aiohttp.ClientSession() as session, session.get('https://inspirobot.me/api?generate=true') as response:
            link = await response.text()
            await interaction.response.send_message(link)



async def setup(bot):
    await bot.add_cog(Fun_Commands(bot))