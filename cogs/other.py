from discord.commands import slash_command
from discord.ext import commands
import discord
import datetime
import time

from modules import util, views

class Other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name='invite',
        description=util.get_str('en', 'command_description_invite'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_invite'),
            'ja': util.get_str('ja', 'command_description_invite')
        }
    )
    @commands.cooldown(2, 4)
    async def invite(self, ctx: discord.ApplicationContext):

        lang = util.get_guild_lang(ctx)

        await ctx.respond(embed = discord.Embed(
            title = util.get_str(lang, 'command_string_bot_invitation'),
            description = util.get_str(lang, 'command_string_click_here_to_invite').format(link = util.configuration['invite']),
            color = util.Colors.BLUE
        ))

    @slash_command(
        name='info',
        description=util.get_str('en', 'command_description_info'),
        description_localizations={
            'es-ES': util.get_str('es', 'command_description_info'),
            'ja': util.get_str('ja', 'command_description_info')
        }
    )
    @commands.cooldown(3, 5)
    async def info(self, ctx: discord.ApplicationContext):

        lang = util.get_guild_lang(ctx)

        current_time = time.time()
        difference = int(round(current_time - util.start_time))
        bot_uptime = str(datetime.timedelta(seconds=difference))

        translations_credits = ''
        translations_credits += f'{util.get_str(lang, "command_string_translations_en_credit").format(user = util.configuration["translations"]["en"])}\n'
        translations_credits += f'{util.get_str(lang, "command_string_translations_es_credit").format(user = util.configuration["translations"]["es"])}\n'
        translations_credits += f'{util.get_str(lang, "command_string_translations_ja_credit").format(user = util.configuration["translations"]["ja"])}'

        embed = discord.Embed(
            title = 'Fortnite Data',
            description = util.get_str(lang, 'command_string_powered_by').format(
                fortniteapi_link = 'https://fortnite-api.com/',
                benbot_link = 'https://benbot.app/'
            ),
            color = util.Colors.BLUE
        )
        embed.add_field(name = util.get_str(lang, 'command_string_developer'), value = '`Bay#1218`')
        embed.add_field(name = util.get_str(lang, 'command_string_servers'), value = f'`{len(self.bot.guilds)}`')
        embed.add_field(name = util.get_str(lang, 'command_string_uptime'), value = f'`{bot_uptime}`')
        embed.add_field(name = util.get_str(lang, 'command_string_translations'), value = translations_credits)

        await ctx.respond(
            embed = embed,
            view = views.LinkButton(
                label = util.get_str(lang, 'command_button_support_server'),
                url = 'https://discord.gg/UU9HjA5'
            )
        )


def setup(bot):
    bot.add_cog(Other(bot))