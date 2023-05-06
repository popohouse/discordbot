import discord
from discord.ext import commands
import aiohttp
import re

class AniList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if self.bot.user.mentioned_in(message):
            return
        if any(re.match(r'<.*:[^:]+:\d+>', e) for e in message.content.split()) or '@' in message.content:
            return

        

        content = message.content.strip()
        if not (content.startswith('{') and content.endswith('}')) and not (content.startswith('<') and content.endswith('>')):
            return
        
        if content.startswith('<#'):
            return
        
        media_type = 'ANIME' if content.startswith('{') else 'MANGA'
        start_index = 1
        end_index = len(content) - 1

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
            'search': content[start_index:end_index],
            'type': media_type
        }

        url = 'https://graphql.anilist.co'
        async with self.session.post(url, json={'query': query, 'variables': variables}) as response:
            json_data = await response.json()
            data = json_data['data']['Media']
            
            if not data:
                return await message.channel.send("This title doesn't exist.")
            
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
            
            #Don't allow hentai in sfw channels
            if 'Hentai' in data['genres'] and not message.channel.is_nsfw():
                await message.channel.send('Please check this series in a NSFW channel.')
                return
                    

            image_url = 'https://img.anili.st/media/' + str(data['id'])
            status = data['status']
            
            start_date = f"{data['startDate']['month']}/{data['startDate']['day']}/{data['startDate']['year']}"
            
            if data['endDate']:
                end_date = f"{data['endDate']['month']}/{data['endDate']['day']}/{data['endDate']['year']}"
                footer_text = f"{media_type.capitalize()} • {status} • {start_date} - {end_date}"
            else:
                footer_text = f"{media_type.capitalize()} • {status} • {start_date}"
                
            
            embed = discord.Embed(description=f"[{title}]({url})", color=5814783)
            
            embed.add_field(name=genres, value=description)
            
            embed.set_footer(text=footer_text)
            

            embed.set_image(url=image_url)


            await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AniList(bot))