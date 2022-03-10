from discord.commands import slash_command
from discord.ext import commands
import discord
import datetime
import time

from modules import util, components

class Other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='settings', description=util.get_str('en', 'command_description_item'), guild_ids=util.debug_guilds)
    @commands.cooldown(4, 10)
    async def settings(self, ctx):

        lang = util.get_guild_lang(ctx)

        if ctx.author.guild_permissions.administrator == False:

            await ctx.respond(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_only_admin_command'),
                color = util.Colors.RED
            ))

        else:

            data = util.database_get_server(ctx.guild)

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_server_configuration'),
                color = util.Colors.BLUE
            )
            embed.add_field(name=util.get_str(lang, 'command_string_prefix'), value=f'`{data["prefix"]}`', inline=False)
            embed.add_field(name=util.get_str(lang, 'command_string_language'), value=f'`{data["language"]}`', inline=False)
            embed.add_field(name=util.get_str(lang, 'command_string_shop_channel'), value=f'`{util.get_str(lang, "command_string_configured") if data["shop_channel"]["enabled"] == True else util.get_str(lang, "command_string_not_configurated")}`', inline=False)
            embed.add_field(name=util.get_str(lang, 'command_string_updates_channel'), value=f'`{util.get_str(lang, "command_string_configured") if data["updates_channel"]["enabled"] == True else util.get_str(lang, "command_string_not_configurated")}`', inline=False)

            await ctx.respond(
                embed = embed,
                view = components.SettingsOptions(lang)
            )

    @slash_command(name='invite', description=util.get_str('en', 'command_description_invite'), guild_ids=util.debug_guilds)
    @commands.cooldown(2, 4)
    async def invite(self, ctx):
        """
        Let you invite the bot to your server
        """

        lang = util.get_guild_lang(ctx)

        await ctx.respond(embed = discord.Embed(
            title = util.get_str(lang, 'command_string_bot_invitation'),
            description = util.get_str(lang, 'command_string_click_here_to_invite').format(link = util.configuration['invite']),
            color = util.Colors.BLUE
        ))

    @slash_command(name='ping', description=util.get_str('en', 'command_description_ping'), guild_ids=util.debug_guilds)
    @commands.cooldown(2, 1)
    async def ping(self, ctx):
        """
        Checks the bot latency
        """

        lang = util.get_guild_lang(ctx)

        ms = (ctx.message.created_at - ctx.message.created_at).total_seconds() * 1000

        await ctx.respond(embed=discord.Embed(
            description = util.get_str(lang, 'command_string_pong_ms').format(miliseconds = ms),
            color = util.Colors.BLUE
        ))

    @slash_command(name='info', description=util.get_str('en', 'command_description_info'), guild_ids=util.debug_guilds)
    @commands.cooldown(3, 5)
    async def info(self, ctx):
        """
        Shows general info of the bot
        """

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
        embed.add_field(name = util.get_str(lang, 'command_string_developer'), value = '`Bay#1111`')
        embed.add_field(name = util.get_str(lang, 'command_string_servers'), value = f'`{len(self.bot.guilds)}`')
        embed.add_field(name = util.get_str(lang, 'command_string_uptime'), value = f'`{bot_uptime}`')
        embed.add_field(name = util.get_str(lang, 'command_string_translations'), value = translations_credits)

        await ctx.respond(
            embed = embed,
            view = components.LinkButton(
                label = util.get_str(lang, 'command_button_support_server'),
                url = 'https://discord.gg/UU9HjA5'
            )
        )


def setup(bot):
    bot.add_cog(Other(bot))