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
            self.updates_check.start()
        except:
            log.critical(f'An error ocurred starting one or more tasks. Traceback:\n{traceback.format_exc()}')

    ###
    ## Updates Channel Stuff
    ###

    @tasks.loop(minutes=4)
    async def updates_check(self):

        log.debug('Executing "tasks.updates_check" task')

        try: # New cosmetics

            for lang in util.configuration['languages']:

                cached_cosmetics = json.load(open(f'cache/cosmetics/all_{lang}.json', 'r', encoding='utf-8'))
                new_cosmetics = await util.fortniteapi[lang]._load_cosmetics(language = lang)

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

                    log.debug(f'Sent {len(embeds)} embeds to {len(list(util.database.guilds.find({"updates_channel.enabled": True})))} guilds in {int((time.time() - start_timestamp))} seconds! - Status: {result}')
                
                else:

                    log.debug('No cosmetic changes detected.')

        except Exception:
            log.error(f'Failed while checking upcoming cosmetics changes. Traceback:\n{traceback.format_exc()}')


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
            rate_limit_retry=True
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