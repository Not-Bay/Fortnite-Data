from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands, pages
import traceback
import aiohttp
import discord
import logging
import time
import json
import cgi
import io

from modules import util, views

log = logging.getLogger('FortniteData.cogs.general')

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name='item',
        description=util.get_str('en', 'command_description_item'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_item'),
            'ja': util.get_str('ja', 'command_description_item')
        },
        guild_ids=util.debug_guilds
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
        )
    ):

        lang = util.get_guild_lang(ctx)

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
                            search_tags_str + f'`{tag}`' + '\n'

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
        name='playlist',
        description=util.get_str('en', 'command_description_playlist'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_playlist'),
            'ja': util.get_str('ja', 'command_description_playlist')
        },
        guild_ids=util.debug_guilds
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
        )
    ):

        lang = util.get_guild_lang(ctx)

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
        name='shop',
        description=util.get_str('en', 'command_description_shop'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_shop'),
            'ja': util.get_str('ja', 'command_description_shop')
        },
        guild_ids=util.debug_guilds
    )
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def shop(
        self,
        ctx
    ):

        lang = util.get_guild_lang(ctx)
        url = util.get_custom_shop_url(util.database_get_server(ctx))

        embed = discord.Embed(
            title = util.get_str(lang, 'command_string_current_item_shop'),
            color = util.Colors.BLURPLE
        )
        embed.set_image(url = url)

        await ctx.respond(embed = embed)

    @slash_command(
        name='news',
        description=util.get_str('en', 'command_description_news'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_news'),
            'ja': util.get_str('ja', 'command_description_news')
        },
        guild_ids=util.debug_guilds
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def news(
        self,
        ctx,
        language = Option(
            str,
            description = 'Language for the news',
            required = False,
            default = 'none'
        )
    ):

        lang = util.get_guild_lang(ctx)
        data_lang = language if language != 'none' else lang

        data = await util.fortniteapi[lang].get_news(language = data_lang)

        if data == False:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_error_fetching_news'),
                color = util.Colors.BLUE
            ))
            return
        
        else:

            items = []

            count = 0
            if data['data']['br'] != None:
                for motd in data['data']['br']['motds']:
                    count += 1

                    embed = discord.Embed(
                        title = util.get_str(data_lang, 'command_button_battle_royale'),
                        description = f'**{motd["title"]}**\n{motd["body"]}',
                        color = util.Colors.BLUE
                    )
                    embed.set_image(url=motd['image'])
                    embed.set_footer(text=util.get_str(data_lang, 'command_string_page_int_of_int').format(count = count, total = len(data['data']['br']['motds'])))
                    
                    items.append(embed)

            count = 0
            if data['data']['stw'] != None:
                for message in data['data']['stw']['messages']:
                    count += 1

                    embed = discord.Embed(
                        title = util.get_str(data_lang, 'command_button_save_the_world'),
                        description = f'**{message["title"]}**\n{message["body"]}',
                        color = util.Colors.BLUE
                    )
                    embed.set_image(url=message['image'])
                    embed.set_footer(text=util.get_str(data_lang, 'command_string_page_int_of_int').format(count = count, total = len(data['data']['stw']['messages'])))
                    
                    items.append(embed)

            paginator = pages.Paginator(
                pages = items
            )
            await paginator.respond(interaction = ctx.interaction)

    @slash_command(
        name='aes',
        description=util.get_str('en', 'command_description_aes'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_aes'),
            'ja': util.get_str('ja', 'command_description_aes')
        },
        guild_ids=util.debug_guilds
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
        )
    ):

        lang = util.get_guild_lang(ctx)

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
        name='stats',
        description=util.get_str('en', 'command_description_stats'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_stats'),
            'ja': util.get_str('ja', 'command_description_stats')
        },
        guild_ids=util.debug_guilds
    )
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def stats(
        self,
        ctx: discord.ApplicationContext,
        display_name: Option(
            str,
            description = 'Account display name',
            required=True,
        ),
        account_type = Option(
            str,
            description = 'Type of account',
            required = True,
            choices = [
                OptionChoice(name = 'Epic', value = 'epic'),
                OptionChoice(name = 'PlayStation', value = 'psn'),
                OptionChoice(name = 'Xbox', value = 'xbl')
            ]
        )
    ):

        lang = util.get_guild_lang(ctx)

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
        name='code',
        description=util.get_str('en', 'command_description_code'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_code'),
            'ja': util.get_str('ja', 'command_description_code')
        },
        guild_ids=util.debug_guilds
    )
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def code(
        self,
        ctx: discord.ApplicationContext,
        code: Option(
            str,
            description = 'Creator code to check',
            required = True
        )
    ):

        lang = util.get_guild_lang(ctx)

        data = await util.fortniteapi[lang].get_cc(code = code)

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
        name='upcoming',
        description=util.get_str('en', 'command_description_upcoming'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_upcoming'),
            'ja': util.get_str('ja', 'command_description_upcoming')
        },
        guild_ids=util.debug_guilds
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def upcoming(
        self,
        ctx: discord.ApplicationContext
    ):

        lang = util.get_guild_lang(ctx)

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


    @slash_command(
        name='files-search',
        description=util.get_str('en', 'command_description_search'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_search'),
            'ja': util.get_str('ja', 'command_description_search')
        },
        guild_ids=util.debug_guilds
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def search(
        self,
        ctx: discord.ApplicationContext,
        filename = Option(
            str,
            description = 'File name to search',
            required = True
        )
    ):

        lang = util.get_guild_lang(ctx)

        async with aiohttp.ClientSession() as session:

            response = await session.get(f'https://benbot.app/api/v1/files/search?path={filename}')

            if response.status == 200:

                if len(await response.text()) == 2: # empty list
                    await ctx.respond(embed=discord.Embed(
                        description = util.get_str(lang, 'command_string_search_nothing_found'),
                        color = util.Colors.RED
                    ))
                    return

                else:

                    results = await response.json()

                    embed_description = f'{util.get_str(lang, "command_string_search_results").format(query = filename)}\n'

                    fileNeeded = False
                    
                    for i in results:
                        embed_description += f'`{i}`\n'

                        if len(embed_description) > 2048:
                            fileNeeded = True
                            break
                    
                    if fileNeeded:

                        file = discord.File(
                            io.StringIO(json.dumps(results, indent=2, ensure_ascii=False)),
                            filename = 'results.json'
                        )
                        await ctx.respond(file = file)
                        return

                    else:

                        embed = discord.Embed(
                            title = util.get_str(lang, 'command_string_file_search'),
                            description = embed_description,
                            color = util.Colors.BLUE
                        )
                        await ctx.respond(embed = embed)
                        return

            else:

                embed = discord.Embed(
                    description = util.get_str(lang, 'command_string_api_error_on_file_search').format(status = response.status),
                    color = util.Colors.RED
                )
                await ctx.respond(embed = embed)

    
    @slash_command(
        name='files-export',
        description=util.get_str('en', 'command_description_export'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_export'),
            'ja': util.get_str('ja', 'command_description_export')
        },
        guild_ids=util.debug_guilds
    )
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def export(
        self,
        ctx: discord.ApplicationContext,
        filename: Option(
            str,
            description = 'File name to export'
        )
    ):

        lang = util.get_guild_lang(ctx)

        if filename == None:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_export_missing_parameters').format(prefix = ctx.prefix),
                color = util.Colors.BLUE
            ))
            return
        
        else:

            if filename.endswith('.uasset') == False:

                await ctx.respond(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_export_error_no_uasset_filename'),
                    color = util.Colors.RED
                ))
                return

            else:

                async with aiohttp.ClientSession() as session:

                    response = await session.get(f'https://benbot.app/api/v1/exportAsset?path={filename}')

                    if response.status == 404:

                        await ctx.respond(embed=discord.Embed(
                            description = util.get_str(lang, 'command_string_export_error_no_file_found'),
                            color = util.Colors.RED
                        ))
                        return

                    elif response.status == 200:

                        value, params = cgi.parse_header(response.headers['Content-Disposition'])
                        filename = params['filename']

                        if response.headers['Content-Type'] == 'application/json':

                            file = discord.File(
                                io.StringIO(json.dumps(await response.text())),
                                filename
                            )

                        elif response.headers['Content-Type'] == 'image/png':

                            file = discord.File(
                                io.BytesIO(await response.read()),
                                filename
                            )

                        elif response.headers['Content-Type'] == 'audio/ogg':

                            file = discord.File(
                                io.BytesIO(await response.read()),
                                filename
                            )

                        else:

                            file = discord.File(
                                io.BytesIO(await response.read()),
                                filename
                            )

                        try:
                            await ctx.respond(file = file)

                        except:

                            embed = discord.Embed(
                                description = util.get_str(lang, 'command_string_export_error_sending_file').format(traceback = traceback.format_exc()),
                                color = util.Colors.RED
                            )
                            await ctx.respond(embed = embed)

                    else:

                        embed = discord.Embed(
                            description = util.get_str(lang, 'command_string_api_error_on_file_export').format(status = response.status),
                            color = util.Colors.RED
                        )
                        await ctx.respond(embed = embed)
   
    
def setup(bot):
    bot.add_cog(General(bot))