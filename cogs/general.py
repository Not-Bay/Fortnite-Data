from discord.ext import commands
from discord_components import *
import traceback
import aiohttp
import asyncio
import discord
import logging
import time
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

        if command_ == None:

            prefix = util.get_prefix(self.bot, ctx.message)

            commands_list = ['help', 'item', 'news', 'shop', 'stats', 'aes', 'upcoming', 'code', 'settings']

            general_cmds_str = ''
            for command in commands_list:
                try:
                    cmd = self.bot.get_command(command)
                    general_cmds_str += f'`{prefix}{cmd.usage}`' + '\n'
                except:
                    continue

            embed = discord.Embed(
                title = 'Help',
                description = f'Use `{prefix}help <command>` to see more info about a command.',
                color = 0x349eeb
            )
            embed.add_field(name='Commands:', value=general_cmds_str, inline=False)

            embed.set_footer(text=f'Made by Bay#4384 • Version {util.version}')
            embed.set_thumbnail(url='https://images-ext-2.discordapp.net/external/BZlqfymUFg4jvrOetFhqr6u6YbaptHhYkPCR7yZUb10/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/729409703360069722/f1fcb3da5b075da0c6e5283bcb8b3fba.webp')

            components = [
                Button(style=ButtonStyle.URL, label='Support Server', url='https://discord.gg/UU9HjA5')
            ]

            await ctx.send(embed=embed, components=components)
            return
        
        else:

            cmd = self.bot.get_command(command_)

            if cmd == None:

                await ctx.send(embed=discord.Embed(
                    description = 'That command was not found',
                    color = 0xff2929
                ))
                return

            else:

                prefix = util.get_prefix(self.bot, ctx.message)

                aliases_str = ''
                for alias in cmd.aliases:
                    aliases_str += f'`{alias}` '

                if aliases_str == '':
                    aliases_str = 'There\'s no aliases'

                embed = discord.Embed(
                    title = 'Help',
                    description = f'Command `{prefix}{cmd.name}`:',
                    color = 0x349eeb
                )
                embed.add_field(name='Description:', value=f'`{cmd.help}`', inline=False)
                embed.add_field(name='Usage:', value=f'`{prefix}{cmd.usage}`', inline=False)
                embed.add_field(name='Aliases:', value=aliases_str, inline=False)

                embed.set_thumbnail(url='https://images-ext-2.discordapp.net/external/BZlqfymUFg4jvrOetFhqr6u6YbaptHhYkPCR7yZUb10/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/729409703360069722/f1fcb3da5b075da0c6e5283bcb8b3fba.webp')

                await ctx.send(embed=embed)

    
    @commands.command(usage='item <name or ID>', aliases=['cosmetic'])
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def item(self, ctx, *, name_or_id = None):
        """Search for cosmetics by their name or ID. Special arguments available."""

        server = util.database_get_server(ctx.guild)
        search_language = server['language']

        if name_or_id == None:

            await ctx.send(embed=discord.Embed(
                description = f'Missing parameters! Usage: `{ctx.prefix}item <name or ID>`',
                color = discord.Colour.blue()
            ))
            return

        else:

            special_args = [  # this acts like a filter. For example if you type "f!item ren --outfit"
                '--outfit',   # will return only outfits with "re"
                '--emote',
                '--backpack',
                '--pickaxe',
                '--wrap',
                '--loadingscreen',
                '--spray',
                '--glider',
                '--banner'
            ]

            cosmetic_type = None
            splitted_name_or_id = name_or_id.split()

            log.debug(f'Checking for special args in "{name_or_id}"')

            if len(splitted_name_or_id) != 1:

                for i in splitted_name_or_id:

                    if i.lower() in special_args:

                        cosmetic_type = str(i.replace('--', ''))
                        name_or_id = name_or_id.replace(f' {i}', '')

                        log.debug(f'Detected special arg: "{i}"')

                        break

                    else:

                        continue


            if cosmetic_type == None:

                log.debug(f'Searching with args: "{name_or_id}"')

                results = await util.fortniteapi.get_cosmetic(query = name_or_id, language=search_language)

            
            else:

                log.debug(f'Searching {cosmetic_type} with args: "{name_or_id}"')

                results = await util.fortniteapi.get_cosmetic(query = name_or_id, cosmetic_type=cosmetic_type, language=search_language)

            if results == False:
                await ctx.send(embed=discord.Embed(
                    description = f'Sorry but the cosmetics data for this language is currently loading. Please try again in a few seconds.',
                    color = discord.Colour.orange()
                ))
                return
                

            if len(results) == 0:

                await ctx.send(embed=discord.Embed(
                    description = 'No cosmetics were found with that name/id.',
                    color = discord.Colour.red()
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

                    i.add_field(name='ID', value=f'`{cosmetic["id"]}`', inline=False)
                    i.add_field(name='Rarity', value=f'`{cosmetic["rarity"]["displayValue"]}`', inline=False)
                    i.add_field(name='Introduction', value=f'`{cosmetic["introduction"]["text"]}`' if cosmetic['introduction'] else 'Not introduced yet', inline=False)
                    i.add_field(name='Set', value=f'`{cosmetic["set"]["text"]}`' if cosmetic['set'] else 'None', inline=False)

                    if cosmetic['searchTags'] != None:

                        search_tags_str = ''
                        for i in cosmetic['searchTags']:
                            search_tags_str + f'`{i}`' + '\n'

                        i.add_field(name='Search Tags', value=search_tags_str, inline=False)

                    else:
                        i.add_field(name='Search Tags', value=f'None', inline=False)
                        

                    i.set_thumbnail(url=cosmetic['images']['icon'])

                    i.set_footer(text=f'Result {count} of {len(results)}')

                    pages.append(i)


                components = []

                if len(results) > 1:
                    components = [[
                        Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                        Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                        Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
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
                                Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                                Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
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
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def shop(self, ctx, language = 'en'):
        """Shows the latest fortnite item shop image."""

        async with aiohttp.ClientSession() as session:

            URL = f'https://fortool.fr/cm/api/v1/shop?lang={language}'

            response = await session.get(URL)
            data = await response.json()

            if response.status != 200:

                if data['result'] == False:

                    await ctx.send(embed=discord.Embed(
                        description = f'Sorry but that language is not supported.',
                        color = discord.Colour.blue()
                    ))
                    return
                
                else:

                    await ctx.send(embed=discord.Embed(
                        description = f'An error ocurred getting item shop. API returned status {response.status}.',
                        color = discord.Colour.blue()
                    ))
                    return
            
            else:

                try:

                    data = await response.json()

                    embed = discord.Embed(
                        title = 'Current fortnite item shop',
                        color = discord.Colour.blue()
                    )
                    embed.set_image(url=f'{data["images"]["carousel"]}?cache={int(time.time())}')

                    await ctx.send(embed=embed)

                except KeyError:

                    await ctx.send(embed=discord.Embed(
                        description = 'Sorry but that language is not supported by the API.',
                        color = discord.Colour.blue()
                    ))
                    return

                except Exception:

                    log.error(f'An error ocurred sendind shop image. Traceback: {traceback.format_exc()}')

                    await ctx.send(embed=discord.Embed(
                        description = f'An error ocurred sending item shop image.',
                        color = discord.Colour.red()
                    ))
                    return

    @commands.command(usage='news [language]')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def news(self, ctx, language = 'en'):
        """Shows an interactive message with all the game news (Battle Royale, Creative and Save The World)"""

        data = await util.fortniteapi.get_news()

        if data == False:

            await ctx.send(embed=discord.Embed(
                description = 'An error ocurred getting news data. Please try again later.',
                color = discord.Colour.blue()
            ))
            return
        
        else:

            br_motds = []
            cr_motds = []
            stw_motds = []

            count = 0
            for motd in data['data']['br']['motds']:
                count += 1

                embed = discord.Embed(
                    title = motd['tabTitle'],
                    description = f'**{motd["title"]}**\n{motd["body"]}',
                    color = discord.Colour.blue()
                )
                embed.set_footer(text=f'Page {count} of {len(data["data"]["br"]["motds"])}')
                embed.set_image(url=motd['image'])
                
                br_motds.append(embed)

            count = 0
            for motd in data['data']['creative']['motds']:
                count += 1

                embed = discord.Embed(
                    title = motd['tabTitle'],
                    description = f'**{motd["title"]}**\n{motd["body"]}',
                    color = discord.Colour.blue()
                )
                embed.set_image(url=motd['image'])
                embed.set_footer(text=f'Page {count} of {len(data["data"]["creative"]["motds"])}')
                
                cr_motds.append(embed)

            count = 0
            for message in data['data']['stw']['messages']:
                count += 1

                embed = discord.Embed(
                    title = message['adspace'],
                    description = f'**{message["title"]}**\n{message["body"]}',
                    color = discord.Colour.blue()
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
                        Button(style=ButtonStyle.green if current_book == 0 else ButtonStyle.gray, label='Battle Royale', custom_id='SHOW_BR_BOOK', disabled=True if current_book == 0 else False),
                        Button(style=ButtonStyle.green if current_book == 1 else ButtonStyle.gray, label='Creative', custom_id='SHOW_CR_BOOK', disabled=True if current_book == 1 else False),
                        Button(style=ButtonStyle.green if current_book == 2 else ButtonStyle.gray, label='Save the World', custom_id='SHOW_STW_BOOK', disabled=True if current_book == 2 else False)
                    ],
                    [
                        Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                        Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(books[current_book]) else False)
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
                            Button(style=ButtonStyle.green if current_book == 0 else ButtonStyle.gray, label='Battle Royale', custom_id='SHOW_BR_BOOK', disabled=True if current_book == 0 else False),
                            Button(style=ButtonStyle.green if current_book == 1 else ButtonStyle.gray, label='Creative', custom_id='SHOW_CR_BOOK', disabled=True if current_book == 1 else False),
                            Button(style=ButtonStyle.green if current_book == 2 else ButtonStyle.gray, label='Save the World', custom_id='SHOW_STW_BOOK', disabled=True if current_book == 2 else False)
                        ],
                        [
                            Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                            Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(books[current_book]) else False)
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
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def aes(self, ctx, keyformat = 'hex'):
        """Shows the current AES keys to decrypt game files"""

        if keyformat.lower() not in ['base64', 'hex']:

            await ctx.send(embed=discord.Embed(
                description = f'Key format must be `base64` or `hex`. Example: `{ctx.prefix}aes base64`',
                color = discord.Colour.red()
            ))
            return

        else:

            data = await util.fortniteapi.get_aes(keyformat=keyformat)

            if data == False:

                await ctx.send(embed=discord.Embed(
                    description = f'Could not get AES keys right now. Try again later',
                    color = discord.Colour.red()
                ))
                return

            embed = discord.Embed(
                title = f'AES for build {data["data"]["build"]}', 
                description = f'Main key: {data["data"]["mainKey"]}',
                color = discord.Colour.blue()
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
                        title = f'AES for build {data["data"]["build"]}', 
                        description = f'Main key: {data["data"]["mainKey"]}',
                        color = discord.Colour.blue()
                    )
                    count = 0

                embed.add_field(name=key['pakFilename'], value=f'GUID: {key["pakGuid"]}\nKey: {key["key"]}', inline=False)

            if len(pages) == 1:

                await ctx.send(
                    embed = pages[0]
                )
                return

            else:

                components = [[
                    Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                    Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False)
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
                                Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                                Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False)
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
    @commands.cooldown(2, 14, commands.BucketType.user)
    async def stats(self, ctx, *, account_name = None):
        """Search for player stats. Search can be made for Epic, PSN and XBOX accounts"""

        if account_name == None:
            await ctx.send(embed=discord.Embed(
                description = f'Missing parameters! Usage: `{ctx.prefix}stats <account name>`',
                color = discord.Colour.blue()
            ))
            return

        components = [[
            Button(style=ButtonStyle.grey, label='Epic', custom_id='SEARCH_TYPE_EPIC'),
            Button(style=ButtonStyle.blue, label='PlayStation', custom_id='SEARCH_TYPE_PSN'),
            Button(style=ButtonStyle.green, label='Xbox', custom_id='SEARCH_TYPE_XBOX')
        ]]

        msg = await ctx.send(
            embed=discord.Embed(
                description = 'Select the account type to search stats',
                color = discord.Colour.blue()
            ),
            components=components
        )

        def check(interaction):
            return interaction.author == ctx.author and interaction.message == msg

        try:

            interaction = await self.bot.wait_for('button_click', check=check, timeout=180)

            if interaction.custom_id == 'SEARCH_TYPE_EPIC':
                data = await util.fortniteapi.get_stats(account_name=account_name, account_type='epic')
            
            elif interaction.custom_id == 'SEARCH_TYPE_PSN':
                data = await util.fortniteapi.get_stats(account_name=account_name, account_type='psn')

            elif interaction.custom_id == 'SEARCH_TYPE_XBOX':
                data = await util.fortniteapi.get_stats(account_name=account_name, account_type='xbl')

            
            if data['status'] == 404:

                embed = discord.Embed(
                    description = 'There is no stats for this account or it does not exists.',
                    color = discord.Colour.red()
                )
                await interaction.respond(
                    type = 7,
                    embed = embed,
                    components = []
                )
                return

            elif data['status'] == 403:

                embed = discord.Embed(
                    description = 'Sorry but the stats of this account are private.',
                    color = discord.Colour.red()
                )
                await interaction.respond(
                    type = 7,
                    embed = embed,
                    components = []
                )
                return

            elif data['status'] == 200:

                embed = discord.Embed(
                    title = f'{data["data"]["account"]["name"]} stats',
                    color = discord.Colour.blue()
                )
                embed.set_image(url=f'{data["data"]["image"]}?cache={time.time()}')
                embed.set_footer(text=f'Level {data["data"]["battlePass"]["level"]} • Account ID {data["data"]["account"]["id"]}')

                await interaction.respond(
                    type = 7,
                    embed = embed,
                    components = []
                )


        except asyncio.TimeoutError:

            await msg.edit(embed=discord.Embed(
                description = 'Search canceled by timeout.',
                color = discord.Colour.red()
            ), components=[])


    @commands.command(usage='code <creator code>', aliases=['creatorcode', 'cc'])
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def code(self, ctx, *, creator_code = None):
        """Shows info about a creator code"""

        if creator_code == None:

            await ctx.send(embed=discord.Embed(
                description = f'Missing parameters! Usage: `{ctx.prefix}code <creator code>`',
                color = discord.Colour.red()
            ))
            return

        else:

            data = await util.fortniteapi.get_cc(code=creator_code)

            if data == False:

                await ctx.send(embed=discord.Embed(
                    description = 'No creator code found.',
                    color = discord.Colour.red()
                ))
                return

            else:

                embed = discord.Embed(
                    title = 'Creator code search',
                    color = discord.Colour.blue()
                )

                embed.add_field(name='Code', value=f'`{data["data"]["code"]}`')
                embed.add_field(name='Account', value=f'`{data["data"]["account"]["name"]}`')
                embed.add_field(name='Status', value=f'`{data["data"]["status"]}`')

                embed.set_footer(text=f'Account id {data["data"]["account"]["id"]}')

                await ctx.send(embed=embed)
                

    @commands.command(usage='upcoming', aliases=['leaked'])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def upcoming(self, ctx):
        """Shows an interactive message with all the new/upcoming cosmetics"""

        data = await util.fortniteapi.get_new_items()

        if data == False:

            await ctx.send(embed=discord.Embed(
                description = 'Could not get upcoming items right now. Try again later',
                color = discord.Colour.red()
            ))
            return

        else:

            pages = []
            current_page = 0

            count = 0

            for cosmetic in data['data']['items']:

                count += 1

                i = discord.Embed(
                    title = f'Upcoming cosmetics',
                    description = f'Upcoming cosmetics of build {data["data"]["build"]}',
                    color = util.get_color_by_rarity(cosmetic['rarity']['value'])
                )

                i.add_field(name='Name', value=f'`{cosmetic["name"]}`', inline=False)
                i.add_field(name='Description', value=f'`{cosmetic["description"]}`', inline=False)
                i.add_field(name='ID', value=f'`{cosmetic["id"]}`', inline=False)
                i.add_field(name='Rarity', value=f'`{cosmetic["rarity"]["displayValue"]}`', inline=False)
                i.add_field(name='Set', value=f'`{cosmetic["set"]["text"]}`' if cosmetic['set'] else 'None', inline=False)

                i.set_thumbnail(url=cosmetic['images']['icon'])

                i.set_footer(text=f'Result {count} of {len(data["data"]["items"])}')

                pages.append(i)


            components = []

            if len(pages) > 1:
                components = [[
                    Button(style=ButtonStyle.blue, label='<<', custom_id='PAGE_TO_FIRST', disabled=True if current_page < 1 else False),
                    Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                    Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
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
                            Button(style=ButtonStyle.blue, label='Back', custom_id='PAGE_BACK', disabled=True if current_page < 1 else False),
                            Button(style=ButtonStyle.blue, label='Next', custom_id='PAGE_NEXT', disabled=True if current_page + 1 == len(pages) else False),
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

    
def setup(bot):
    bot.add_cog(General(bot))