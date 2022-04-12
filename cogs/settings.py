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
        name='language', 
        description=util.get_str('en', 'command_description_settings_language'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_settings_language'),
            'ja': util.get_str('ja', 'command_description_settings_language')
        },
    )
    @commands.cooldown(2, 4)
    async def settings_language(
        self,
        ctx: discord.ApplicationContext,
        new_language: Option(
            str,
            description = 'New language to use',
            default = 'none',
            choices = [
                OptionChoice(name = 'English', value = 'en'),
                OptionChoice(name = 'Español', value = 'es'),
                OptionChoice(name = '日本語', value = 'ja')
            ]
        )
    ):
        
        lang = util.get_guild_lang(ctx)

        if ctx.author.guild_permissions.administrator == False:

            await ctx.respond(
                embed = discord.Embed(
                    description = util.get_str(lang, 'command_string_only_admin_command'),
                    color = util.Colors.RED
                ),
                ephemeral = True
            )

        else:

            server = util.database_get_server(ctx)

            if server['language'] == new_language:

                await ctx.respond(
                    embed = discord.Embed(
                        description = util.get_str(lang, 'command_string_new_lang_same_as_old'),
                        color = util.Colors.RED
                    ),
                    ephemeral = True
                )

            elif new_language == 'none':

                await ctx.respond(
                    embed = discord.Embed(
                        description = util.get_str(lang, 'command_string_current_language_and_options').format(language = server['language'], options = 'en / es / ja'),
                        color = util.Colors.BLURPLE
                    )
                )

            else:

                changes = util.database_update_server(
                    ctx = ctx,
                    changes = {
                        '$set': {
                            'language': new_language
                        }
                    }
                )

                await ctx.respond(
                    embed = discord.Embed(
                        description = util.get_str(lang, 'interaction_string_language_changed_to').format(lang = new_language),
                        color = util.Colors.GREEN
                    )
                )

    @settings.command(
        name='shop', 
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
        
        lang = util.get_guild_lang(ctx)

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
            view = view
        )

    @settings.command(
        name='updates', 
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
        
        lang = util.get_guild_lang(ctx)

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
            view = view
        )

def setup(bot):
    bot.add_cog(Settings(bot))