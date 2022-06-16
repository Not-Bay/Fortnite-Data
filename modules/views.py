import traceback
import logging
import discord
import io

from modules import util

log = logging.getLogger('FortniteData.modules.components')

###
## Commands components
###

class ReportToDeveloper(discord.ui.Button):
    def __init__(self, lang):
        super().__init__(
            label = util.get_str(lang, 'command_button_report_error_to_developer'),
            style = discord.ButtonStyle.gray
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        user_id = str(interaction.user.id)

        try:
            cached_error = util.error_cache[user_id]

            embed = discord.Embed(
                title = 'Error reported',
                description = f'Reported by <@{user_id}>',
                color = util.Colors.RED
            )
            file = discord.File(
                fp = io.StringIO(cached_error),
                filename = 'traceback.txt'
            )
            channel = await interaction.client.fetch_channel(util.configuration.get('error_reports_channel'))

            if channel == None:
                log.error('Error report could\'nt be sent. Invalid errors channel id in config')
            
            else:
                await channel.send(
                    embed = embed,
                    file = file
                )
            await interaction.response.send_message(
                embed = discord.Embed(
                    description = util.get_str(self.lang, 'command_string_error_was_reported_correctly'),
                    color = util.Colors.GREEN
                ),
                ephemeral = True
            )
        except KeyError:
            await interaction.response.send_message(
                embed = discord.Embed(
                    description = util.get_str(self.lang, 'command_string_error_can_not_report'),
                    color = util.Colors.RED
                ),
                ephemeral = True
            )

class ShopChannelConfigure(discord.ui.Button):
    def __init__(self, lang: str):
        super().__init__(
            label = util.get_str(lang, 'interaction_button_configure_channel'),
            style = discord.ButtonStyle.gray
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        server = await util.database_get_server(interaction)

        channels = []
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel) and channel.permissions_for(interaction.guild.me).manage_webhooks == True:
                channels.append(channel)

        if len(channels) == 0:
            await interaction.response.edit_message(
                embed = discord.Embed(
                    description = util.get_str(self.lang, 'command_string_there_are_no_channels'),
                    color = util.Colors.RED
                ),
                view = None
            )
            return

        select_options = []
        if server['shop_channel']['enabled'] == True:
            select_options.append(discord.SelectOption(
                label = util.get_str(self.lang, 'interaction_button_disable'),
                description = util.get_str(self.lang, 'command_string_select_this_to_disable'),
                value = 'DISABLE'
            ))
        for channel in channels:
            select_options.append(
                discord.SelectOption(
                    label = '# ' + channel.name,
                    value = str(channel.id)
                )
            )

        await interaction.response.edit_message(
            embed = discord.Embed(
                description = util.get_str(self.lang, 'command_string_select_a_new_channel_description'),
                color = util.Colors.BLURPLE
            ),
            view = discord.ui.View(
                ShopChannelSelect(self.lang, select_options),
                timeout = 120
            )
        )

class ShopChannelSelect(discord.ui.Select):
    def __init__(self, lang: str, options: list):
        super().__init__(
            options = options
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        server = await util.database_get_server(interaction)

        if self.values[0] == 'DISABLE':

            try:
                webhook = await interaction.client.fetch_webhook(server['shop_channel']['webhook_id'])
                await webhook.delete(reason = f'Shop channel disabled by {interaction.user}')

            except discord.NotFound:
                log.debug('Ignoring webhook delete. It doest not exists anymore')
            except discord.errors.Forbidden:

                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_webhook_delete'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
            except:

                log.error(f'An error ocurred removing webhook in shop channel disabling. Traceback: {traceback.format_exc()}')

            change = await util.database_update_server(
                ctx = interaction,
                changes = {
                    '$set': {
                        'shop_channel.enabled': False,
                        'shop_channel.webhook': None,
                        'shop_channel.channel': None,
                        'shop_channel.webhook_id': None
                    }
                }
            )
            await interaction.response.edit_message(
                embed = discord.Embed(
                    description = util.get_str(self.lang, 'interaction_string_channel_disabled'),
                    color = util.Colors.BLUE
                ),
                view = None
            )

        else:
            try:
                channel = await interaction.client.fetch_channel(int(self.values[0]))
            except:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_invalid_channel_or_not_accesible'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
            try:
                webhook = await channel.create_webhook(
                    name = 'Fortnite Data Shop Channel',
                    reason = f'Shop channel configured by {interaction.user}'
                )
            except:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_webhook_create'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
                return
            change = await util.database_update_server(
                ctx = interaction,
                changes = {
                    '$set': {
                        'shop_channel.enabled': True,
                        'shop_channel.webhook': webhook.url,
                        'shop_channel.channel': channel.id,
                        'shop_channel.webhook_id': webhook.id
                    }
                }
            )
            if change != None:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_channel_configured').format(channel = f'<#{channel.id}>'),
                        color = util.Colors.BLUE
                    ),
                    view = None
                )
                return
            else:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_unknown'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
                return

class ShopChannelManage(discord.ui.Button):
    def __init__(self, lang: str):
        super().__init__(
            label = util.get_str(lang, 'interaction_button_configure_options'),
            style = discord.ButtonStyle.gray
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        server = await util.database_get_server(interaction)

        modal_options = []
        for option in ['header', 'subheader', 'footer']:
            modal_options.append(
                discord.ui.InputText(
                    style = discord.InputTextStyle.singleline,
                    label = util.get_str(self.lang, f'interaction_string_shop_option_{option}'),
                    value = server['shop_channel']['config'][option],
                    max_length = 40,
                    required = False
                )
            )
        
        await interaction.response.send_modal(
            modal = ShopChannelOptions(
                lang = self.lang,
                options = modal_options
            )
        )

class ShopChannelOptions(discord.ui.Modal):
    def __init__(self, lang: str, options: list):
        super().__init__(
            title = util.get_str(lang, 'interaction_string_select_to_configure')
        )
        self.lang = lang

        for option in options:
            self.add_item(option)

    async def callback(self, interaction: discord.Interaction):

        changes = await util.database_update_server(
            ctx = interaction,
            changes = {
                '$set': {
                    'shop_channel.config.header': self.children[0].value,
                    'shop_channel.config.subheader': self.children[1].value,
                    'shop_channel.config.footer': self.children[2].value
                }
            }
        )

        server_data = await util.database_get_server(interaction)

        if server_data['shop_channel']['enabled'] == False:
            channel = util.get_str(self.lang, 'command_string_not_configurated')
        else:
            channel = f'<#{server_data["shop_channel"]["channel"]}>'

        options_string = '\n'
        for option in ['header', 'subheader', 'footer']:
            options_string += f'`{option}` - {util.get_str(self.lang, "command_string_not_configurated") if server_data["shop_channel"]["config"][option] == None else server_data["shop_channel"]["config"][option]}\n'

        view = discord.ui.View(
            ShopChannelConfigure(self.lang),
            ShopChannelManage(self.lang),
            timeout = 120
        )
        await interaction.response.edit_message(
            embed = discord.Embed(
                title = util.get_str(self.lang, 'interaction_string_shop_config'),
                description = util.get_str(self.lang, 'command_string_current_channel_and_options').format(
                    channel = channel,
                    options = options_string
                ),
                color = util.Colors.BLURPLE
            ),
            view = view
        )

class UpdatesChannelConfigure(discord.ui.Button):
    def __init__(self, lang: str):
        super().__init__(
            label = util.get_str(lang, 'interaction_button_configure_channel'),
            style = discord.ButtonStyle.gray
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        server = await util.database_get_server(interaction)

        channels = []
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel) and channel.permissions_for(interaction.guild.me).manage_webhooks == True:
                channels.append(channel)

        if len(channels) == 0:
            await interaction.response.edit_message(
                embed = discord.Embed(
                    description = util.get_str(self.lang, 'command_string_there_are_no_channels'),
                    color = util.Colors.RED
                ),
                view = None
            )
            return

        select_options = []
        if server['updates_channel']['enabled'] == True:
            select_options.append(discord.SelectOption(
                label = util.get_str(self.lang, 'interaction_button_disable'),
                description = util.get_str(self.lang, 'command_string_select_this_to_disable'),
                value = 'DISABLE'
            ))
        for channel in channels:
            select_options.append(
                discord.SelectOption(
                    label = '# ' + channel.name,
                    value = str(channel.id)
                )
            )

        await interaction.response.edit_message(
            embed = discord.Embed(
                description = util.get_str(self.lang, 'command_string_select_a_new_channel_description'),
                color = util.Colors.BLURPLE
            ),
            view = discord.ui.View(
                UpdatesChannelSelect(self.lang, select_options),
                timeout = 120
            )
        )

class UpdatesChannelSelect(discord.ui.Select):
    def __init__(self, lang: str, options: list):
        super().__init__(
            options = options
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        server = await util.database_get_server(interaction)

        if self.values[0] == 'DISABLE':

            try:
                webhook = await interaction.client.fetch_webhook(server['updates_channel']['webhook_id'])
                await webhook.delete(reason = f'Updates channel disabled by {interaction.user}')

            except discord.NotFound:
                log.debug('Ignoring webhook delete. It doest not exists anymore')
            except discord.errors.Forbidden:

                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_webhook_delete'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
            except:

                log.error(f'An error ocurred removing webhook in updates channel disabling. Traceback: {traceback.format_exc()}')

            change = await util.database_update_server(
                ctx = interaction,
                changes = {
                    '$set': {
                        'updates_channel.enabled': False,
                        'updates_channel.webhook': None,
                        'updates_channel.channel': None,
                        'updates_channel.webhook_id': None
                    }
                }
            )
            await interaction.response.edit_message(
                embed = discord.Embed(
                    description = util.get_str(self.lang, 'interaction_string_channel_disabled'),
                    color = util.Colors.BLUE
                ),
                view = None
            )

        else:
            try:
                channel = await interaction.client.fetch_channel(int(self.values[0]))
            except:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_invalid_channel_or_not_accesible'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
            try:
                webhook = await channel.create_webhook(
                    name = 'Fortnite Data Updates Channel',
                    reason = f'Updates channel configured by {interaction.user}'
                )
            except:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_webhook_create'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
                return
            change = await util.database_update_server(
                ctx = interaction,
                changes = {
                    '$set': {
                        'updates_channel.enabled': True,
                        'updates_channel.webhook': webhook.url,
                        'updates_channel.channel': channel.id,
                        'updates_channel.webhook_id': webhook.id
                    }
                }
            )
            if change != None:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_channel_configured').format(channel = f'<#{channel.id}>'),
                        color = util.Colors.BLUE
                    ),
                    view = None
                )
                return
            else:
                await interaction.response.edit_message(
                    embed = discord.Embed(
                        description = util.get_str(self.lang, 'interaction_string_error_unknown'),
                        color = util.Colors.RED
                    ),
                    view = None
                )
                return

class UpdatesChannelManage(discord.ui.Button):
    def __init__(self, lang: str):
        super().__init__(
            label = util.get_str(lang, 'interaction_button_configure_options'),
            style = discord.ButtonStyle.gray
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        server = await util.database_get_server(interaction)

        enabled = interaction.client.get_emoji(931338312159989781)
        disabled = interaction.client.get_emoji(931338312604602450)
        
        options_string = ''
        select_options = []
        for option in ['shopsections', 'cosmetics', 'playlists', 'news', 'aes']:

            select_options.append(
                discord.SelectOption(
                    label = util.get_str(self.lang, f'interaction_string_updates_option_{option}'),
                    description = util.get_str(self.lang, f'interaction_string_updates_option_{option}_description'),
                    emoji = enabled if server['updates_channel']['config'][option] == True else disabled,
                    value = option
                )
            )

            options_string += f'`{util.get_str(self.lang, f"interaction_string_updates_option_{option}")}` - {util.get_str(self.lang, "command_string_configured") if server["updates_channel"]["config"][option] == True else util.get_str(self.lang, "command_string_disabled")}\n'

        await interaction.response.edit_message(
            embed = discord.Embed(
                title = util.get_str(self.lang, 'interaction_string_updates_config'),
                description = f"{util.get_str(self.lang, 'interaction_string_select_to_disable_or_enable')}\n{options_string}",
                color = util.Colors.BLUE
            ),
            view = discord.ui.View(
                UpdatesChannelManageSelect(lang = self.lang, options = select_options),
                timeout = 120
            )
        )

class UpdatesChannelManageSelect(discord.ui.Select):
    def __init__(self, lang: str, options: list):
        super().__init__(
            options = options
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):

        server = await util.database_get_server(interaction)

        if server['updates_channel']['config'][self.values[0]] == True:
            change = await util.database_update_server(
                ctx = interaction,
                changes = {
                    '$set': {
                        f'updates_channel.config.{self.values[0]}': False
                    }
                }
            )
        
        else:
            change = await util.database_update_server(
                ctx = interaction,
                changes = {
                    '$set': {
                        f'updates_channel.config.{self.values[0]}': True
                    }
                }
            )

        server = await util.database_get_server(interaction)

        enabled = interaction.client.get_emoji(931338312159989781)
        disabled = interaction.client.get_emoji(931338312604602450)
        
        options_string = ''
        select_options = []
        for option in ['shopsections', 'cosmetics', 'playlists', 'news', 'aes']:

            select_options.append(
                discord.SelectOption(
                    label = util.get_str(self.lang, f'interaction_string_updates_option_{option}'),
                    description = util.get_str(self.lang, f'interaction_string_updates_option_{option}_description'),
                    emoji = enabled if server['updates_channel']['config'][option] == True else disabled,
                    value = option
                )
            )

            options_string += f'`{util.get_str(self.lang, f"interaction_string_updates_option_{option}")}` - {util.get_str(self.lang, "command_string_configured") if server["updates_channel"]["config"][option] == True else util.get_str(self.lang, "command_string_disabled")}\n'

        await interaction.response.edit_message(
            embed = discord.Embed(
                title = util.get_str(self.lang, 'interaction_string_updates_config'),
                description = f"{util.get_str(self.lang, 'interaction_string_select_to_disable_or_enable')}\n{options_string}",
                color = util.Colors.BLUE
            ),
            view = discord.ui.View(
                UpdatesChannelManageSelect(lang = self.lang, options = select_options),
                timeout = 120
            )
        )

###
## General components
###

class LinkButton(discord.ui.View):
    def __init__(self, label: str, url: str):
        super().__init__()

        self.add_item(
            discord.ui.Button(
                label = label,
                url = url
            )
        )

# Autocompletes

async def autocomplete_search_language(ctx: discord.AutocompleteContext):

    languages = ['ar', 'de', 'en', 'es', 'es-419', 'fr', 'it', 'ja', 'ko', 'pl', 'pt-BR', 'ru', 'tr']
    results = []

    for i in languages:

        if ctx.value.lower() in i:
            results.append(i)

    return results