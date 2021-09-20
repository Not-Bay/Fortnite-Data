from discord_webhook import DiscordWebhook, DiscordEmbed
from discord.ext import commands, tasks
import traceback
import aiohttp
import logging
import json
import time

import util

log = logging.getLogger('FortniteData.cogs.tasks')

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ClientSession = aiohttp.ClientSession

        log.debug('Starting tasks...')
        try:
            self.cosmetics_cache_refresh.start()
            self.updates_check.start()
        except:
            log.critical(f'An error ocurred starting one or more tasks. Traceback:\n{traceback.format_exc()}')

    @tasks.loop(minutes=10)
    async def cosmetics_cache_refresh(self):

        log.debug('Executing "tasks.cosmetics_cache_refresh" task')

        if util.fortniteapi == None:
            util.fortniteapi = util.FortniteAPI()

        try:
            await util.fortniteapi._load_cosmetics()

        except Exception:
            log.error(f'Failed while updating cosmetics. Traceback:\n{traceback.format_exc()}')

    ###
    ## Updates Channel Stuff
    ###

    @tasks.loop(minutes=2)
    async def updates_check(self):

        log.debug('Executing "tasks.updates_check" task')

        try: # New cosmetics

            new_raw_cosmetics = await util.fortniteapi.get_new_items()
            cached_raw_cosmetics = json.load(open('cache/new_cosmetics.json', 'r', encoding='utf-8'))

            if new_raw_cosmetics['data']['hash'] != cached_raw_cosmetics['data']['hash']:

                start_timestamp = time.time()

                new_cosmetics = []

                for i in new_raw_cosmetics['data']['items']:
                    if i not in cached_raw_cosmetics['data']['items']:

                        new_cosmetics.append(i)

                if len(new_cosmetics) > 0:

                    embeds = []

                    count = 0
                    for i in new_cosmetics:

                        embed = DiscordEmbed(
                            title = 'New cosmetics detected!' if count == 0 else None,
                            description = f'**{i["name"]}**\n{i["description"]}',
                            color = util.get_color_by_rarity(i['rarity']['value'])
                        )

                        embed.add_embed_field(name='ID', value=f'`{i["id"]}`', inline=False)
                        embed.add_embed_field(name='Type', value=f'`{i["type"]["displayValue"]}`', inline=False)
                        embed.add_embed_field(name='Rarity', value=f'`{i["rarity"]["displayValue"]}`', inline=False)
                        embed.add_embed_field(name='Introduction', value=f'`{i["introduction"]["text"]}`' if i['introduction'] else 'Not introduced yet', inline=False)
                        embed.add_embed_field(name='Set', value=f'`{i["set"]["text"]}`' if i['set'] else 'None', inline=False)

                        embed.set_thumbnail(url=i['images']['icon'])
                        count += 1

                        embed.set_footer(text=f'{count} of {len(new_cosmetics)}')

                        if count == len(new_cosmetics):
                            embed.set_footer(text=f'{count} of {len(new_cosmetics)} • Provided by Fortnite-API.com')
                        

                        embeds.append(embed)

                    await self.updates_channel_send(embeds=embeds, type_='cosmetics')

                    with open('cache/new_cosmetics.json', 'w', encoding='utf-8') as f:
                        json.dump(new_raw_cosmetics, f, indent=4, ensure_ascii=False)

                log.debug(f'Sent {len(embeds)} embeds to {len(list(util.database.guilds.find({"updates_channel.enabled": True})))} guilds in {int((time.time() - start_timestamp))} seconds!')
            
            else:

                log.debug('No cosmetic changes detected.')

        except Exception:
            log.error(f'Failed while checking upcoming cosmetics changes. Traceback:\n{traceback.format_exc()}')


    async def updates_channel_send(self, embeds, type_):
        
        servers = list(util.database.guilds.find({'updates_channel.enabled': True}))

        webhooks = []
        queue = await self._create_queue(embeds)

        for i in servers:

            if i['updates_channel']['config'][type_] == False:
                continue

            guild = self.bot.get_guild(i['server_id'])

            if guild != None:

                webhooks.append(i['updates_channel']['webhook'])

        for embeds in queue:

            webhook = DiscordWebhook(url=webhooks, rate_limit_retry=True)
            for page in embeds:
                webhook.add_embed(page)

            webhook.execute()


    async def _create_queue(self, embeds): # Separate embeds in lists of 10

        queue = []
        subqueue = []

        for embed in embeds:

            if len(subqueue) == 9:

                subqueue.append(embed)
                queue.append(subqueue)
                
                subqueue = []
                continue
            else:
                subqueue.append(embed)
                continue

        return queue


def setup(bot):
    bot.add_cog(Tasks(bot))