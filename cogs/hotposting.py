import discord
import praw
import random
import asyncio

from discord.ext.commands.context import Context
from discord.ext.commands._types import BotT
from discord.ext import commands
from utils import permissions, http, default


with open('secrets.txt', 'r') as f:
    secrets = f.read().splitlines()
    client_id = secrets[0]
    client_secret = secrets[1]
    user_agent = secrets[2]

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

sent_posts = []
class hotposting (commands.Cog):
        def __init__(self, bot):
            self.bot: commands.AutoShardedBot = bot
            self.config = default.load_json()

        @commands.command(help='Displays a random hot post from the "bois" subreddit.', usage='<@1097951798540652564> femboy')
        async def bois(self, ctx: Context[BotT]):
            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("This command does not work in DMs. Please use it in an NSFW channel.")
                return
            if not ctx.channel.is_nsfw():
                await ctx.send("Please run this command in a channel marked as NSFW.")
                return            

            hot_posts = list(reddit.subreddit('bois').hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.url)
            embed.set_image(url=post.url)
            await ctx.send(embed=embed)

        @commands.command(help='Displays a random hot post from the specified subreddit.', usage='<@1097951798540652564> hot [subreddit]')
        async def hot(self, ctx: Context[BotT], subreddit: str):
            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("This command does not work in DMs. Please use it in an NSFW channel.")
                return
            if not ctx.channel.is_nsfw():
                await ctx.send("Please run this command in a channel marked as NSFW.")
                return
            hot_posts = list(reddit.subreddit(subreddit).hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.url)
            embed.set_image(url=post.url)

async def setup(bot):
    await bot.add_cog(hotposting(bot))
