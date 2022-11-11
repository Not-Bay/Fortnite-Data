from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands, pages
import aiofiles
import aiohttp
import discord
import logging
import time
import json
import cgi
import io

from modules import util

log = logging.getLogger('FortniteData.cogs.general')

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name=util.get_str('en', 'command_name_item'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_item'),
            'ja': util.get_str('ja', 'command_name_item'),
        },
        description=util.get_str('en', 'command_description_item'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_item'),
            'ja': util.get_str('ja', 'command_description_item')
        }
    )
    @commands.cooldown(5, 8, commands.BucketType.user)
    async def item(
        self,
        ctx: discord.ApplicationContext,
        query: Option(
            str,
            description = 'Name or ID of the cosmetic',
            required = True
        ),
        match_method: Option(
            str,
            description = 'Match method to use',
            required = False,
            default = 'contains',
            choices = [
                OptionChoice(name='Starts', value='starts'),
                OptionChoice(name='Contains', value='contains')
            ]
        ),
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        if query == None:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_item_missing_parameters').format(prefix = ctx.prefix),
                color = util.Colors.BLUE
            ))
            return

        else:

            if util.fortniteapi[lang]._loaded_cosmetics == False:

                await ctx.respond(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_cosmetics_data_loading'),
                    color = util.Colors.ORANGE
                ))
                return

            log.debug(f'Searching cosmetics with args: "{query}"')

            results = await util.fortniteapi[lang].get_cosmetic(query = query, match_method = match_method)

            if results == False:
                await ctx.respond(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_cosmetics_data_loading'),
                    color = util.Colors.ORANGE
                ))
                return
                

            if len(results) == 0:

                await ctx.respond(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_no_cosmetics_found'),
                    color = util.Colors.RED
                ))
                return

            else:

                items = []
                count = 0

                for cosmetic in results:
                    count += 1

                    i = discord.Embed(
                        title = f'{cosmetic["type"]["displayValue"]}',
                        description = f'**{cosmetic["name"]}**\n{cosmetic["description"]}',
                        color = util.get_color_by_rarity(cosmetic['rarity']['value'])
                    )

                    i.add_field(name=util.get_str(lang, 'command_string_id'), value=f'`{cosmetic["id"]}`', inline=False)
                    i.add_field(name=util.get_str(lang, 'command_string_rarity'), value=f'`{cosmetic["rarity"]["displayValue"]}`', inline=False)
                    i.add_field(name=util.get_str(lang, 'command_string_introduction'), value=f'`{cosmetic["introduction"]["text"]}`' if cosmetic['introduction'] else 'Not introduced yet', inline=False)
                    i.add_field(name=util.get_str(lang, 'command_string_set'), value=f'`{cosmetic["set"]["text"]}`' if cosmetic['set'] else 'None', inline=False)

                    if cosmetic['searchTags'] != None:

                        search_tags_str = ''
                        for tag in cosmetic['searchTags']:
                            search_tags_str += f'`{tag}`\n'

                        i.add_field(name=util.get_str(lang, 'command_string_search_tags'), value=search_tags_str, inline=False)

                    else:
                        i.add_field(name=util.get_str(lang, 'command_string_search_tags'), value=util.get_str(lang, 'command_string_none'), inline=False)
                        

                    i.set_thumbnail(url=cosmetic['images']['icon'])

                    i.set_footer(text=util.get_str(lang, 'command_string_result_int_of_int').format(count = count, results = len(results)))

                    items.append(i)
    
                paginator = pages.Paginator(
                    pages = items
                )
                await paginator.respond(interaction = ctx.interaction)


    @slash_command(
        name=util.get_str('en', 'command_name_playlist'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_playlist'),
            'ja': util.get_str('ja', 'command_name_playlist'),
        },
        description=util.get_str('en', 'command_description_playlist'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_playlist'),
            'ja': util.get_str('ja', 'command_description_playlist')
        }
    )
    @commands.cooldown(5, 8, commands.BucketType.user)
    async def playlist(
        self,
        ctx: discord.ApplicationContext,
        query: Option(
            str,
            description = 'Name or ID of the playlist',
            required = True
        ),
        match_method: Option(
            str,
            description = 'Match method to use',
            required = False,
            default = 'contains',
            choices = [
                OptionChoice(name='Starts', value='starts'),
                OptionChoice(name='Contains', value='contains')
            ]
        ),
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        if util.fortniteapi[lang]._loaded_playlists == 0:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_playlists_data_loading'),
                color = util.Colors.ORANGE
            ))
            return

        else:

            if query == None:

                await ctx.respond(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_playlist_missing_parameters').format(prefix = ctx.prefix),
                    color = util.Colors.BLUE
                ))
                return

            else:

                results = await util.fortniteapi[lang].get_playlist(query = query, match_method = match_method)

                if len(results) == 0:

                    await ctx.respond(embed=discord.Embed(
                        description = util.get_str(lang, 'command_string_no_playlists_found'),
                        color = util.Colors.RED
                    ))
                    return

                else:

                    items = []
                    count = 0

                    for playlist in results:
                        count += 1

                        if playlist['description'] != None:
                            playlist_description = playlist['description']
                        else:
                            playlist_description = util.get_str(lang, 'command_string_none')

                        if playlist['subName'] != None:
                            playlist_title = f'{playlist["name"]} {playlist["subName"]}'
                        else:
                            playlist_title = playlist['name']

                        if playlist['accumulateToProfileStats'] == True:
                            playlist_affectStats = util.get_str(lang, 'command_string_yes')
                        elif playlist['accumulateToProfileStats'] == False:
                            playlist_affectStats = util.get_str(lang, 'command_string_no')
                        else:
                            playlist_affectStats = util.get_str(lang, 'command_string_unknown')

                        i = discord.Embed(
                            title = playlist_title,
                            description = playlist_description
                        )

                        i.add_field(name=util.get_str(lang, 'command_string_max_teams'), value=f'`{playlist["maxTeams"]}`', inline=True)
                        i.add_field(name=util.get_str(lang, 'command_string_max_team_size'), value=f'`{playlist["maxTeamSize"]}`', inline=True)
                        i.add_field(name=util.get_str(lang, 'command_string_affects_player_stats'), value=f'`{playlist_affectStats}`', inline=True)

                        if playlist['images']['showcase']:
                            i.set_image(url=playlist['images']['showcase'])

                        i.set_footer(text=util.get_str(lang, 'command_string_result_int_of_int').format(count = count, results = len(results)))

                        items.append(i)

                    paginator = pages.Paginator(
                        pages = items
                    )
                    await paginator.respond(interaction = ctx.interaction)


    @slash_command(
        name=util.get_str('en', 'command_name_sections'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_sections'),
            'ja': util.get_str('ja', 'command_name_sections'),
        },
        description=util.get_str('en', 'command_description_sections'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_sections'),
            'ja': util.get_str('ja', 'command_description_sections')
        }
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def sections(
        self,
        ctx: discord.ApplicationContext,
        query: Option(
            str,
            description = 'Name or id to search',
            required = True
        ),
        match_method: Option(
            str,
            description = 'Match method to use',
            required = False,
            default = 'contains',
            choices = [
                OptionChoice(name='Starts', value='starts'),
                OptionChoice(name='Contains', value='contains')
            ]
        ),
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        await ctx.defer()

        async with aiofiles.open(f'cache/shopsections/current.json', 'r', encoding='utf-8') as f:
            active_sections = json.loads(await f.read())

        async with aiofiles.open(f'cache/shopsections/sections_{lang}.json', 'r', encoding='utf-8') as f:
            sections = json.loads(await f.read())

        embeds = []
        for section in sections:
            
            if match_method == 'starts':

                continueCount = 0
                if not section.get('sectionId', '').lower().startswith(query.lower()):
                    continueCount += 1

                if not section.get('sectionDisplayName', '').lower().startswith(query.lower()):
                    continueCount += 1

                if continueCount >= 2:
                    continue

            elif match_method == 'contains':

                continueCount = 0
                if not query.lower() in section.get('sectionId', '').lower():
                    continueCount += 1

                if not query.lower() in section.get('sectionDisplayName', '').lower():
                    continueCount += 1

                if continueCount >= 2:
                    continue

            embed = discord.Embed(
                title = 'Shop Sections',
                color = util.Colors.GREEN
            )

            embed.add_field(
                name = util.get_str(lang, 'command_string_section_section_id'),
                value = section.get('sectionId', util.get_str(lang, 'command_string_none'))
            )
            embed.add_field(
                name = util.get_str(lang, 'command_string_section_display_name'),
                value = section.get('sectionDisplayName', util.get_str(lang, 'command_string_none'))
            )
            embed.add_field(
                name = util.get_str(lang, 'command_string_section_priority'),
                value = section.get('landingPriority', util.get_str(lang, 'command_string_none'))
            )
            embed.add_field(
                name = util.get_str(lang, 'command_string_section_has_timer'),
                value = util.get_str(lang, 'command_string_yes') if section.get('bShowTimer', False) == True else util.get_str(lang, 'command_string_no')
            )
            embed.add_field(
                name = util.get_str(lang, 'command_string_section_can_notify'),
                value = util.get_str(lang, 'command_string_yes') if section.get('bEnableToastNotification', False) == True else util.get_str(lang, 'command_string_no')
            )

            if section.get('sectionId', '') in list(active_sections.keys()):
                embed.set_footer(text = util.get_str(lang, 'command_string_section_active_notice'))
            
            embeds.append(embed)

        if len(embeds) == 0:
            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_no_sections_found'),
                color = util.Colors.RED
            ))
            return

        paginator = pages.Paginator(
            pages = embeds
        )
        await paginator.respond(interaction = ctx.interaction)


    @slash_command(
        name=util.get_str('en', 'command_name_shop'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_shop'),
            'ja': util.get_str('ja', 'command_name_shop'),
        },
        description=util.get_str('en', 'command_description_shop'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_shop'),
            'ja': util.get_str('ja', 'command_description_shop')
        }
    )
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def shop(
        self,
        ctx
    ):
        lang = util.get_lang(ctx)
        server = await util.database_get_server(ctx)
        url = util.get_custom_shop_url(server)

        embed = discord.Embed(
            title = util.get_str(lang, 'command_string_current_item_shop'),
            color = util.Colors.BLURPLE
        )
        embed.set_image(url = url)

        await ctx.respond(embed = embed)

    @slash_command(
        name=util.get_str('en', 'command_name_news'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_news'),
            'ja': util.get_str('ja', 'command_name_news'),
        },
        description=util.get_str('en', 'command_description_news'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_news'),
            'ja': util.get_str('ja', 'command_description_news')
        }
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def news(
        self,
        ctx,
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        data = await util.fortniteapi[lang].get_news(language = lang)

        if data == False:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_error_fetching_news'),
                color = util.Colors.BLUE
            ))
            return
        
        else:

            items = []

            if data['data']['br'] != None:
                for motd in data['data']['br']['motds']:

                    embed = discord.Embed(
                        title = util.get_str(lang, 'command_button_battle_royale'),
                        description = f'**{motd["title"]}**\n{motd["body"]}',
                        color = util.Colors.BLUE
                    )
                    embed.set_image(url=motd['image'])
                    
                    items.append(embed)

            if data['data']['stw'] != None:
                for message in data['data']['stw']['messages']:

                    embed = discord.Embed(
                        title = util.get_str(lang, 'command_button_save_the_world'),
                        description = f'**{message["title"]}**\n{message["body"]}',
                        color = util.Colors.BLUE
                    )
                    embed.set_image(url=message['image'])
                    
                    items.append(embed)

            paginator = pages.Paginator(
                pages = items
            )
            await paginator.respond(interaction = ctx.interaction)

    @slash_command(
        name=util.get_str('en', 'command_name_aes'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_aes'),
            'ja': util.get_str('ja', 'command_name_aes'),
        },
        description=util.get_str('en', 'command_description_aes'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_aes'),
            'ja': util.get_str('ja', 'command_description_aes')
        }
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def aes(
        self,
        ctx,
        keyformat: Option(
            str,
            description = 'Keys format',
            required = False,
            default = 'hex',
            choices = [
                OptionChoice(name='Hex', value='hex'),
                OptionChoice(name='Base64', value='base64')
            ]
        ),
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        data = await util.fortniteapi[lang].get_aes(keyformat=keyformat)

        if data == False:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_unavailable_aes'),
                color = util.Colors.RED
            ))
            return

        embed = discord.Embed(
            title = util.get_str(lang, 'command_string_aes_for_build').format(build = data['data']['build']), 
            description = util.get_str(lang, 'command_string_main_key').format(key = data['data']['mainKey']),
            color = util.Colors.BLUE
        )

        items = []

        count = 0
        for key in data['data']['dynamicKeys']:
            count += 1

            if count == 5:
                embed.set_footer(text=f'Page {len(items) + 1}')
                items.append(embed)

                embed = discord.Embed(
                    title = util.get_str(lang, 'command_string_aes_for_build').format(build = data['data']['build']), 
                    description = util.get_str(lang, 'command_string_main_key').format(key = data['data']['mainKey']),
                    color = util.Colors.BLUE
                )
                count = 0

            embed.add_field(name=key['pakFilename'], value=f'GUID: {key["pakGuid"]}\n{util.get_str(lang, "command_string_key")}: {key["key"]}', inline=False)

        paginator = pages.Paginator(
            pages = items
        )
        await paginator.respond(interaction = ctx.interaction)
    
    @slash_command(
        name=util.get_str('en', 'command_name_stats'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_stats'),
            'ja': util.get_str('ja', 'command_name_stats'),
        },
        description=util.get_str('en', 'command_description_stats'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_stats'),
            'ja': util.get_str('ja', 'command_description_stats')
        }
    )
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def stats(
        self,
        ctx: discord.ApplicationContext,
        display_name: Option(
            str,
            description = 'Account display name',
            required = True
        ),
        account_type: Option(
            str,
            description = 'Type of account',
            required = False,
            default = 'epic',
            choices = [
                OptionChoice(name = 'Epic', value = 'epic'),
                OptionChoice(name = 'PlayStation', value = 'psn'),
                OptionChoice(name = 'Xbox', value = 'xbl')
            ]
        ),
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        data = await util.fortniteapi[lang].get_stats(
            account_name = display_name,
            account_type = account_type
        )
        
        if data['status'] == 404:

            embed = discord.Embed(
                description = util.get_str(lang, 'command_string_no_stats_or_not_exists'),
                color = util.Colors.RED
            )
            await ctx.respond(
                embed = embed
            )
            return

        elif data['status'] == 403:

            embed = discord.Embed(
                description = util.get_str(lang, 'command_string_stats_are_private'),
                color = util.Colors.RED
            )
            await ctx.respond(
                embed = embed
            )
            return

        else:

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_stats_of_name').format(name = data['data']['account']['name']),
                color = util.Colors.BLUE
            )
            embed.set_image(url=f'{data["data"]["image"]}?cache={time.time()}') # discord cache goes brrrrrrr
            embed.set_footer(text=util.get_str(lang, 'command_string_stats_footer').format(level = data['data']['battlePass']['level'], accountId = data['data']['account']['id']))

            await ctx.respond(
                embed = embed
            )


    @slash_command(
        name=util.get_str('en', 'command_name_code'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_code'),
            'ja': util.get_str('ja', 'command_name_code'),
        },
        description=util.get_str('en', 'command_description_code'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_code'),
            'ja': util.get_str('ja', 'command_description_code')
        }
    )
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def code(
        self,
        ctx: discord.ApplicationContext,
        creatorcode: Option(
            str,
            description = 'Creator code to check',
            required = True
        ),
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        data = await util.fortniteapi[lang].get_cc(code = creatorcode)

        if data == False:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_no_code_found'),
                color = util.Colors.RED
            ))
            return

        else:

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_creator_code_search'),
                color = util.Colors.BLUE
            )

            embed.add_field(name=util.get_str(lang, 'command_string_code'), value=f'`{data["data"]["code"]}`')
            embed.add_field(name=util.get_str(lang, 'command_string_account'), value=f'`{data["data"]["account"]["name"]}`')
            embed.add_field(name=util.get_str(lang, 'command_string_status'), value=f'`{data["data"]["status"]}`')

            embed.set_footer(text=util.get_str(lang, 'command_string_account_id').format(id = data['data']['account']['id']))

            await ctx.respond(
                embed = embed
            )


    @slash_command(
        name=util.get_str('en', 'command_name_upcoming'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_upcoming'),
            'ja': util.get_str('ja', 'command_name_upcoming'),
        },
        description=util.get_str('en', 'command_description_upcoming'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_upcoming'),
            'ja': util.get_str('ja', 'command_description_upcoming')
        }
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def upcoming(
        self,
        ctx: discord.ApplicationContext,
        language: Option(
            str,
            description = 'Language to use',
            required = False,
            default = 'none',
            choices = [
                OptionChoice(
                    name = lang,
                    value = lang
                ) for lang in util.configuration.get('languages')
            ]
        )
    ):

        lang = util.get_lang(ctx)
        if language != 'none':
            lang = language

        data = await util.fortniteapi[lang].get_new_items()

        if data == False:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_upcoming_cosmetics_fetch_error'),
                color = util.Colors.RED
            ))
            return

        else:

            items = []

            count = 0

            for cosmetic in data['data']['items']:

                count += 1

                i = discord.Embed(
                    title = util.get_str(lang, 'command_string_upcoming_cosmetics'),
                    description = util.get_str(lang, 'command_string_upcoming_cosmetics_for_build').format(build = data['data']['build']),
                    color = util.get_color_by_rarity(cosmetic['rarity']['value'])
                )

                i.add_field(name=util.get_str(lang, 'command_string_name'), value=f'`{cosmetic["name"]}`', inline=False)
                i.add_field(name=util.get_str(lang, 'command_string_description_no_dots'), value=f'`{cosmetic["description"]}`', inline=False)
                i.add_field(name=util.get_str(lang, 'command_string_id'), value=f'`{cosmetic["id"]}`', inline=False)
                i.add_field(name=util.get_str(lang, 'command_string_rarity'), value=f'`{cosmetic["rarity"]["displayValue"]}`', inline=False)
                i.add_field(name=util.get_str(lang, 'command_string_set'), value=f'`{cosmetic["set"]["text"]}`' if cosmetic['set'] else util.get_str(lang, 'command_string_none'), inline=False)

                i.set_thumbnail(url=cosmetic['images']['icon'])

                i.set_footer(text=util.get_str(lang, 'command_string_result_int_of_int').format(count = count, results = len(data['data']['items'])))

                items.append(i)

            paginator = pages.Paginator(
                pages = items
            )
            await paginator.respond(interaction = ctx.interaction) 
    
def setup(bot):
    bot.add_cog(General(bot))