from discord.ext import commands
import aiohttp
import re
import discord
from discord import app_commands

class AniList(commands.Cog):
    def __init__(self, bot)-> None:
        self.bot = bot
    async def cog_unload(self):
        self.bot.loop.create_task(self.session.close())    

    async def search(self, interaction, media_type: str, search: str):
        self.session = aiohttp.ClientSession()
        query = '''
        query ($search: String, $type: MediaType) {
          Media (search: $search, type: $type) {
            id
            meanScore
            title {
              romaji
              english
              native
            }
            coverImage {
              large
            }
            bannerImage
            startDate {
              year
              month
              day
            }
            endDate {
              year
              month
              day
            }
            status
            genres
            description(asHtml: false)
            siteUrl
          }
        }
        '''

        variables = {
            'search': search,
            'type': media_type.upper()
        }

        url = 'https://graphql.anilist.co'
        async with self.session.post(url, json={'query': query, 'variables': variables}) as response:
            json_data = await response.json()
            data = json_data['data']['Media']
            
            if not data:
                return await interaction.response.send_message("This title doesn't exist.")
            
            romaji_title = data['title'].get('romaji', '')
            english_title = data['title'].get('english', '')
            native_title = data['title'].get('native', '')
            title = english_title or romaji_title or native_title

            url = data['siteUrl']
            
            if data['description'] is not None:
                description = re.sub('<[^<]+?>', '', data['description'])
            else:
                description = ""
                
            if len(description) >= 400:
                description = description[:350] + f'... [(more)]({url})'
            
            genres = ', '.join(data['genres'])
            if "hentai" in genres.lower() and interaction.channel.nsfw is False:
                return await interaction.response.send_message("Please run this in the nsfw channel.", ephemeral=True)        
                    
            image_url = 'https://img.anili.st/media/' + str(data['id'])
            status = data['status']
            
            start_date = ''
            if data['startDate']['year'] and data['startDate']['month'] and data['startDate']['day']:
                start_date = f"{data['startDate']['month']}/{data['startDate']['day']}/{data['startDate']['year']}"

            end_date = ''
            if data['endDate'] and data['endDate']['year'] and data['endDate']['month'] and data['endDate']['day']:
                end_date = f"{data['endDate']['month']}/{data['endDate']['day']}/{data['endDate']['year']}"

            if end_date and status not in ['RELEASING', 'NOT_YET_RELEASED']:
                footer_text = f"{media_type.capitalize()} • {status} • {start_date} - {end_date}"
            else:
                footer_text = f"{media_type.capitalize()} • {status} • {start_date}"
            
            embed = discord.Embed(description=f"[{title}]({url})", color=5814783)
            
            embed.add_field(name=genres, value=description)
            
            embed.set_footer(text=footer_text)
            

            embed.set_image(url=image_url)


            await interaction.response.send_message(embed=embed)
            await self.session.close()

    @app_commands.command(name="anime", description="Search for an anime on AniList")
    @commands.guild_only()
    async def anime(self, interaction: discord.Interaction, search: str)-> None:
        await self.search(interaction, "anime", search)

    @app_commands.command(name="manga", description="Search for a manga on AniList")
    @commands.guild_only()
    async def manga(self, interaction: discord.Interaction, search: str)-> None:
        await self.search(interaction, "manga", search)

async def setup(bot):
    await bot.add_cog(AniList(bot))