import discord
from discord import app_commands
from discord.ext import commands

import praw
import random



from utils.config import Config

config = Config.from_env()

client_id = config.reddit_client_id
client_secret = config.reddit_client_secret
user_agent = config.reddit_user_agent

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

sent_posts = []
class hotposting (commands.Cog):
        def __init__(self, bot):
            self.bot: commands.AutoShardedBot = bot

        @app_commands.command()
        async def bois(self, interaction: discord.Interaction):
            if isinstance(interaction.channel, discord.DMChannel):
                await interaction.response.send_message("This command does not work in DMs. Please use it in an NSFW channel.", ephemeral=True)
                return
            if not interaction.channel.is_nsfw():
                await interaction.response.send_message("Please run this command in a channel marked as NSFW.", ephemeral=True)
                return            

            hot_posts = list(reddit.subreddit('bois').hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif', '.mp4'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            await interaction.response.send_message(embed=embed)

        @app_commands.command()
        async def thigh(self, interaction: discord.Interaction):
            if isinstance(interaction.channel, discord.DMChannel):
                await interaction.response.send_message("This command does not work in DMs. Please use it in an NSFW channel.", ephemeral=True)
                return
            if not interaction.channel.is_nsfw():
                await interaction.response.send_message("Please run this command in a channel marked as NSFW.", ephemeral=True)
                return

            subreddits = ['ThighCrushing', 'ThickThighs', 'thighdeology', 'Thigh_Brows', 'thighhighs', 'Thighs' ]
            subreddit = random.choice(subreddits)
            hot_posts = list(reddit.subreddit(subreddit).hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif', '.mp4'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            await interaction.response.send_message(embed=embed)



        @app_commands.command()
        async def femboys(self, interaction: discord.Interaction):
            if isinstance(interaction.channel, discord.DMChannel):
                await interaction.response.send_message("This command does not work in DMs. Please use it in an NSFW channel.", ephemeral=True)
                return
            if not interaction.channel.is_nsfw():
                await interaction.response.send_message("Please run this command in a channel marked as NSFW.", ephemeral=True)
                return            

            hot_posts = list(reddit.subreddit('femboys').hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif', '.mp4'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            await interaction.response.send_message(embed=embed)

        @app_commands.command()
        async def hot(self, interaction: discord.Interaction, subreddit: str):
            if isinstance(interaction.channel, discord.DMChannel):
                await interaction.response.send_message("This command does not work in DMs. Please use it in an NSFW channel.", ephemeral=True)
                return
            if not interaction.channel.is_nsfw():
                await interaction.response.send_message("Please run this command in a channel marked as NSFW.", ephemeral=True)
                return
            hot_posts = list(reddit.subreddit(subreddit).hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif', '.mp4'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            await interaction.response.send_message(embed=embed)


            
async def setup(bot):
    await bot.add_cog(hotposting(bot))
