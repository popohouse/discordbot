import discord
import praw
import random


from discord.ext.commands.context import Context
from discord.ext import commands
from utils import default


with open('data/secrets.txt', 'r') as f:
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

        @commands.command(help='Displays a random hot post from the "bois" subreddit.', usage='!bois')
        async def bois(self, ctx: Context):
            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("This command does not work in DMs. Please use it in an NSFW channel.")
                return
            if not ctx.channel.is_nsfw():
                await ctx.send("Please run this command in a channel marked as NSFW.")
                return            

            hot_posts = list(reddit.subreddit('bois').hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif', '.mp4'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            await ctx.send(embed=embed)

        @commands.command(help='Displays a random hot post from one of the subreddits: ThighCrushing, ThickThighs, thighdeology, Thigh_Brows, thighhighs, Thighs.', usage='!bois')
        async def thigh(self, ctx: Context):
            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("This command does not work in DMs. Please use it in an NSFW channel.")
                return
            if not ctx.channel.is_nsfw():
                await ctx.send("Please run this command in a channel marked as NSFW.")
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
            await ctx.send(embed=embed)



        @commands.command(help='Displays a random hot post from the "femboys" subreddit.', usage='!femboy')
        async def femboys(self, ctx: Context):
            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("This command does not work in DMs. Please use it in an NSFW channel.")
                return
            if not ctx.channel.is_nsfw():
                await ctx.send("Please run this command in a channel marked as NSFW.")
                return            

            hot_posts = list(reddit.subreddit('femboys').hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif', '.mp4'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            await ctx.send(embed=embed)

        @commands.command(help='Displays a random hot post from the specified subreddit.', usage='!hot [subreddit]')
        async def hot(self, ctx: Context, subreddit: str):
            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("This command does not work in DMs. Please use it in an NSFW channel.")
                return
            if not ctx.channel.is_nsfw():
                await ctx.send("Please run this command in a channel marked as NSFW.")
                return
            hot_posts = list(reddit.subreddit(subreddit).hot(limit=100))
            image_posts = [post for post in hot_posts if post.is_self == False and post.url.endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif', '.mp4'))]
            post = random.choice(image_posts)
            while post in sent_posts:
                post = random.choice(image_posts)
            sent_posts.append(post)
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            await ctx.send(embed=embed)


            
async def setup(bot):
    await bot.add_cog(hotposting(bot))
