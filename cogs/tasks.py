from discord.ext import commands, tasks
import traceback
import requests
import discord
import logging

import util

log = logging.getLogger('FortniteData.cogs.tasks')

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        log.debug('Starting tasks...')
        try:
            self.cosmetics_cache_refresh.start()
            self.updates_check.start()
        except:
            log.critical(f'An error ocurred starting one or more tasks. Traceback:\n{traceback.format_exc()}')

    @tasks.loop(minutes=20)
    async def cosmetics_cache_refresh(self):

        log.debug('Executing "tasks.cosmetics_cache_refresh" task')

        if util.fortniteapi == None:
            util.fortniteapi = util.FortniteAPI()

        try:
            await util.fortniteapi._load_cosmetics()
            return
        except Exception:
            log.error(f'Failed while updating cosmetics. Traceback:\n{traceback.format_exc()}')

    ###
    ## Updates Channel Stuff
    ###

    @tasks.loop(minutes=5)
    async def updates_check(self):

        log.debug('Executing "tasks.updates_check" task')

        try: # New cosmetics

            new_cosmetics = []

            current_data = util.fortniteapi.new_cosmetics
            new_data = await util.fortniteapi.get_new_items()

            for cosmetic in new_data:
                if cosmetic not in current_data:

                    new_cosmetics.append(cosmetic)

            log.debug(f'Detected {len(new_cosmetics)} new cosmetics.')

            if len(new_cosmetics) > 0:

                embeds = []

                count = 0
                for i in new_cosmetics:

                    embed = discord.Embed(
                        title = 'New cosmetics detected!' if count == 0 else None,
                        color = util.get_color_by_rarity(i['rarity']['value'])
                    )

                    embed.add_field(name='ID', value=f'`{i["id"]}`', inline=False)
                    embed.add_field(name='Rarity', value=f'`{i["rarity"]["displayValue"]}`', inline=False)
                    embed.add_field(name='Introduction', value=f'`{i["introduction"]["text"]}`' if i['introduction'] else 'Not introduced yet', inline=False)
                    embed.add_field(name='Set', value=f'`{i["set"]["text"]}`' if i['set'] else 'None', inline=False)

                    embed.set_thumbnail(url=i['images']['icon'])

                    if count+1 == len(new_cosmetics):
                        embed.set_footer(text=f'{len(new_cosmetics)} new cosmetics • Provided by Fortnite-API.com')

                    embeds.append(embed)

                await self.updates_channel_send(embeds=embeds, type_='cosmetics')

        except Exception:
            log.error(f'Failed while checking upcoming cosmetics changes. Traceback:\n{traceback.format_exc()}')


    async def updates_channel_send(self, embeds, type_):
        
        servers = util.database.guilds.find({'updates_channel.enabled': True})
        
        queue = await self._create_queue(embeds)

        for i in servers:

            if i['updates_channel']['config'][type_] == False:
                continue

            try:
                guild = self.bot.get_guild(i['server_id'])

                if guild != None:

                    for embeds in queue:
                        await self._updates_send(url=i['updates_channel']['webhook'], embeds=embeds)

            except Exception:
                log.error(f'Failed while trying to send updates message to guild {i["server_id"]}. Traceback:\n{traceback.format_exc()}')


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
    
    async def _updates_send(self, url, embeds): # POST to Discord

        try:

            data = {
                "embeds": embeds
            }
            post = requests.post(url, data=data)

            if post.status_code == 200:
                return True
            else:
                return post

        except Exception:
            log.error(f'Failed post to webhook {url}. Traceback:\n{traceback.format_exc()}')


def setup(bot):
    bot.add_cog(Tasks(bot))