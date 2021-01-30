from discord.ext import commands, tasks
import requests
import traceback
import io
import asyncio
import discord
import requests
import random
import funcs
import json
import main
import time


def text_guild(guild, value: str):
    server = main.db.guilds.find_one({"server_id": guild.id})
    lang = 'es' if server['lang'] == 'es' else 'en' if server['lang'] == 'en' else 'ja' if server['lang'] == 'ja' else 'en'

    try:
        with open(f'langs/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)[str(value)]
    except:
        with open(f'langs/{lang}.json', 'r', encoding='utf-8-sig') as f:
            return json.load(f)[str(value)]


async def wait_for_valid_image(headers):

    base_url = 'https://api.nitestats.com/v1/shop/image'

    while True:

        response = requests.get(base_url, params=headers)

        if response.status_code == 200:
            if response.headers["Content-Type"] == 'image/png':
                return response

        await asyncio.sleep(4.3)


class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot):

        self.bot = bot

        self.fnapi_key = None

        self.check_shop.start()
        self.update_dbpy_stats.start()
        self.status_changes.start()
        self.update_topgg_stats.start()


    def cog_unload(self):
        
        self.check_shop.stop()
        self.update_dbpy_stats.stop()
        self.status_changes.stop()
        self.update_topgg_stats.stop()


    def fnapi_request(self, url):

        if self.fnapi_key == None:
            with open('values.json', 'r', encoding='utf-8') as f:
                self.fnapi_key = json.load(f)["fnapi_key"]

        headers = {
            "x-api-key": self.fnapi_key
        }
        response = requests.get(url, headers=headers)

        return response

    @tasks.loop(seconds=15)
    async def check_shop(self):

        await self.bot.wait_until_ready()

        with open('cached/shop.txt', 'r', encoding='utf-8') as c:
            cached = c.read()
        response = requests.get('https://api.nitestats.com/v1/shop/shophash')

        if response.status_code == 200:

            if cached != response.text:

                with open('cached/shop.txt', 'w', encoding='utf-8') as f:
                    f.write(response.text)

                main.log.info(f'New shop detected. {response.text}')
                funcs.log('New shop detected <:FNWarn:762553132898058282>')

                servers = main.db.guilds
                start_time = time.time()
                count = 0

                for guild in self.bot.guilds:

                    server = servers.find_one({"server_id": guild.id})

                    if server['shop_channel'] == 1:
                        continue

                    await self.bot.wait_until_ready()
                    channel = self.bot.get_channel(int(server['shop_channel']))

                    if channel == None:
                        continue

                    embed = discord.Embed(color=0x570ae4)
                    embed.set_author(
                        name=text_guild(guild, 'new_fortnite_shop'),
                        url='https://discord.com/oauth2/authorize?client_id=729409703360069722&permissions=379968&scope=bot',
                        icon_url=f'https://cdn.discordapp.com/emojis/763528352828227584.png'
                    )
                    embed.set_image(url='attachment://shop.png')

                    shopimage = await wait_for_valid_image(funcs.compose_shop_headers(guild))

                    file = discord.File(
                        fp = io.BytesIO(shopimage.content),
                        filename = 'shop.png',
                        spoiler = False
                    )

                    try:
                        await self.bot.wait_until_ready()
                        await channel.send(embed=embed, file=file)
                        main.log.debug(f'Sended shop successfully: {channel.id}')
                        count += 1
                    except Exception as error:
                        main.log.error(f'Could not send shop. Channel: "{channel.id}" GuildID: "{channel.guild.id}". Error: {error}')
                        funcs.log(f'Error while trying to send shop to channel {channel.id}:\n```\b{"".join(traceback.format_exception(None, error, error.__traceback__))}```')

                main.log.info(f'Sended shop in `{round(time.time() - start_time, 3)}` seconds to `{count}` channels')
                funcs.log(f'Sended shop in `{round(time.time() - start_time, 3)}` seconds to `{count}` channels')



    @tasks.loop(seconds=300)
    async def status_changes(self):

        await self.bot.wait_until_ready()

        try:
            statuses = [
                f'{len(self.bot.guilds)} servers',
                f'{requests.get("https://api.peely.de/v1/br/progress/data").json()["data"]["DaysLeft"]} days to end season',
                f'{len(requests.get("https://fortnite-api.com/v2/cosmetics/br").json()["data"])} cosmetics ingame',
                f'{requests.get("https://fortnite-api.com/v2/cosmetics/br/new").json()["data"]["items"]} unreleased cosmetics',
                'f!invite',
                'docs.fortnitedata.tk'
            ]
            selected = random.choice(statuses)
            
            await self.bot.change_presence(activity=discord.Game(name=selected))
            main.log.debug(f'Status updated: "{selected}"')
        except:
            pass


    @tasks.loop(minutes=30)
    async def update_dbpy_stats(self):

        await self.bot.wait_until_ready()

        with open('values.json', 'r', encoding='utf-8') as f:
            values = json.load(f)

        headers = {'Authorization': f'{values["dbpy_token"]}'}
        params = {'server_count': f'{len(self.bot.guilds)}'}

        if self.bot.user.id == 729409703360069722:

            try:
                requests.post(f'https://discord.boats/api/v2/bot/729409703360069722', headers=headers, json=params)
                main.log.debug('Posted stats to discord.boats.')
            except Exception as e:
                main.log.error(f'Failed to post stats to discord.boats: {e}')


    @tasks.loop(minutes=30)
    async def update_topgg_stats(self):

        await self.bot.wait_until_ready()

        with open('values.json', 'r', encoding='utf-8') as f:
            values = json.load(f)

        headers = {
            "Authorization": values['topgg_token']
            }
        params = {
            "server_count": f"{len(self.bot.guilds)}"
            }

        if self.bot.user.id == 729409703360069722:

            try:
                requests.post(f'https://top.gg/api/bots/729409703360069722/stats', headers=headers, json=params).raise_for_status()
                main.log.debug('Posted stats to top.gg.')
            except Exception as e:
                main.log.error(f'Failed to post stats to top.gg: {e}')


def setup(bot):
    bot.add_cog(Tasks(bot))
