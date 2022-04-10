from discord.commands import Option, OptionChoice, SlashCommandGroup, CommandPermission
from discord.ext import commands
import discord

from modules import util

class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    settings = SlashCommandGroup(
        'settings',
        util.get_str('en', 'command_description_settings'),
        guild_ids = util.debug_guilds
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

            server_data = util.database_get_server(ctx)

            if server_data['language'] == new_language:

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
                        description = util.get_str(lang, 'command_string_current_language_and_options').format(language = server_data['language'], options = 'en / es / ja'),
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

def setup(bot):
    bot.add_cog(Settings(bot))