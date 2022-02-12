from discord_webhook import DiscordWebhook, DiscordEmbed
from discord.ext import commands, tasks
import traceback
import aiofiles
import aiohttp
import logging
import asyncio
import json
import time
import sys

import util

log = logging.getLogger('FortniteData.cogs.tasks')

class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ClientSession = aiohttp.ClientSession

        self.updates_execution_count = 0
        self.shopcheck_execution_count = 0

        if '--disable-updates-tasks' in sys.argv:
            log.debug('Skipping tasks start. --disable-updates-tasks is in command line arguments.')
            return

        log.debug('Starting tasks...')
        try:
            self.shop_check.start()
            self.updates_check.start()
        except:
            log.critical(f'An error ocurred starting one or more tasks. Traceback:\n{traceback.format_exc()}')

    ###
    ## Updates/Shop Channel Stuff
    ###
    
    @tasks.loop(minutes=3)
    async def shop_check(self):

        self.shopcheck_execution_count += 1

        while True:
            if util.ready == True: # only if bot ready
                break
            else:
                await asyncio.sleep(1)

        log.debug('Executing "tasks.shop_check" task')

        try: # compare shop hash

            log.debug('Comparing shop hash...')

            async with aiofiles.open('cache/shop/shophash.json', 'r', encoding='utf-8') as f:
                cached_shop_hash = json.loads(await f.read())
            
            async with self.ClientSession() as session:
                request = await session.get('https://api.nitestats.com/v1/shop/shophash')
                if request.status != 200:
                    log.error(f'An error ocurred in shop_check task. The shophash online returned status {request.status}')
                else:
                    current_shop_hash = await request.text()

            if current_shop_hash == cached_shop_hash['shophash']: # no changes
                log.debug('Shop hash compared, no changes found.')
                return
            
            else:
                log.info('New shop detected.')

                async with aiofiles.open('cache/shop/shophash.json', 'w', encoding='utf-8') as f:
                    await f.write(json.dumps({"shophash": current_shop_hash}))

                log.debug('Waiting for nitestats for the shop image...')
                while True:

                    async with self.ClientSession() as session:
                        request = await session.get('https://api.nitestats.com/v1/shop/image')

                        if request.status == 200:

                            if request.headers['Content-Type'] == 'image/png':
                                break # image should be ready

                    await asyncio.sleep(5) # image isn't ready, next check will be in 5 seconds

                servers = list(util.database.guilds.find({'shop_channel.enabled': True}))
                await self.shop_channel_send(servers) # this should send the shop to every webhook. SO PLEASE WORK THANK U


        except Exception:
            log.error(f'Failed while checking shop changes. Traceback:\n{traceback.format_exc()}')


    @tasks.loop(minutes=4)
    async def updates_check(self):

        self.updates_execution_count += 1

        while True:
            if util.ready == True: # start checking only if the bot is completely ready
                break
            else:
                await asyncio.sleep(1)

        log.debug('Executing "tasks.updates_check" task')

        try: # New cosmetics

            log.debug('Checking cosmetic updates...')

            for lang in util.configuration['languages']:

                async with aiofiles.open(f'cache/cosmetics/all_{lang}.json', 'r', encoding='utf-8') as f:
                    cached_cosmetics = json.loads(await f.read())
                new_cosmetics = await util.fortniteapi[lang]._load_cosmetics()

                cached_cosmetic_ids = [i['id'] for i in cached_cosmetics['data']] # List of every cosmetic ID

                start_timestamp = time.time()
                new_cosmetics_list = []

                for cosmetic in new_cosmetics:

                    if cosmetic['id'] not in cached_cosmetic_ids:

                        new_cosmetics_list.append(cosmetic)


                if len(new_cosmetics_list) > 0:

                    log.debug(f'Building embeds for {len(new_cosmetics_list)} new cosmetics...')

                    embeds = []

                    count = 0
                    for i in new_cosmetics_list:

                        color = str(util.get_color_by_rarity(i['rarity']['value']))

                        embed = DiscordEmbed()
                        if count == 0:
                            embed.set_author(name=util.get_str(lang, 'update_message_string_new_cosmetics_detected'))

                        embed.title = f'{i["name"]}'

                        embed.description = f'{i["description"]}'

                        embed.color = color.replace('0x', '')

                        embed.add_embed_field(name=util.get_str(lang, 'command_string_id'), value=f'`{i["id"]}`', inline=False)

                        embed.add_embed_field(name=util.get_str(lang, 'command_string_type'), value=f'`{i["type"]["displayValue"]}`', inline=False)

                        embed.add_embed_field(name=util.get_str(lang, 'command_string_rarity'), value=f'`{i["rarity"]["displayValue"]}`', inline=False)

                        if i['introduction'] != None:
                            embed.add_embed_field(name=util.get_str(lang, 'command_string_introduction'), value=f'`{i["introduction"]["text"]}`', inline=False)
                        else:
                            embed.add_embed_field(name=util.get_str(lang, 'command_string_introduction'), value=util.get_str(lang, 'command_string_not_introduced_yet'), inline=False)

                        if i['set'] != None:
                            embed.add_embed_field(name=util.get_str(lang, 'command_string_set'), value=f'`{i["set"]["text"]}`', inline=False)
                        else:
                            embed.add_embed_field(name=util.get_str(lang, 'command_string_set'), value=util.get_str(lang, 'command_string_none'), inline=False)

                        embed.set_thumbnail(url=i['images']['icon'])
                        count += 1

                        if count == len(new_cosmetics):
                            embed.set_footer(text=util.get_str(lang, 'command_string_int_of_int_with_credits').format(count = count, total = len(new_cosmetics_list)))
                        else:
                            embed.set_footer(text=util.get_str(lang, 'command_string_int_of_int').format(count = count, total = len(new_cosmetics_list)))


                        embeds.append(embed)

                    result = await self.updates_channel_send(embeds=embeds, type_='cosmetics', lang=lang)

                    log.debug(f'Sent {len(embeds)} embeds to {len(result)} guilds in {int((time.time() - start_timestamp))} seconds! - Status: {result}')
                
                else:

                    log.debug('No cosmetic changes detected.')
                    if self.updates_execution_count == 1:
                        continue # in order to load cosmetics to every language at startup
                    else:
                        break

        except Exception:
            log.error(f'Failed while checking upcoming cosmetics changes. Traceback:\n{traceback.format_exc()}')

        try: # playlists

            log.debug('Checking playlists updates...')

            for lang in util.configuration['languages']:

                async with aiofiles.open(f'cache/playlists/{lang}.json', 'r', encoding='utf-8') as f:
                    cached_playlists = json.loads(await f.read())

                new_playlists = await util.fortniteapi[lang]._load_playlists()

                added_playlists = []

                if len(cached_playlists['data']) != len(new_playlists):

                    to_send_list = []

                    for playlist in new_playlists['data']:
                        if playlist not in cached_playlists['data']:

                            added_playlists.append(playlist)

                    if len(added_playlists) != 0:

                        count = 0

                        for playlist in added_playlists:

                            embed = DiscordEmbed()
                            if count == 0:
                                embed.set_author(name=util.get_str(lang, 'update_message_string_new_playlists_detected'))

                            embed.title = playlist['name']

                            if playlist['description'] != None:
                                embed.description = playlist['description']
                            
                            else:
                                embed.description = util.get_str(lang, 'update_message_string_playlist_no_description')

                            embed.color = 0x3498db

                            if playlist['images']['showcase'] != None:
                                embed.set_image(url = playlist['images']['showcase'])

                            footer_icon = None
                            if playlist['images']['missionIcon'] != None:
                                footer_icon = playlist['images']['missionIcon']

                            count += 1

                            if count == len(added_playlists):
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int_with_credits').format(count = count, total = len(added_playlists)), icon_url = footer_icon)
                            else:
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int').format(count = count, total = len(added_playlists)), icon_url = footer_icon)
                            
                            to_send_list.append(embed)

                    result = await self.updates_channel_send(embeds=to_send_list, type_='playlists', lang=lang)

                    log.debug(f'Sent {len(to_send_list)} embeds to {len(result)} guilds in {int((time.time() - start_timestamp))} seconds! - Status: {result}')

                else:
                    if self.updates_execution_count == 1:
                        continue # playlists need some love at startup too
                    else:
                        break


        except:
            log.error(f'Failed while checking playlists changes. Traceback:\n{traceback.format_exc()}')

        try: # ingame news

            log.debug('Checking ingame news updates...')

            for lang in util.configuration['languages']:

                async with aiofiles.open(f'cache/news/{lang}.json', 'r', encoding='utf-8') as f:
                    cached_news = json.loads(await f.read())
                new_news = await util.fortniteapi[lang].get_news(language = lang)

                to_send_list = []

                if new_news['data']['br'] != None:

                    br_motds = []

                    if cached_news['data']['br']['hash'] != new_news['data']['br']['hash']:

                        for motd in new_news['data']['br']['motds']:
                            if motd not in cached_news['data']['br']['motds']:
                                br_motds.append(motd)

                        sorted_br_motds = sorted(br_motds, key = lambda x: x['sortingPriority'], reverse = True)
                        count = 0
                        for motd in sorted_br_motds:

                            embed = DiscordEmbed()
                            if count == 0:
                                embed.set_author(name=util.get_str(lang, 'update_message_string_br_news_updated'))

                            embed.title = motd['title']

                            embed.description = motd['body']

                            embed.color = 0x3498db

                            embed.set_image(url = motd['image'])

                            count += 1

                            if count == len(br_motds):
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int_with_credits').format(count = count, total = len(sorted_br_motds)))
                            else:
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int').format(count = count, total = len(sorted_br_motds)))
                            
                            to_send_list.append(embed)
                    
                    else:
                        log.debug(f'[{lang}] No br news changes found')

                if new_news['data']['creative'] != None:

                    cr_motds = []

                    if cached_news['data']['creative']['hash'] != new_news['data']['creative']['hash']:

                        for motd in new_news['data']['creative']['motds']:
                            if motd not in cached_news['data']['creative']['motds']:
                                cr_motds.append(motd)

                        sorted_cr_motds = sorted(cr_motds, key = lambda x: x['sortingPriority'], reverse = True)
                        count = 0
                        for motd in sorted_cr_motds:

                            embed = DiscordEmbed()
                            if count == 0:
                                embed.set_author(name=util.get_str(lang, 'update_message_string_creative_news_updated'))

                            embed.title = motd['title']

                            embed.description = motd['body']

                            embed.color = 0x3498db

                            embed.set_image(url = motd['image'])

                            count += 1

                            if count == len(sorted_cr_motds):
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int_with_credits').format(count = count, total = len(sorted_cr_motds)))
                            else:
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int').format(count = count, total = len(sorted_cr_motds)))
                            
                            to_send_list.append(embed)
                    
                    else:
                        log.debug(f'[{lang}] No creative news changes found')

                if new_news['data']['stw'] != None:

                    stw_motds = []

                    if cached_news['data']['stw']['hash'] != new_news['data']['stw']['hash']:

                        for motd in new_news['data']['stw']['messages']:
                            if motd not in cached_news['data']['stw']['messages']:
                                stw_motds.append(motd)

                        count = 0
                        for motd in stw_motds:

                            embed = DiscordEmbed()
                            if count == 0:
                                embed.set_author(name=util.get_str(lang, 'update_message_string_stw_news_updated'))

                            embed.title = motd['title']

                            embed.description = motd['body']

                            embed.color = 0x3498db

                            embed.set_image(url = motd['image'])

                            count += 1

                            if count == len(stw_motds):
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int_with_credits').format(count = count, total = len(br_motds)))
                            else:
                                embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int').format(count = count, total = len(br_motds)))
                            
                            to_send_list.append(embed)
                    
                    else:
                        log.debug(f'[{lang}] No stw news changes found')

                if len(to_send_list) != 0:

                    async with aiofiles.open(f'cache/news/{lang}.json', 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(new_news))

                    result = await self.updates_channel_send(embeds=to_send_list, type_='news', lang=lang)

                    log.debug(f'Sent {len(to_send_list)} embeds to {len(result)} guilds in {int((time.time() - start_timestamp))} seconds! - Status: {result}')

                else:

                    break

        except:
            log.error(f'Failed while checking ingame news changes. Traceback:\n{traceback.format_exc()}')

        try: # aes (using hex format)

            log.debug('Checking aes updates...')

            thereIsChanges = False

            async with aiofiles.open('cache/aes/hex.json', 'r', encoding='utf-8') as f:
                cached_aes = json.loads(await f.read())
            new_aes = await util.fortniteapi[lang].get_aes()

            for lang in util.configuration['languages']:

                to_send_list = []

                if cached_aes['data']['mainKey'] != new_aes['data']['mainKey']:

                    thereIsChanges = True

                    embed = DiscordEmbed()
                    embed.set_author(name=util.get_str(lang, 'update_message_string_aes_mainkey_changed'))

                    embed_description = ''
                    embed_description += f'{util.get_str(lang, "update_message_string_aes_old")} ~~`{cached_aes["data"]["mainKey"]}`~~\n'
                    embed_description += f'{util.get_str(lang, "update_message_string_aes_new")} `{new_aes["data"]["mainKey"]}`'

                    embed.description = embed_description

                    embed.color = 0x3498db

                    embed.set_footer(text=util.get_str(lang, 'command_string_api_footer_credits'))

                    to_send_list.append(embed)

                if cached_aes['data']['dynamicKeys'] != new_aes['data']['dynamicKeys']:

                    thereIsChanges = True

                    new_keys = []

                    count = 0

                    for key in new_aes['data']['dynamicKeys']:
                        if key not in cached_aes['data']['dynamicKeys']:

                            new_keys.append(key)

                    for key in new_keys:

                        embed = DiscordEmbed()

                        if count == 0:
                            embed.set_author(name=util.get_str(lang, 'update_message_string_aes_dynamickeys_changes_detected'))

                        embed.add_embed_field(
                            name = util.get_str(lang, 'update_message_string_aes_dynamickey_filename'),
                            value = f'`{key["pakFilename"]}`',
                            inline = False
                        )
                        embed.add_embed_field(
                            name = util.get_str(lang, 'update_message_string_aes_dynamickey_guid'),
                            value = f'`{key["pakGuid"]}`',
                            inline = False
                        )
                        embed.add_embed_field(
                            name = util.get_str(lang, 'update_message_string_aes_dynamickey_key'),
                            value = f'`{key["key"]}`',
                            inline = False
                        )

                        embed.color = 0x3498db

                        count += 1

                        if count == len(new_keys):
                            embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int_with_credits').format(count = count, total = len(new_keys)))
                        else:
                            embed.set_footer(text = util.get_str(lang, 'command_string_int_of_int').format(count = count, total = len(new_keys)))

                        to_send_list.append(embed)

                if thereIsChanges == False:
                    break

                else:

                    if lang == util.configuration['languages'][0]: # only update cache once
                        async with aiofiles.open(f'cache/aes/hex.json', 'w', encoding='utf-8') as f:
                            await f.write(json.dumps(new_aes))

                    result = await self.updates_channel_send(embeds=to_send_list, type_='aes', lang=lang)

                    log.debug(f'Sent {len(to_send_list)} embeds to {len(result)} guilds in {int((time.time() - start_timestamp))} seconds! - Status: {result}')

                    continue

        except:
            log.error(f'Failed while checking aes changes. Traceback:\n{traceback.format_exc()}')


    async def shop_channel_send(self, servers):

        status_codes = []

        for server in servers:

            log.debug(f'Preparing shop image for server {server["server_id"]}...')

            lang = server['language']

            embed = DiscordEmbed()
            embed.set_author(name=util.get_str(lang, 'shop_message_string_new_shop_rotation'))
            embed.set_image(url=util.get_custom_shop_url(server))
            embed.color = 0x750de6

            webhook = DiscordWebhook(
                url = server['shop_channel']['webhook'],
                rate_limit_retry=False, # its impossible to get ratelimit using the webhook once per day. Right?
                avatar_url='https://cdn.discordapp.com/avatars/729409703360069722/f1fcb3da5b075da0c6e5283bcb8b3fba.png'
            )

            webhook.add_embed(embed)

            result = webhook.execute(remove_embeds=True)

            log.debug(f'Shop image sent. Status {result}')

            status_codes.append(result)

        log.debug(f'Shop was sent to every server. Status codes: {status_codes}')


    async def updates_channel_send(self, embeds, type_, lang):
        
        servers = list(util.database.guilds.find({'updates_channel.enabled': True, 'language': lang}))

        queues = await self._create_queue(embeds)
        urls = []

        for i in servers:

            if i['updates_channel']['config'][type_] == False:
                continue

            guild = self.bot.get_guild(i['server_id'])

            if guild != None:

                urls.append(i['updates_channel']['webhook'])


        status_codes = []

        webhook = DiscordWebhook(
            url=urls,
            rate_limit_retry=True,
            avatar_url='https://cdn.discordapp.com/avatars/729409703360069722/f1fcb3da5b075da0c6e5283bcb8b3fba.png'
        )

        for i in queues:
            
            for em in i:
                webhook.add_embed(em)

            result = webhook.execute(remove_embeds=True)

            status_codes.append(result)

        return status_codes


    async def _create_queue(self, embeds: list): # Separate embeds in lists of 10

        log.debug('Creating embeds queue...')

        master_list = []
        temp_list = []

        master_append_count = 0

        for embed in embeds:

            if len(temp_list) > 9:

                master_append_count += 1

                master_list.append([i for i in temp_list])
                temp_list.clear()

                temp_list.append(embed)
            
            else:

                temp_list.append(embed)

        if master_append_count == 0:
            master_list.append(temp_list)

        log.debug(f'Created {len(master_list)} embed queues!')

        return master_list


def setup(bot):
    bot.add_cog(Tasks(bot))