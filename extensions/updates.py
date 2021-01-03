from discord.ext import commands, tasks
import main
import funcs
import discord
import json
import requests
import sys

class Updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.updates_cosmetics.start()
        self.updates_playlists.start()
        self.updates_aes.start()
        self.updates_news.start()
        self.updates_blogposts_c.start()
        self.updates_blogposts_n.start()


    async def send_update_message(self, type:str ,embed=None, content=None, file=None):
        
        servers = main.db.guilds

        channels = []

        for guild in self.bot.guilds:

            server = servers.find_one({"server_id": guild.id})

            if server['updates_channel'] != 1:

                if server['updates_config'][type] == True:
                    c = self.bot.get_channel(int(server['updates_channel']))

                    if c != None:
                        channels.append(c)
        for chan in channels:
            try:
                await chan.send(embed=embed, content=content, file=file)
            except Exception as e:
                funcs.log(f'Failed to send update message to channel {chan.id}: {e}')


    @tasks.loop(seconds=75)
    async def updates_cosmetics(self):

        await self.bot.wait_until_ready()

        response = requests.get('https://fortnite-api.com/v2/cosmetics/br/new')

        if response.status_code != 200:
            funcs.logdebug(f'[Updates][updates_cosmetics] Received status {response.status_code}')
            return

        with open('cached/cosmetics.json', 'r', encoding='utf-8') as f:
            cached = json.load(f)

        if cached != response.json():

            for cosmetic in response.json()['data']['items']:
                if cosmetic not in cached['data']['items']:

                    try:

                        embed = discord.Embed(
                            title = f'New {cosmetic["type"]["value"]}',
                            description = f'**{cosmetic["name"]}**\n_{cosmetic["description"]}_\n\n**ID**\n`{cosmetic["id"]}`\n**Rarity**\n`{cosmetic["rarity"]["displayValue"]}`\n**Set**\n`{cosmetic["set"]["text"] if cosmetic["set"] else ""}`',
                            color = funcs.rarity_color(cosmetic['rarity']['value'])
                        )
                        if cosmetic['images']['icon']:
                            embed.set_thumbnail(url=cosmetic['images']['icon'])

                        if cosmetic['images']['featured']:
                            embed.set_image(url=cosmetic['images']['featured'])

                        await self.send_update_message(type='cosmetics', embed=embed)

                    except Exception as e:
                        funcs.log(f'Failed to send a new cosmetic to updates channel: {e}')

            with open('cached/cosmetics.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=4, ensure_ascii=False)


    @tasks.loop(seconds=60)
    async def updates_playlists(self):

        await self.bot.wait_until_ready()

        response = requests.get('https://fortnite-api.com/v1/playlists')

        if response.status_code != 200:
            funcs.logdebug(f'[Updates][updates_playlists] Received status {response.status_code}')
            return

        with open('cached/playlists.json', 'r', encoding='utf-8') as f:
            cached = json.load(f)

        if cached != response.json():

            for playlist in response.json()['data']:
                if playlist not in cached['data']:

                    try:

                        embed = discord.Embed(
                            title = 'New playlist',
                            description = f'**{playlist["name"]}**\n\n_{playlist["description"]}_\n**ID**\n`{playlist["id"]}`',
                            color = discord.Colour.blue()
                        )
                        if playlist['images']['showcase']:
                            embed.set_image(url=playlist['images']['showcase'])
                        else:
                            embed.set_footer(text='No image found')
                        if playlist['images']['missionIcon']:
                            embed.set_thumbnail(url=playlist['images']['missionIcon'])

                        await self.send_update_message(type='playlists', embed=embed)

                    except Exception as e:
                        funcs.logdebug(f'Failed to send a new playlist to updates channel: {e}')

            with open('cached/playlists.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=4, ensure_ascii=False)


    @tasks.loop(seconds=60)
    async def updates_aes(self):

        await self.bot.wait_until_ready()

        response = requests.get('https://fortnite-api.com/v2/aes')

        if response.status_code != 200:
            funcs.logdebug(f'[Updates][updates_aes] Received status {response.status_code}')
            return

        with open('cached/aes.json', 'r', encoding='utf-8') as f:
            cached = json.load(f)

        if cached != response.json():

            if response.json()['data']['mainKey'] != cached['data']['mainKey']:

                embed = discord.Embed(
                    title = 'Main key changed',
                    description = f'**Old**\n~~`{cached["data"]["mainKey"]}`~~\n**New**\n`{response.json()["data"]["mainKey"]}`',
                    color = discord.Colour.blue()
                )
                
                await self.send_update_message(type='aes', embed=embed)


            for pak in response.json()['data']['dynamicKeys']:
                if pak not in cached['data']['dynamicKeys']:

                    try:

                        embed = discord.Embed(
                            title = 'New pak got decrypted',
                            description = f'**{pak["pakFilename"]}**\n**pakGuid**\n`{pak["pakGuid"]}`\n**key**\n`{pak["key"]}`',
                            color = discord.Colour.blue()
                        )

                        await self.send_update_message(type='aes', embed=embed)

                    except Exception as e:
                        funcs.logdebug(f'Failed to send a new aes key to updates channel: {e}')

            with open('cached/aes.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=4, ensure_ascii=False)


    @tasks.loop(seconds=35)
    async def updates_news(self):

        await self.bot.wait_until_ready()

        response = requests.get('https://fortnite-api.com/v2/news')

        if response.status_code != 200:
            funcs.logdebug(f'[Updates][updates_news] Received status {response.status_code}')
            return

        with open('cached/news.json', 'r', encoding='utf-8') as f:
            cached = json.load(f)

        if cached != response.json():

            if response.json()['data']['br']['image'] != cached['data']['br']['image']:

                embed = discord.Embed(
                    title = 'Battle Royale News Updated',
                    color = discord.Colour.blue()
                )
                embed.set_image(url=response.json()['data']['br']['image'])

                await self.send_update_message('news', embed=embed)

            if response.json()['data']['creative']['image'] != cached['data']['creative']['image']:

                embed = discord.Embed(
                    title = 'Creative News Updated',
                    color = discord.Colour.blue()
                )
                embed.set_image(url=response.json()['data']['creative']['image'])

                await self.send_update_message('news', embed=embed)

            if response.json()['data']['stw']['image'] != cached['data']['stw']['image']:

                embed = discord.Embed(
                    title = 'Save the World News Updated',
                    color = discord.Colour.blue()
                )
                embed.set_image(url=response.json()['data']['stw']['image'])

                await self.send_update_message('news', embed=embed)


            with open('cached/news.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=4, ensure_ascii=False)


    @tasks.loop(seconds=60)
    async def updates_blogposts_n(self):

        await self.bot.wait_until_ready()

        responseN = requests.get('https://api.peely.de/v1/blogposts/normal')

        if responseN.status_code != 200:
            funcs.logdebug(f'[Updates][updates_blogposts normal] Received status {responseN.status_code}')
            return

        with open('cached/blogposts_n.json', 'r', encoding='utf-8') as f:
            cachedN = json.load(f)

        if cachedN != responseN.json():

            for blogpost in responseN.json()['data']['blogposts']:
                if blogpost not in cachedN['data']['blogposts']:

                    try:
                        desc = f'_{blogpost["description"]}_'
                    except:
                        desc = ''
                    try:
                        url = f'[Link]({blogpost["url"]})'
                    except:
                        url = ''

                    embed = discord.Embed(
                        title = 'New blogpost',
                        description = f'**{blogpost["title"]}**\n{desc}\n\n{url}',
                        color = 0x570ae4
                    )
                    try:
                        embed.set_footer(text=blogpost['author'])
                    except:
                        pass
                    try:
                        embed.set_image(url=blogpost['image'])
                    except:
                        pass

                    await self.send_update_message(type='blogposts', embed=embed)
            
            with open('cached/blogposts_n.json', 'w', encoding='utf-8') as f:
                json.dump(responseN.json(), f, indent=4, ensure_ascii=False)


    @tasks.loop(seconds=60)
    async def updates_blogposts_c(self):

        responseC = requests.get('https://api.peely.de/v1/blogposts/competitive')

        if responseC.status_code != 200:
            funcs.logdebug(f'[Updates][updates_blogposts competitive] Received status {responseC.status_code}')
            return

        with open('cached/blogposts_c.json', 'r', encoding='utf-8') as f:
            cachedC = json.load(f)

        if cachedC != responseC.json():

            for blogpost in responseC.json()['data']['blogposts']:
                if blogpost not in cachedC['data']['blogposts']:

                    try:
                        desc = f'_{blogpost["description"]}_'
                    except:
                        desc = ''
                    try:
                        url = f'[Link]({blogpost["url"]})'
                    except:
                        url = ''

                    embed = discord.Embed(
                        title = 'New competitive blogpost',
                        description = f'**{blogpost["title"]}**\n{desc}\n\n{url}',
                        color = 0x570ae4
                    )
                    try:
                        embed.set_footer(text=blogpost['author'])
                    except:
                        pass
                    try:
                        embed.set_image(url=blogpost['image'])
                    except:
                        pass

                    await self.send_update_message(type='blogposts', embed=embed)
            
            with open('cached/blogposts_c.json', 'w', encoding='utf-8') as f:
                json.dump(responseC.json(), f, indent=4, ensure_ascii=False)


def setup(bot):
    bot.add_cog(Updates(bot))