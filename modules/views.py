from discord.ext import commands, pages
import logging
import discord
import io

from modules import util

log = logging.getLogger('FortniteData.modules.components')

###
## Commands components
###

class ReportToDeveloper(discord.ui.View): # on_application_command_error
    def __init__(self, lang: str, ctx: discord.ApplicationContext):
        super().__init__()

        self.ctx = ctx

        self.add_item(
            discord.ui.Button(
                label = util.get_str(lang, 'command_button_report_error_to_developer'),
                custom_id = f'ERROR_{ctx.author.id}'
            )
        )

    async def callback(ctx: discord.ApplicationContext):

        lang = util.get_guild_lang(ctx)

        error_info = ctx.interaction.custom_id.replace('ERROR_', '').split('_')

        user_id = error_info[0]

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
            
            channel = await ctx.bot.fetch_channel(util.configuration.get('error_reports_channel'))

            if channel == None:
                log.error('Error report could\'nt be sent. Invalid errors channel id in config')
            
            else:
                await channel.send(
                    embed = embed,
                    file = file
                )

            await ctx.interaction.response.send_message(
                embed = discord.Embed(
                    description = util.get_str(lang, 'command_string_error_was_reported_correctly'),
                    color = util.Colors.GREEN
                ),
                ephemeral = True
            )

        except KeyError:

            await ctx.interaction.response.send_message(
                embed = discord.Embed(
                    description = util.get_str(lang, 'command_string_error_can_not_report'),
                    color = util.Colors.RED
                ),
                ephemeral = True
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