from discord.ext import commands
from discord_components import *
import traceback
import asyncio
import discord
import logging
import datetime
import io

import util

log = logging.getLogger('FortniteData.cogs.events')

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        lang = util.get_guild_lang(ctx.guild)

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.CommandOnCooldown):

            end_seconds = int(str(error.retry_after)[0]) + 1

            embed = discord.Embed(
                description = util.get_str(lang, 'command_string_on_cooldown'),
                color = discord.Colour.orange()
            )
            embed.set_footer(text=util.get_str(lang, 'command_string_on_cooldown_retry_after').format(seconds = end_seconds))
            
            await ctx.send(
                embed=embed
            )
            return

        elif isinstance(error, commands.DisabledCommand):

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_disabled_command'),
                description = util.get_str(lang, 'command_string_disabled_command_description'),
                color = discord.Colour.red()
            )
            embed.set_footer(text=util.get_str(lang, 'command_string_disabled_command_footer'))

            await ctx.send(
                embed = embed
            )
            return

        else:

            traceback_str = ''.join(traceback.format_exception(None, error, error.__traceback__))

            util.error_cache[str(ctx.author.id)] = {} # save error to a temporary cache
            util.error_cache[str(ctx.author.id)][str(ctx.message.id)] = traceback_str

            description = util.get_str(lang, 'command_string_an_unknown_error_ocurred').format(traceback = traceback_str)

            if len(description) > 4096:
                description = util.get_Str(lang, 'command_string_an_unknown_error_ocurred'.format(traceback = error))

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_an_error_ocurred'),
                description = util.get_str(lang, 'command_string_an_unknown_error_ocurred').format(traceback = traceback_str),
                color = discord.Colour.red()
            )
            components = [
                Button(
                    style=ButtonStyle.red,
                    label=util.get_str(lang, 'command_button_report_error_to_developer'),
                    custom_id=f'REPORTED_ERROR_{ctx.author.id}_{ctx.message.id}'
                )
            ]

            await ctx.send(
                embed = embed,
                components = components
            )


    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        util.database_store_server(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        util.database_remove_server(guild)


    @commands.Cog.listener()
    async def on_button_click(self, interaction: Interaction):

        lang = util.get_guild_lang(interaction.guild)

        if interaction.custom_id == 'SERVER_PREFIX_CONFIGURE':

            if interaction.author.guild_permissions.administrator == False:
                return

            def message_check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            def interaction_check(i):
                return interaction.author == i.author and interaction.message == i.message

            server = util.database_get_server(interaction.guild)
            
            msg = await interaction.respond(
                type = 7,
                embed = discord.Embed(
                    description = util.get_str(lang, 'interaction_string_send_new_prefix'),
                    color = discord.Colour.blue()
                ),
                components = [
                    Button(
                        style = ButtonStyle.gray,
                        label = util.get_str(lang, 'interaction_button_cancel'),
                        custom_id = 'CANCEL'
                    )
                ]
            )

            try:

                pending_tasks = [
                    self.bot.wait_for('message', check=message_check, timeout=120),
                    self.bot.wait_for('button_click', check=interaction_check, timeout=120)
                ]

                done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when = asyncio.FIRST_COMPLETED)

                for task in pending_tasks:
                    task.cancel()

                finished_task = list(done_tasks)[0].result()

                if isinstance(finished_task, Interaction):

                    await finished_task.respond(
                        type = 7,
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_canceled_by_user'),
                            color = discord.Colour.red()
                        ),
                        components = []
                    )

                else:

                    user_msg = finished_task

                    if len(user_msg.content) > 4:

                        await interaction.message.edit(
                            embed = discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_new_prefix_too_long'),
                                color = discord.Colour.red()
                            )
                        )
                        return

                    else:

                        new_prefix = user_msg.content

                        if new_prefix == server['prefix']:

                            await interaction.message.edit(
                                embed = discord.Embed(
                                    description = util.get_str(lang, 'interaction_string_error_new_prefix_duplicate'),
                                    color = discord.Colour.red()
                                )
                            )
                            return

                        else:

                            change = util.database_update_server(interaction.guild, {'$set': {'prefix': new_prefix}})

                            await interaction.message.edit(
                                embed = discord.Embed(
                                    description = util.get_str(lang, 'interaction_string_changed_prefix').format(prefix = new_prefix),
                                    color = discord.Colour.green()
                                )
                            )
                            return

            except asyncio.TimeoutError:

                await interaction.message.edit(
                    embed = discord.Embed(
                        description = util.get_str(lang, 'interaction_string_canceled_by_timeout'),
                        color = discord.Colour.red()
                    )
                )
                return

        elif interaction.custom_id == 'SERVER_LANG_CONFIGURE':

            if interaction.author.guild_permissions.administrator == False:
                return

            def check(i):
                return interaction.author == i.author and interaction.message == i.message

            server = util.database_get_server(interaction.guild)

            components = [[
                Button(style=ButtonStyle.green if server['language'] == 'en' else ButtonStyle.gray, label='English', disabled=True if server['language'] == 'en' else False, custom_id='SERVER_LANG_OPTION_EN'),
                Button(style=ButtonStyle.green if server['language'] == 'es' else ButtonStyle.gray, label='Español', disabled=True if server['language'] == 'es' else False, custom_id='SERVER_LANG_OPTION_ES'),
                Button(style=ButtonStyle.green if server['language'] == 'ja' else ButtonStyle.gray, label='日本語', disabled=True if server['language'] == 'ja' else False, custom_id='SERVER_LANG_OPTION_JA')
            ]]

            msg = await interaction.respond(
                type = 7,
                embed = discord.Embed(
                    description = util.get_str(lang, 'interaction_string_select_language'),
                    color = discord.Colour.blue()
                ),
                components = components
            )

            try:

                i = await self.bot.wait_for('button_click', check=check, timeout=120)

                if i.custom_id == 'SERVER_LANG_OPTION_EN':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'en'}})

                    await i.respond(
                        type = 7,
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_language_changed_to').format(lang = 'English'),
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

                elif i.custom_id == 'SERVER_LANG_OPTION_ES':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'es'}})

                    await i.respond(
                        type = 7,
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_language_changed_to').format(lang = 'Español'),
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

                elif i.custom_id == 'SERVER_LANG_OPTION_JA':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'ja'}})

                    await i.respond(
                        type = 7,
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_language_changed_to').format(lang = '日本語'),
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

            except asyncio.TimeoutError:

                await msg.edit(embed=discord.Embed(
                    description = util.get_str(lang, 'interaction_string_canceled_by_timeout'),
                    color = discord.Colour.blue()
                ))

        elif interaction.custom_id == 'SERVER_SHOP_CHANNEL_CONFIGURE':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)
            already_configurated = server['shop_channel']['enabled']

            components = [
                Button(
                    style = ButtonStyle.red,
                    label = util.get_str(lang, 'interaction_button_configure_channel'),
                    custom_id = 'SERVER_SHOP_CHANNEL_CONFIGURE_CHANNEL'
                ),
                Button(
                    style = ButtonStyle.gray,
                    label = util.get_str(lang, 'interaction_button_configure_options'),
                    custom_id = 'SERVER_SHOP_CHANNEL_CONFIGURE_OPTIONS'
                )
            ]

            embed = discord.Embed(
                title = util.get_str(lang, 'interaction_string_shop_config'),
                color = discord.Colour.blue()
            )
            embed.add_field(
                name = util.get_str(lang, 'interaction_string_channel'),
                value = f'<#{server["shop_channel"]["channel"]}>' if already_configurated else util.get_str(lang, 'command_string_not_configurated'),
                inline = False
            )

            options_string = ''
            for i in ['header', 'subheader', 'footer']:
                options_string += f'`{i}` - {util.get_str(lang, "command_string_not_configurated") if server["shop_channel"]["config"][i] == None else server["shop_channel"]["config"][i]}\n'

            embed.add_field(
                name = util.get_str(lang, 'interaction_string_updates_options'),
                value = options_string,
                inline = False
            )

            await interaction.respond(
                type = 7,
                embed = embed,
                components = components
            )

        elif interaction.custom_id == 'SERVER_UPDATES_CHANNEL_CONFIGURE':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)
            already_configurated = server['updates_channel']['enabled']

            components = [
                Button(
                    style = ButtonStyle.red,
                    label = util.get_str(lang, 'interaction_button_configure_channel'),
                    custom_id = 'SERVER_UPDATES_CHANNEL_CONFIGURE_CHANNEL'
                ),
                Button(
                    style = ButtonStyle.gray,
                    label = util.get_str(lang, 'interaction_button_configure_options'),
                    custom_id = 'SERVER_UPDATES_CHANNEL_CONFIGURE_OPTIONS'
                )
            ]

            embed = discord.Embed(
                title = util.get_str(lang, 'interaction_string_updates_config'),
                color = discord.Colour.blue()
            )
            embed.add_field(
                name = util.get_str(lang, 'interaction_string_channel'),
                value = f'<#{server["updates_channel"]["channel"]}>' if already_configurated else util.get_str(lang, 'command_string_not_configurated'),
                inline = False
            )

            options_string = ''
            for i in ['cosmetics', 'playlists', 'news', 'aes']:
                options_string += f'`{i}` - {util.get_str(lang, "command_string_configured") if server["updates_channel"]["config"][i] == True else util.get_str(lang, "command_string_disabled")}\n'

            embed.add_field(
                name = util.get_str(lang, 'interaction_string_updates_options'),
                value = options_string,
                inline = False
            )

            await interaction.respond(
                type = 7,
                embed = embed,
                components = components
            )


        elif interaction.custom_id == 'SERVER_UPDATES_CHANNEL_CONFIGURE_OPTIONS':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)

            enabled = self.bot.get_emoji(931338312159989781)
            disabled = self.bot.get_emoji(931338312604602450)

            options_string = ''
            for op in ['cosmetics', 'playlists', 'news', 'aes']:
                options_string += f'`{util.get_str(lang, f"interaction_string_updates_option_{op}")}` - {util.get_str(lang, "command_string_disabled") if server["updates_channel"]["config"][op] == True else util.get_str(lang, "command_string_disabled")}\n'

            embed = discord.Embed(
                title = util.get_str(lang, 'interaction_string_updates_config'),
                description = f'{util.get_str(lang, "interaction_string_select_to_disable_or_enable")}\n{options_string}',
                color = discord.Colour.blue()
            )

            components = [
                Select(
                    options = [
                        SelectOption(emoji = enabled if server['updates_channel']['config'][i] == True else disabled, label = util.get_str(lang, f'interaction_string_updates_option_{i}'), description = util.get_str(lang, f'interaction_string_updates_option_{i}_description'), value = i ) for i in ['cosmetics', 'playlists', 'news', 'aes']
                    ],
                    custom_id = 'SERVER_UPDATES_SELECT_OPTION'
                )
            ]

            await interaction.respond(
                type = 7,
                embed = embed,
                components = components
            )

            def check(i):
                return interaction.author == i.author and interaction.message == i.message

            while True:

                try:

                    i = await self.bot.wait_for('select_option', check=check, timeout=90)

                    if server['updates_channel']['config'][i.values[0]] == True:

                        change = util.database_update_server(
                            guild = interaction.guild,
                            changes = {'$set': {f'updates_channel.config.{i.values[0]}': False}}
                        )

                    else:

                        change = util.database_update_server(
                            guild = interaction.guild,
                            changes = {'$set': {f'updates_channel.config.{i.values[0]}': True}}
                        )

                    server = util.database_get_server(interaction.guild)

                    options_string = ''
                    for op in ['cosmetics', 'playlists', 'news', 'aes']:
                        options_string += f'`{util.get_str(lang, f"interaction_string_updates_option_{op}")}` - {util.get_str(lang, "command_string_configured") if server["updates_channel"]["config"][op] == True else util.get_str(lang, "command_string_disabled")}\n'

                    embed = discord.Embed(
                        title = util.get_str(lang, 'interaction_string_updates_config'),
                        description = f'{util.get_str(lang, "interaction_string_select_to_disable_or_enable")}\n{options_string}',
                        color = discord.Colour.blue()
                    )

                    components = [
                        Select(
                            options = [
                                SelectOption(emoji = enabled if server['updates_channel']['config'][i] == True else disabled, label = util.get_str(lang, f'interaction_string_updates_option_{i}'), description = util.get_str(lang, f'interaction_string_updates_option_{i}_description'), value = i ) for i in ['cosmetics', 'playlists', 'news', 'aes']
                            ],
                            custom_id = 'SERVER_UPDATES_SELECT_OPTION'
                        )
                    ]

                    await i.respond(
                        type = 7,
                        embed = embed,
                        components = components
                    )

                except asyncio.TimeoutError:

                    components[0].disabled = True

                    await interaction.message.edit(
                        embed = embed,
                        components = components
                    )
                    break

        elif interaction.custom_id == 'SERVER_SHOP_CHANNEL_CONFIGURE_CHANNEL':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)
            already_configurated = server['shop_channel']['enabled']

            embed = discord.Embed(
                description = util.get_str(lang, 'interaction_string_send_channel'),
                color = discord.Colour.blue()
            )

            components = [
                Button(
                    style = ButtonStyle.gray,
                    label = util.get_str(lang, 'interaction_button_cancel'),
                    custom_id = 'CANCEL'
                )
            ]

            if already_configurated:
                components.append(
                    Button(
                        style = ButtonStyle.red,
                        label = util.get_str(lang, 'interaction_button_disable'),
                        custom_id = 'SERVER_SHOP_DISABLE'
                    )
                )

            await interaction.respond(
                type = 7,
                embed = embed,
                components = [
                    components
                ]
            )

            def message_check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            def interaction_check(i):
                return interaction.author == i.author and interaction.message == i.message

            try:

                pending_tasks = [
                    self.bot.wait_for('message', check=message_check),
                    self.bot.wait_for('button_click', check=interaction_check)
                ]

                done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when = asyncio.FIRST_COMPLETED, timeout=120)

                for task in pending_tasks:
                    task.cancel()

                finished_task = list(done_tasks)[0].result()

                if isinstance(finished_task, Interaction):

                    return

                else:

                    usrmsg = finished_task
                    channel_id = usrmsg.content.lower().strip('<#> ')

                    try:
                        channel_int = int(channel_id)
                        channel = await self.bot.fetch_channel(channel_int)
                    except:

                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_send_channel_only'),
                            color = discord.Colour.red(),
                            components = []
                        ))
                        return

                    if channel == None:

                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_error_invalid_channel_or_not_accesible'),
                            color = discord.Colour.red(),
                            components = []
                        ))
                        return
                    
                    else:

                        try: #create webhook

                            webhook = await channel.create_webhook(name='Fortnite Data Shop Channel', reason=f'Shop channel configured by {interaction.author}')

                        except:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_webhook_create'),
                                color = discord.Colour.red(),
                                components = []
                            ))
                            return
                            
                        change = util.database_update_server(interaction.guild, {'$set': {'shop_channel.enabled': True, 'shop_channel.webhook': webhook.url, 'shop_channel.channel': channel.id, 'shop_channel.webhook_id': webhook.id}})

                        if change != None:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_channel_configured').format(channel = f'<#{channel.id}>'),
                                color = discord.Colour.blue(),
                                components = []
                            ))
                            return
                        
                        else:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_unknown'),
                                color = discord.Colour.red(),
                                components = []
                            ))
                            return


            except asyncio.TimeoutError:

                await interaction.message.edit(embed=discord.Embed(
                    description = util.get_str(lang, 'interaction_string_canceled_by_timeout'),
                    color = discord.Colour.red(),
                    components = []
                ))
                return

        elif interaction.custom_id == 'SERVER_SHOP_CHANNEL_CONFIGURE_OPTIONS':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)
            
            enabled = self.bot.get_emoji(931338312159989781)
            disabled = self.bot.get_emoji(931338312604602450)

            options_string = ''
            for op in ['header', 'subheader', 'footer']:
                options_string += f'`{util.get_str(lang, f"interaction_string_shop_option_{op}")}` - {util.get_str(lang, "command_string_disabled") if server["shop_channel"]["config"][op] == None else server["shop_channel"]["config"][op]}\n'

            embed = discord.Embed(
                title = util.get_str(lang, 'interaction_string_shop_config'),
                description = f'{util.get_str(lang, "interaction_string_select_to_configure")}\n{options_string}',
                color = discord.Colour.blue()
            )

            components = [
                Select(
                    options = [
                        SelectOption(emoji = enabled if server['shop_channel']['config'][i] != None else disabled, label = util.get_str(lang, f'interaction_string_shop_option_{i}'), description = util.get_str(lang, f'interaction_string_shop_option_{i}_description'), value = i) for i in ['header', 'subheader', 'footer']
                    ],
                    custom_id = 'SERVER_SHOP_SELECT_OPTION'
                )
            ]

            await interaction.respond(
                type = 7,
                embed = embed,
                components = components
            )

            def check(i):
                return interaction.author == i.author and interaction.message == i.message
            
            def message_check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            while True:

                try:

                    i = await self.bot.wait_for('select_option', check=check, timeout=90)

                    optionComponents = [
                        Button(
                            style = ButtonStyle.blue,
                            label = util.get_str(lang, 'command_button_back'),
                            custom_id = 'GO_BACK'
                        ),
                        Button(
                            style = ButtonStyle.gray,
                            label = util.get_str(lang, 'interaction_button_disable'),
                            custom_id = 'OPTION_CLEAR'
                        )
                    ]

                    optionEmbed = discord.Embed(
                        title = util.get_str(lang, f'interaction_string_shop_option_{i.values[0]}'),
                        description = f'{util.get_str(lang, f"interaction_string_current_value").format(value=server["shop_channel"]["config"][i.values[0]])}\n{util.get_str(lang, "interaction_string_send_the_new_value")}'
                    )

                    await i.respond(
                        type = 7,
                        embed = optionEmbed,
                        components = optionComponents
                    )

                    try:
                        pending_tasks = [
                            self.bot.wait_for('message', check=message_check),
                            self.bot.wait_for('button_click', check=check)
                        ]

                        done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when = asyncio.FIRST_COMPLETED, timeout=120)

                        for task in pending_tasks:
                            task.cancel()

                        finished_task = list(done_tasks)[0].result()

                        if isinstance(finished_task, Interaction):

                            if finished_task.custom_id == 'GO_BACK':

                                await finished_task.respond(
                                    type = 7,
                                    embed = embed,
                                    components = components
                                )
                                continue

                            elif finished_task.custom_id == 'OPTION_CLEAR':

                                change = util.database_update_server(
                                    guild = interaction.guild,
                                    changes = {'$set': {f'shop_channel.config.{i.values[0]}': None}}
                                )

                                server = util.database_get_server(interaction.guild)

                                options_string = ''
                                for op in ['header', 'subheader', 'footer']:
                                    options_string += f'`{util.get_str(lang, f"interaction_string_shop_option_{op}")}` - {util.get_str(lang, "command_string_disabled") if server["shop_channel"]["config"][op] == None else server["shop_channel"]["config"][op]}\n'
                                
                                embed.description = f'{util.get_str(lang, "interaction_string_select_to_configure")}\n{options_string}'

                                await interaction.message.edit(
                                    embed = embed,
                                    components = [
                                        Select(
                                            options = [
                                                SelectOption(emoji = enabled if server['shop_channel']['config'][i] != None else disabled, label = util.get_str(lang, f'interaction_string_shop_option_{i}'), description = util.get_str(lang, f'interaction_string_shop_option_{i}_description'), value = i) for i in ['header', 'subheader', 'footer']
                                            ],
                                            custom_id = 'SERVER_SHOP_SELECT_OPTION'
                                        )
                                    ]
                                )
                                continue
                        
                        else:

                            new_value = finished_task.content

                            change = util.database_update_server(
                                guild = interaction.guild,
                                changes = {'$set': {f'shop_channel.config.{i.values[0]}': new_value}}
                            )

                            server = util.database_get_server(interaction.guild)

                            options_string = ''
                            for op in ['header', 'subheader', 'footer']:
                                options_string += f'`{util.get_str(lang, f"interaction_string_shop_option_{op}")}` - {util.get_str(lang, "command_string_disabled") if server["shop_channel"]["config"][op] == None else server["shop_channel"]["config"][op]}\n'
                            
                            embed.description = f'{util.get_str(lang, "interaction_string_select_to_configure")}\n{options_string}'

                            await interaction.message.edit( # go back to select
                                embed = embed,
                                components = [
                                    Select(
                                        options = [
                                            SelectOption(emoji = enabled if server['shop_channel']['config'][i] != None else disabled, label = util.get_str(lang, f'interaction_string_shop_option_{i}'), description = util.get_str(lang, f'interaction_string_shop_option_{i}_description'), value = i) for i in ['header', 'subheader', 'footer']
                                        ],
                                        custom_id = 'SERVER_SHOP_SELECT_OPTION'
                                    )
                                ]
                            )
                            continue


                    except asyncio.TimeoutError: # another timeout handler for the new value prompt only

                        await interaction.message.edit(
                            embed = embed,
                            components = components
                        )
                        break


                except asyncio.TimeoutError:

                    components[0].disabled = True

                    await interaction.message.edit(
                        embed = embed,
                        components = components
                    )
                    break

        elif interaction.custom_id == 'SERVER_UPDATES_CHANNEL_CONFIGURE_CHANNEL':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)
            already_configurated = server['updates_channel']['enabled']

            embed = discord.Embed(
                description = util.get_str(lang, 'interaction_string_send_channel'),
                color = discord.Colour.blue()
            )

            components = [
                Button(
                    style = ButtonStyle.gray,
                    label = util.get_str(lang, 'interaction_button_cancel'),
                    custom_id = 'CANCEL'
                )
            ]

            if already_configurated:
                components.append(
                    Button(
                        style = ButtonStyle.red,
                        label = util.get_str(lang, 'interaction_button_disable'),
                        custom_id = 'SERVER_UPDATES_DISABLE'
                    )
                )

            msg = await interaction.respond(
                type = 7,
                embed = embed,
                components = [
                    components
                ]
            )

            def message_check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            def interaction_check(i):
                return interaction.author == i.author and interaction.message == i.message

            try:

                pending_tasks = [
                    self.bot.wait_for('message', check=message_check),
                    self.bot.wait_for('button_click', check=interaction_check)
                ]

                done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when = asyncio.FIRST_COMPLETED, timeout = 120)

                for task in pending_tasks:
                    task.cancel()

                finished_task = list(done_tasks)[0].result()

                if isinstance(finished_task, Interaction):

                    return

                else:

                    usrmsg = finished_task
                    channel_id = usrmsg.content.lower().strip('<#> ')

                    try:
                        channel_int = int(channel_id)
                        channel = await self.bot.fetch_channel(channel_int)
                    except:

                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_send_channel_only'),
                            color = discord.Colour.red(),
                            components = []
                        ))
                        return

                    if channel == None:

                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_error_invalid_channel_or_not_accesible'),
                            color = discord.Colour.red(),
                            components = []
                        ))
                        return
                    
                    else:

                        try: #create webhook

                            webhook = await channel.create_webhook(name='Fortnite Data Updates Channel', reason=f'Updates channel configured by {interaction.author}')

                        except:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_webhook_create'),
                                color = discord.Colour.red(),
                                components = []
                            ))
                            return
                            
                        change = util.database_update_server(interaction.guild, {'$set': {'updates_channel.enabled': True, 'updates_channel.webhook': webhook.url, 'updates_channel.channel': channel.id, 'updates_channel.webhook_id': webhook.id}})

                        if change != None:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_channel_configured').format(channel = f'<#{channel.id}>'),
                                color = discord.Colour.blue(),
                                components = []
                            ))
                            return
                        
                        else:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_unknown'),
                                color = discord.Colour.red(),
                                components = []
                            ))
                            return

            except asyncio.TimeoutError:

                await interaction.message.edit(embed=discord.Embed(
                    description = util.get_str(lang, 'interaction_string_canceled_by_timeout'),
                    color = discord.Colour.red(),
                    components = []
                ))
                return
        
        elif interaction.custom_id == 'SERVER_UPDATES_DISABLE':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)

            try:
                webhook = await self.bot.fetch_webhook(server['updates_channel']['webhook_id'])
                await webhook.delete()
            except discord.NotFound:
                log.debug('Ignoring webhook delete. It does not exists anymore')

            except discord.Forbidden:

                await interaction.message.edit(embed=discord.Embed(
                    description = util.get_str(lang, 'interaction_string_error_webhook_delete'),
                    color = discord.Colour.red()
                ))
                return

            except Exception:

                log.error(f'An error ocurred removing webhook in updates channel disabling. Traceback: {traceback.format_exc()}')


            change = util.database_update_server(interaction.guild, {'$set': {'updates_channel.enabled': False, 'updates_channel.webhook': None, 'updates_channel.channel': None, 'updates_channel.webhook_id': None}})

            await interaction.message.edit(embed=discord.Embed(
                description = util.get_str(lang, 'interaction_string_channel_disabled'),
                color = discord.Colour.blue()
            ))
            return

        elif interaction.custom_id == 'SERVER_SHOP_DISABLE':

            if interaction.author.guild_permissions.administrator == False:
                return

            server = util.database_get_server(interaction.guild)

            try:
                webhook = await self.bot.fetch_webhook(server['shop_channel']['webhook_id'])
                await webhook.delete()
            except discord.NotFound:
                log.debug('Ignoring webhook delete. It does not exists anymore')

            except discord.Forbidden:

                await interaction.message.edit(embed=discord.Embed(
                    description = util.get_str(lang, 'interaction_string_error_webhook_delete'),
                    color = discord.Colour.red()
                ))
                return

            except Exception:

                log.error(f'An error ocurred removing webhook in shop channel disabling. Traceback: {traceback.format_exc()}')


            change = util.database_update_server(interaction.guild, {'$set': {'shop_channel.enabled': False, 'shop_channel.webhook': None, 'shop_channel.channel': None, 'shop_channel.webhook_id': None}})

            await interaction.message.edit(embed=discord.Embed(
                description = util.get_str(lang, 'interaction_string_channel_disabled'),
                color = discord.Colour.blue()
            ))
            return

        elif interaction.custom_id == 'CANCEL':

            await interaction.respond(
                type = 7,
                embed = discord.Embed(
                    description = util.get_str(lang, 'interaction_string_canceled_by_user'),
                    color = discord.Colour.red()
                ),
                components = []
            )

        elif interaction.custom_id.startswith('REPORTED_ERROR_'): # Button containing the index for a previously cached error

            parsedChannelAndMessage = interaction.custom_id.replace('REPORTED_ERROR_', '').split('_')

            userId = parsedChannelAndMessage[0]
            messageId = parsedChannelAndMessage[1]

            if userId != str(interaction.user.id):
                return

            try:
                error = util.error_cache[userId][messageId]

                embed = discord.Embed(
                    title = 'Error reported',
                    color = discord.Colour.red(),
                    timestamp = datetime.datetime.utcnow()
                )

                embed_description = f'```py\n{error}```'

                if len(embed_description) < 4096:
                    embed.description = embed_description
                    file = None

                else:

                    file = discord.File(
                        fp = io.StringIO(error),
                        filename = 'error.txt'
                    )
                
                channelId = util.configuration.get('error_reports_channel')

                if channelId != None:

                    try:

                        channel = await self.bot.fetch_channel(channelId)
                        await channel.send(
                            embed = embed,
                            file = file
                        )

                        await interaction.respond(
                            type = 4,
                            embed = discord.Embed(
                                description = util.get_str(lang, 'command_string_error_was_reported_correctly')
                            ),
                            ephemeral = True
                        )

                    except:
                        await interaction.respond(
                            type = 4,
                            content = util.get_str(lang, 'command_string_error_can_not_report'),
                            ephemeral = True
                        )


            except KeyError:

                await interaction.respond(
                    type = 4,
                    content = util.get_str(lang, 'command_string_error_unavailable'),
                    ephemeral = True
                )


def setup(bot):
    bot.add_cog(Events(bot))