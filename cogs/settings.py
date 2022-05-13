from discord.commands import Option, OptionChoice, SlashCommandGroup, CommandPermission
from discord.ext import commands
import discord

from modules import util, views

class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    settings = SlashCommandGroup(
        'settings',
        util.get_str('en', 'command_description_settings')
    )

    @settings.command(
        name=util.get_str('en', 'command_name_settings_shop_channel'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_settings_shop_channel'),
            'ja': util.get_str('ja', 'command_name_settings_shop_channel'),
        },
        description=util.get_str('en', 'command_description_settings_shop_channel'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_settings_shop_channel'),
            'ja': util.get_str('ja', 'command_description_settings_shop_channel')
        }
    )
    @commands.cooldown(2, 4)
    async def settings_shop_channel(
        self,
        ctx: discord.ApplicationContext
    ):
        
        lang = util.get_lang(ctx)

        server = util.database_get_server(ctx)

        if server['shop_channel']['enabled'] == False:
            channel = util.get_str(lang, 'command_string_not_configurated')
        else:
            channel = f'<#{server["shop_channel"]["channel"]}>'

        options_string = '\n'
        for option in ['header', 'subheader', 'footer']:
            options_string += f'`{option}` - {util.get_str(lang, "command_string_not_configurated") if server["shop_channel"]["config"][option] == "" else server["shop_channel"]["config"][option]}\n'

        if ctx.author.guild_permissions.administrator == True:
            view = discord.ui.View(
                views.ShopChannelConfigure(lang),
                views.ShopChannelManage(lang),
                timeout = 120
            )
        else:
            view = None

        await ctx.respond(
            embed = discord.Embed(
                title = util.get_str(lang, 'interaction_string_shop_config'),
                description = util.get_str(lang, 'command_string_current_channel_and_options').format(
                    channel = channel,
                    options = options_string
                ),
                color = util.Colors.BLURPLE
            ),
            view = view,
            ephemeral = True
        )

    @settings.command(
        ame=util.get_str('en', 'command_name_settings_updates_channel'),
        name_localizations={
            'es-ES': util.get_str('es', 'command_name_settings_updates_channel'),
            'ja': util.get_str('ja', 'command_name_settings_updates_channel'),
        },
        description=util.get_str('en', 'command_description_settings_updates_channel'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_settings_updates_channel'),
            'ja': util.get_str('ja', 'command_description_settings_updates_channel')
        }
    )
    @commands.cooldown(2, 4)
    async def settings_updates_channel(
        self,
        ctx: discord.ApplicationContext
    ):
        
        lang = util.get_lang(ctx)

        server = util.database_get_server(ctx)

        if server['updates_channel']['enabled'] == False:
            channel = util.get_str(lang, 'command_string_not_configurated')
        else:
            channel = f'<#{server["updates_channel"]["channel"]}>'

        options_string = '\n'
        for option in ['shopsections', 'cosmetics', 'playlists', 'news', 'aes']:
            options_string += f'`{util.get_str(lang, f"interaction_string_updates_option_{option}")}` - {util.get_str(lang, "command_string_disabled") if server["updates_channel"]["config"][option] == False else util.get_str(lang, "command_string_configured")}\n'

        if ctx.author.guild_permissions.administrator == True:
            view = discord.ui.View(
                views.UpdatesChannelConfigure(lang),
                views.UpdatesChannelManage(lang),
                timeout = 120
            )
        else:
            view = None

        await ctx.respond(
            embed = discord.Embed(
                title = util.get_str(lang, 'interaction_string_updates_config'),
                description = util.get_str(lang, 'command_string_current_channel_and_options').format(
                    channel = channel,
                    options = options_string
                ),
                color = util.Colors.BLURPLE
            ),
            view = view,
            ephemeral = True
        )

def setup(bot):
    bot.add_cog(Settings(bot))