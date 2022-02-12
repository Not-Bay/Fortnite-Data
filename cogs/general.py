from discord.ext import commands
from discord_components import *
import traceback
import aiohttp
import asyncio
import discord
import logging
import time
import json
import cgi
import io

import util

log = logging.getLogger('FortniteData.cogs.general')

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='help [command]')
    @commands.cooldown(4, 10, commands.BucketType.user)
    async def help(self, ctx, command_=None):
        """
        Shows the commands of the bot. Shows info about a command if you enter it as argument
        """

        lang = util.get_guild_lang(ctx)

        if command_ == None:

            prefix = util.get_prefix(self.bot, ctx.message)

            commands_list = ['help', 'item', 'news', 'shop', 'stats', 'aes', 'upcoming', 'code', 'search', 'export', 'invite', 'ping', 'info', 'settings']

            general_cmds_str = ''
            for command in commands_list:
                try:
                    cmd = self.bot.get_command(command)
                    general_cmds_str += f'`{prefix}{cmd.usage}`' + '\n'
                except:
                    continue

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_help'),
                description = util.get_str(lang, 'command_string_to_see_more_info_about_a_command').format(prefix = ctx.prefix),
                color = util.Colors.BLURPLE
            )
            embed.add_field(name=util.get_str(lang, 'command_string_commands'), value=general_cmds_str, inline=False)

            embed.set_footer(text=util.get_str(lang, 'command_string_footer_credits').format(version = util.version))
            embed.set_thumbnail(url='https://images-ext-2.discordapp.net/external/BZlqfymUFg4jvrOetFhqr6u6YbaptHhYkPCR7yZUb10/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/729409703360069722/f1fcb3da5b075da0c6e5283bcb8b3fba.webp')

            components = [
                Button(style=ButtonStyle.URL, label=util.get_str(lang, 'command_button_support_server'), url='https://discord.gg/UU9HjA5')
            ]

            await ctx.send(embed=embed, components=components)
            return
        
        else:

            cmd = self.bot.get_command(command_)

            if cmd == None:

                await ctx.send(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_command_not_found'),
                    color = util.Colors.RED
                ))
                return

            else:

                prefix = util.get_prefix(self.bot, ctx.message)

                aliases_str = ''
                for alias in cmd.aliases:
                    aliases_str += f'`{alias}` '

                if aliases_str == '':
                    aliases_str = util.get_str(lang, 'command_string_no_alias_found')

                embed = discord.Embed(
                    title = util.get_str(lang, 'command_string_help'),
                    description = util.get_str(lang, 'command_string_command').format(prefix = ctx.prefix, command = cmd.name),
                    color = util.Colors.BLURPLE
                )
                embed.add_field(name=util.get_str(lang, 'command_string_description'), value=f'`{cmd.help}`', inline=False)
                embed.add_field(name=util.get_str(lang, 'command_string_usage'), value=f'`{prefix}{cmd.usage}`', inline=False)
                embed.add_field(name=util.get_str(lang, 'command_string_aliases'), value=aliases_str, inline=False)

                embed.set_thumbnail(url='https://images-ext-2.discordapp.net/external/BZlqfymUFg4jvrOetFhqr6u6YbaptHhYkPCR7yZUb10/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/729409703360069722/f1fcb3da5b075da0c6e5283bcb8b3fba.webp')

                await ctx.send(embed=embed)

    
    @commands.command(usage='item <name or ID>', aliases=['cosmetic'])
    @commands.cooldown(5, 8, commands.BucketType.user)
    async def item(self, ctx, *, name_or_id = None):
        """Search for cosmetics by their name or ID. Special arguments available."""

        lang = util.get_guild_lang(ctx)

        if name_or_id == None:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_item_missing_parameters').format(prefix = ctx.prefix),
                color = util.Colors.BLUE
            ))
            return

        else:

            if util.fortniteapi[lang]._loaded_cosmetics == False:

                await ctx.send(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_cosmetics_data_loading'),
                    color = util.Colors.ORANGE
                ))
                return

            special_args = [  # this acts like a filter. For example if you type "f!item ren --outfit"
                '--outfit',   # will return only outfits with "re"
                '--emote',
                '--backpack',
                '--pickaxe',
                '--wrap',
                '--loadingscreen',
                '--spray',
                '--glider',
                '--banner',
                '--contains',
                '--starts'
            ]

            cosmetic_type = None
            match_method = None
            splitted_name_or_id = name_or_id.split()

            log.debug(f'Checking for special args in "{name_or_id}"')

            if len(splitted_name_or_id) != 1:

                for i in splitted_name_or_id:

                    if i.lower() in special_args:

                        if i.lower() in ['--contains', '--starts']:
                            match_method = str(i.replace('--', ''))

                        else:
                            cosmetic_type = str(i.replace('--', ''))

                        name_or_id = name_or_id.replace(f' {i}', '')

                        log.debug(f'Detected special arg: "{i}"')

                    else:

                        continue


            if cosmetic_type == None:

                log.debug(f'Searching with args: "{name_or_id}"')

                if match_method == None:
                    results = await util.fortniteapi[lang].get_cosmetic(query = name_or_id)
                
                else:

                    results = await util.fortniteapi[lang].get_cosmetic(query = name_or_id, match_method = match_method)

            
            else:

                log.debug(f'Searching {cosmetic_type} with args: "{name_or_id}"')

                if match_method == None:
                    results = await util.fortniteapi[lang].get_cosmetic(query = name_or_id, cosmetic_type = cosmetic_type)
                
                else:
                    results = await util.fortniteapi[lang].get_cosmetic(query = name_or_id, cosmetic_type = cosmetic_type, match_method = match_method)

            if results == False:
                await ctx.send(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_cosmetics_data_loading'),
                    color = util.Colors.ORANGE
                ))
                return
                

            if len(results) == 0:

                await ctx.send(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_no_cosmetics_found'),
                    color = util.Colors.RED
                ))
                return

            else:

                current_page = 0

                pages = []
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

                    pages.append(i)


                components = []

                if len(results) > 1:
                    components = [[
                        Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                        Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                        Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
                        Button(style=ButtonStyle.blue, label='>>', custom_id='PAGE_TO_FINAL', disabled=True if current_page + 1 == len(pages) else False)
                    ]]

                msg = await ctx.send(
                    embed = pages[current_page],
                    components = components
                )

                def check(interaction):
                    return interaction.author == ctx.author and interaction.message == msg

                while True:

                    try:

                        interaction = await self.bot.wait_for('button_click', check=check, timeout=300)

                        if interaction.custom_id == 'PAGE_NEXT':
                            current_page += 1

                        elif interaction.custom_id == 'PAGE_BACK':
                            current_page -= 1

                        elif interaction.custom_id == 'PAGE_TO_FIRST':
                            current_page = 0

                        elif interaction.custom_id == 'PAGE_TO_FINAL':
                            current_page = len(pages) - 1

                        await interaction.respond(
                            type = 7,
                            embed = pages[current_page],
                            components = [[
                                Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                                Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                                Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
                                Button(style=ButtonStyle.blue, label='>>', custom_id='PAGE_TO_FINAL', disabled=True if current_page + 1 == len(pages) else False)
                            ]]
                        )
                        continue

                    except asyncio.TimeoutError:

                        await msg.edit(
                            embed = pages[current_page],
                            components = []
                        )
                        return

    @commands.command(usage='playlist <name or ID>')
    @commands.cooldown(5, 8, commands.BucketType.user)
    async def playlist(self, ctx, *, name_or_id = None):
        """Search for playlist by their name or ID."""

        lang = util.get_guild_lang(ctx)

        if util.fortniteapi[lang]._loaded_playlists == 0:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_playlists_data_loading'),
                color = util.Colors.ORANGE
            ))
            return

        else:

            if name_or_id == None:

                await ctx.send(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_playlist_missing_parameters').format(prefix = ctx.prefix),
                    color = util.Colors.BLUE
                ))
                return

            else:

                special_args = [ # just for match method
                    '--contains',
                    '--starts'
                ]

                match_method = 'starts'
                splitted_name_or_id = name_or_id.split()

                log.debug(f'Checking for special args in "{name_or_id}"')

                if len(splitted_name_or_id) != 1:

                    for i in splitted_name_or_id:

                        if i.lower() in special_args:

                            match_method = str(i.replace('--', ''))

                            name_or_id = name_or_id.replace(f' {i}', '')

                            log.debug(f'Detected special arg: "{i}"')

                            break

                        else:

                            continue

                results = await util.fortniteapi[lang].get_playlist(query = name_or_id, match_method = match_method)

                if len(results) == 0:

                    await ctx.send(embed=discord.Embed(
                        description = util.get_str(lang, 'command_string_no_playlists_found'),
                        color = util.Colors.RED
                    ))
                    return

                else:

                    current_page = 0

                    pages = []
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

                        pages.append(i)


                    components = []

                    if len(results) > 1:
                        components = [[
                            Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                            Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                            Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
                            Button(style=ButtonStyle.blue, label='>>', custom_id='PAGE_TO_FINAL', disabled=True if current_page + 1 == len(pages) else False)
                        ]]

                    msg = await ctx.send(
                        embed = pages[current_page],
                        components = components
                    )

                    def check(interaction):
                        return interaction.author == ctx.author and interaction.message == msg

                    while True:

                        try:

                            interaction = await self.bot.wait_for('button_click', check=check, timeout=300)

                            if interaction.custom_id == 'PAGE_NEXT':
                                current_page += 1

                            elif interaction.custom_id == 'PAGE_BACK':
                                current_page -= 1

                            elif interaction.custom_id == 'PAGE_TO_FIRST':
                                current_page = 0

                            elif interaction.custom_id == 'PAGE_TO_FINAL':
                                current_page = len(pages) - 1

                            await interaction.respond(
                                type = 7,
                                embed = pages[current_page],
                                components = [[
                                    Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
                                    Button(style=ButtonStyle.blue, label='>>', custom_id='PAGE_TO_FINAL', disabled=True if current_page + 1 == len(pages) else False)
                                ]]
                            )
                            continue

                        except asyncio.TimeoutError:

                            await msg.edit(
                                embed = pages[current_page],
                                components = []
                            )
                            return


    @commands.command(usage='shop [language]', aliases=['itemshop'])
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def shop(self, ctx, language = 'en'):
        """Shows the latest fortnite item shop image."""

        lang = util.get_guild_lang(ctx)

        url = util.get_custom_shop_url(util.database_get_server(ctx.guild))

        embed = discord.Embed(
            title = util.get_str(lang, 'command_string_current_item_shop'),
            color = util.Colors.BLURPLE
        )
        embed.set_image(url = url)

        await ctx.send(embed = embed)

    @commands.command(usage='news [language]')
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def news(self, ctx, language = None):
        """Shows an interactive message with all the game news (Battle Royale, Creative and Save The World)"""

        lang = util.get_guild_lang(ctx)
        data_lang = language if language != None else lang

        data = await util.fortniteapi[lang].get_news(language = data_lang)

        if data == False:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_error_fetching_news'),
                color = util.Colors.BLUE
            ))
            return
        
        else:

            br_motds = []
            cr_motds = []
            stw_motds = []

            count = 0
            if data['data']['br'] != None:
                for motd in data['data']['br']['motds']:
                    count += 1

                    embed = discord.Embed(
                        title = motd['tabTitle'],
                        description = f'**{motd["title"]}**\n{motd["body"]}',
                        color = util.Colors.BLUE
                    )
                    embed.set_footer(text=f'Page {count} of {len(data["data"]["br"]["motds"])}')
                    embed.set_image(url=motd['image'])
                    
                    br_motds.append(embed)

            count = 0
            if data['data']['creative'] != None:
                for motd in data['data']['creative']['motds']:
                    count += 1

                    embed = discord.Embed(
                        title = motd['tabTitle'],
                        description = f'**{motd["title"]}**\n{motd["body"]}',
                        color = util.Colors.BLUE
                    )
                    embed.set_image(url=motd['image'])
                    embed.set_footer(text=f'Page {count} of {len(data["data"]["creative"]["motds"])}')
                    
                    cr_motds.append(embed)

            count = 0
            if data['data']['stw'] != None:
                for message in data['data']['stw']['messages']:
                    count += 1

                    embed = discord.Embed(
                        title = message['adspace'],
                        description = f'**{message["title"]}**\n{message["body"]}',
                        color = util.Colors.BLUE
                    )
                    embed.set_image(url=message['image'])
                    embed.set_footer(text=f'Page {count} of {len(data["data"]["stw"]["messages"])}')
                    
                    stw_motds.append(embed)


            books = [br_motds, cr_motds, stw_motds]
            current_book = 0
            current_page = 0

            msg = await ctx.send(
                embed = books[current_book][current_page],
                components = [
                    [
                        Button(style=ButtonStyle.green if current_book == 0 else ButtonStyle.gray, label=util.get_str(lang, 'command_button_battle_royale'), custom_id='SHOW_BR_BOOK', disabled=True if current_book == 0 else False),
                       #Button(style=ButtonStyle.green if current_book == 1 else ButtonStyle.gray, label=util.get_str(lang, 'command_button_creative'), custom_id='SHOW_CR_BOOK', disabled=True if current_book == 1 else False),
                        Button(style=ButtonStyle.green if current_book == 2 else ButtonStyle.gray, label=util.get_str(lang, 'command_button_save_the_world'), custom_id='SHOW_STW_BOOK', disabled=True if current_book == 2 else False)
                    ],
                    [
                        Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                        Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(books[current_book]) else False)
                    ]
                ]
            )

            def check(interaction):
                    return interaction.author == ctx.author and interaction.message == msg

            while True:

                try:

                    interaction = await self.bot.wait_for('button_click', check=check, timeout=180)

                    if interaction.custom_id == 'PAGE_NEXT':
                        current_page += 1

                    elif interaction.custom_id == 'PAGE_BACK':
                        current_page -= 1

                    elif interaction.custom_id == 'SHOW_BR_BOOK':
                        current_book = 0
                        current_page = 0

                    elif interaction.custom_id == 'SHOW_CR_BOOK':
                        current_book = 1
                        current_page = 0

                    elif interaction.custom_id == 'SHOW_STW_BOOK':
                        current_book = 2
                        current_page = 0

                    components = [
                        [
                            Button(style=ButtonStyle.green if current_book == 0 else ButtonStyle.gray, label=util.get_str(lang, 'command_button_battle_royale'), custom_id='SHOW_BR_BOOK', disabled=True if current_book == 0 else False),
                            #Button(style=ButtonStyle.green if current_book == 1 else ButtonStyle.gray, label=util.get_str(lang, 'command_button_creative'), custom_id='SHOW_CR_BOOK', disabled=True if current_book == 1 else False),
                            Button(style=ButtonStyle.green if current_book == 2 else ButtonStyle.gray, label=util.get_str(lang, 'command_button_save_the_world'), custom_id='SHOW_STW_BOOK', disabled=True if current_book == 2 else False)
                        ],
                        [
                            Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                            Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(books[current_book]) else False)
                        ]
                    ]

                    await interaction.respond(
                        type = 7,
                        embed = books[current_book][current_page],
                        components = components
                    )
                    continue

                except asyncio.TimeoutError:

                    await msg.edit(
                        embed = books[current_book][current_page],
                        components = []
                    )
                    return

    @commands.command(usage='aes [base64 / hex]')
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def aes(self, ctx, keyformat = 'hex'):
        """Shows the current AES keys to decrypt game files"""

        lang = util.get_guild_lang(ctx)

        if keyformat.lower() not in ['base64', 'hex']:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_key_format_example').format(prefix = ctx.prefix),
                color = util.Colors.RED
            ))
            return

        else:

            data = await util.fortniteapi[lang].get_aes(keyformat=keyformat)

            if data == False:

                await ctx.send(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_unavailable_aes'),
                    color = util.Colors.RED
                ))
                return

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_aes_for_build').format(build = data['data']['build']), 
                description = util.get_str(lang, 'command_string_main_key').format(key = data['data']['mainKey']),
                color = util.Colors.BLUE
            )

            pages = []
            current_page = 0

            count = 0
            for key in data['data']['dynamicKeys']:
                count += 1

                if count == 5:
                    embed.set_footer(text=f'Page {len(pages) + 1}')
                    pages.append(embed)

                    embed = discord.Embed(
                        title = util.get_str(lang, 'command_string_aes_for_build').format(build = data['data']['build']), 
                        description = util.get_str(lang, 'command_string_main_key').format(key = data['data']['mainKey']),
                        color = util.Colors.BLUE
                    )
                    count = 0

                embed.add_field(name=key['pakFilename'], value=f'GUID: {key["pakGuid"]}\n{util.get_str(lang, "command_string_key")}: {key["key"]}', inline=False)

            if len(pages) == 1:

                await ctx.send(
                    embed = pages[0]
                )
                return

            else:

                components = [[
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False)
                ]]

                msg = await ctx.send(
                    embed = pages[current_page],
                    components = components
                )

                def check(interaction):
                    return interaction.author == ctx.author and interaction.message == msg

                while True:

                    try:

                        interaction = await self.bot.wait_for('button_click', check=check, timeout=180)

                        if interaction.custom_id == 'PAGE_NEXT':
                            current_page += 1

                        elif interaction.custom_id == 'PAGE_BACK':
                            current_page -= 1

                        await interaction.respond(
                            type = 7,
                            embed = pages[current_page],
                            components = [[
                                Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                                Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False)
                            ]]
                        )
                        continue

                    except asyncio.TimeoutError:

                        await msg.edit(
                            embed = pages[current_page],
                            components = []
                        )
                        return
    
    @commands.command(usage='stats <account name>')
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def stats(self, ctx, *, account_name = None):
        """Search for player stats. Search can be made for Epic, PSN and XBOX accounts"""

        lang = util.get_guild_lang(ctx)

        if account_name == None:
            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_stats_missing_parameters').format(prefix = ctx.prefix),
                color = util.Colors.BLUE
            ))
            return

        components = [[
            Button(style=ButtonStyle.grey, label='Epic', custom_id='SEARCH_TYPE_EPIC'),
            Button(style=ButtonStyle.blue, label='PlayStation', custom_id='SEARCH_TYPE_PSN'),
            Button(style=ButtonStyle.green, label='Xbox', custom_id='SEARCH_TYPE_XBOX')
        ]]

        msg = await ctx.send(
            embed=discord.Embed(
                description = util.get_str(lang, 'command_string_select_account_type'),
                color = util.Colors.BLUE
            ),
            components=components
        )

        def check(interaction):
            return interaction.author == ctx.author and interaction.message == msg

        try:

            interaction = await self.bot.wait_for('button_click', check=check, timeout=180)

            if interaction.custom_id == 'SEARCH_TYPE_EPIC':
                data = await util.fortniteapi[lang].get_stats(account_name=account_name, account_type='epic')
            
            elif interaction.custom_id == 'SEARCH_TYPE_PSN':
                data = await util.fortniteapi[lang].get_stats(account_name=account_name, account_type='psn')

            elif interaction.custom_id == 'SEARCH_TYPE_XBOX':
                data = await util.fortniteapi[lang].get_stats(account_name=account_name, account_type='xbl')

            
            if data['status'] == 404:

                embed = discord.Embed(
                    description = util.get_str(lang, 'command_string_no_stats_or_not_exists'),
                    color = util.Colors.RED
                )
                await interaction.respond(
                    type = 7,
                    embed = embed,
                    components = []
                )
                return

            elif data['status'] == 403:

                embed = discord.Embed(
                    description = util.get_str(lang, 'command_string_stats_are_private'),
                    color = util.Colors.RED
                )
                await interaction.respond(
                    type = 7,
                    embed = embed,
                    components = []
                )
                return

            elif data['status'] == 200:

                embed = discord.Embed(
                    title = util.get_str(lang, 'command_string_stats_of_name').format(name = data['data']['account']['name']),
                    color = util.Colors.BLUE
                )
                embed.set_image(url=f'{data["data"]["image"]}?cache={time.time()}')
                embed.set_footer(text=util.get_str(lang, 'command_string_stats_footer').format(level = data['data']['battlePass']['level'], accountId = data['data']['account']['id']))

                await interaction.respond(
                    type = 7,
                    embed = embed,
                    components = []
                )


        except asyncio.TimeoutError:

            await msg.edit(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_search_canceled_by_timeout'),
                color = util.Colors.RED
            ), components=[])


    @commands.command(usage='code <creator code>', aliases=['creatorcode', 'cc'])
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def code(self, ctx, *, creator_code = None):
        """Shows info about a creator code"""

        lang = util.get_guild_lang(ctx)

        if creator_code == None:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_code_missing_parameters').format(prefix = ctx.prefix),
                color = util.Colors.RED
            ))
            return

        else:

            data = await util.fortniteapi[lang].get_cc(code=creator_code)

            if data == False:

                await ctx.send(embed=discord.Embed(
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

                await ctx.send(embed=embed)
                

    @commands.command(usage='upcoming', aliases=['leaked'])
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def upcoming(self, ctx):
        """Shows an interactive message with all the new/upcoming cosmetics"""

        lang = util.get_guild_lang(ctx)

        data = await util.fortniteapi[lang].get_new_items()

        if data == False:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_upcoming_cosmetics_fetch_error'),
                color = util.Colors.RED
            ))
            return

        else:

            pages = []
            current_page = 0

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

                pages.append(i)


            components = []

            if len(pages) > 1:
                components = [[
                    Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
                    Button(style=ButtonStyle.blue, label='>>', custom_id='PAGE_TO_FINAL', disabled=True if current_page + 1 == len(pages) else False)
                ]]

            msg = await ctx.send(
                embed = pages[current_page],
                components = components
            )

            def check(interaction):
                return interaction.author == ctx.author and interaction.message == msg

            while True:

                try:

                    interaction = await self.bot.wait_for('button_click', check=check, timeout=180)

                    if interaction.custom_id == 'PAGE_NEXT':
                        current_page += 1

                    elif interaction.custom_id == 'PAGE_BACK':
                        current_page -= 1

                    elif interaction.custom_id == 'PAGE_TO_FIRST':
                        current_page = 0

                    elif interaction.custom_id == 'PAGE_TO_FINAL':
                        current_page = len(pages) - 1

                    await interaction.respond(
                        type = 7,
                        embed = pages[current_page],
                        components = [[
                            Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                            Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_back'), custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                            Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_button_next'), custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
                            Button(style=ButtonStyle.blue, label='>>', custom_id='PAGE_TO_FINAL', disabled=True if current_page + 1 == len(pages) else False)
                        ]]
                    )
                    continue

                except asyncio.TimeoutError:

                    await msg.edit(
                        embed = pages[current_page],
                        components = []
                    )
                    return

    @commands.command(usage='search <query>')
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def search(self, ctx, query = None):
        """
        Searches for .uasset files using the BenBot API
        """

        lang = util.get_guild_lang(ctx)

        if query == None:
            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_search_missing_parameters').format(prefix = ctx.prefix),
                color = util.Colors.BLUE
            ))
            return

        else:

            async with aiohttp.ClientSession() as session:

                response = await session.get(f'https://benbot.app/api/v1/files/search?path={query}')

                if response.status == 200:

                    if len(await response.text()) == 2: # empty list
                        await ctx.send(embed=discord.Embed(
                            description = util.get_str(lang, 'command_string_search_nothing_found'),
                            color = util.Colors.RED
                        ))
                        return

                    else:

                        results = await response.json()

                        embed_description = f'{util.get_str(lang, "command_string_search_results").format(query = query)}\n'

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
                            await ctx.send(file = file)
                            return

                        else:

                            embed = discord.Embed(
                                title = util.get_str(lang, 'command_string_file_search'),
                                description = embed_description,
                                color = util.Colors.BLUE
                            )
                            await ctx.send(embed = embed)
                            return

                else:

                    embed = discord.Embed(
                        description = util.get_str(lang, 'command_string_api_error_on_file_search').format(status = response.status),
                        color = util.Colors.RED
                    )
                    await ctx.send(embed = embed)


    
    @commands.command(usage='export <file name>', aliases=['extract'])
    @commands.cooldown(3, 12, commands.BucketType.user)
    async def export(self, ctx, filename: str):
        """
        Exports .uasset files using the BenBot API
        """

        lang = util.get_guild_lang(ctx)

        if filename == None:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_export_missing_parameters').format(prefix = ctx.prefix),
                color = util.Colors.BLUE
            ))
            return
        
        else:

            if filename.endswith('.uasset') == False:

                await ctx.send(embed=discord.Embed(
                    description = util.get_str(lang, 'command_string_export_error_no_uasset_filename'),
                    color = util.Colors.RED
                ))
                return

            else:

                async with aiohttp.ClientSession() as session:

                    response = await session.get(f'https://benbot.app/api/v1/exportAsset?path={filename}')

                    if response.status == 404:

                        await ctx.send(embed=discord.Embed(
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
                            await ctx.send(file = file)

                        except:

                            embed = discord.Embed(
                                description = util.get_str(lang, 'command_string_export_error_sending_file').format(traceback = traceback.format_exc()),
                                color = util.Colors.RED
                            )
                            await ctx.send(embed = embed)

                    else:

                        embed = discord.Embed(
                            description = util.get_str(lang, 'command_string_api_error_on_file_export').format(status = response.status),
                            color = util.Colors.RED
                        )
                        await ctx.send(embed = embed)
   
    
def setup(bot):
    bot.add_cog(General(bot))