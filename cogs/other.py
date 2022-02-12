from discord.ext import commands
from discord_components import *
import discord
import datetime
import time

import util

class Other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.cooldown(4, 10, commands.BucketType.user)
    @commands.command(usage='settings', aliases=['config'])
    async def settings(self, ctx):

        lang = util.get_guild_lang(ctx.guild)

        if ctx.author.guild_permissions.administrator == False:

            await ctx.send(embed=discord.Embed(
                description = util.get_str(lang, 'command_string_only_admin_command'),
                color = discord.Colour.red()
            ))

        else:

            data = util.database_get_server(ctx.guild)

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_server_configuration'),
                color = discord.Colour.blue()
            )
            embed.add_field(name=util.get_str(lang, 'command_string_prefix'), value=f'`{data["prefix"]}`', inline=False)
            embed.add_field(name=util.get_str(lang, 'command_string_language'), value=f'`{data["language"]}`', inline=False)
            embed.add_field(name=util.get_str(lang, 'command_string_shop_channel'), value=f'`{util.get_str(lang, "command_string_configured") if data["shop_channel"]["enabled"] == True else util.get_str(lang, "command_string_not_configurated")}`', inline=False)
            embed.add_field(name=util.get_str(lang, 'command_string_updates_channel'), value=f'`{util.get_str(lang, "command_string_configured") if data["updates_channel"]["enabled"] == True else util.get_str(lang, "command_string_not_configurated")}`', inline=False)

            components = [
                [
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_string_change_prefix'), custom_id='SERVER_PREFIX_CONFIGURE'),
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_string_change_language'), custom_id='SERVER_LANG_CONFIGURE')
                ],
                [
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_string_manage_updates_channel'), custom_id='SERVER_UPDATES_CHANNEL_CONFIGURE'),
                    Button(style=ButtonStyle.blue, label=util.get_str(lang, 'command_string_manage_shop_channel'), custom_id='SERVER_SHOP_CHANNEL_CONFIGURE')
                ]
            ]

            await ctx.send(
                embed = embed,
                components = components
            )

    @commands.command(usage='invite')
    @commands.cooldown(2, 4)
    async def invite(self, ctx):
        """
        Let you invite the bot to your server
        """

        lang = util.get_guild_lang(ctx.guild)

        await ctx.send(embed = discord.Embed(
            title = util.get_str(lang, 'command_string_bot_invitation'),
            description = util.get_str(lang, 'command_string_click_here_to_invite').format(link = util.configuration['invite']),
            color = discord.Colour.blue()
        ))

    @commands.command(usage='ping')
    @commands.cooldown(2, 1)
    async def ping(self, ctx):
        """
        Checks the bot latency
        """

        lang = util.get_guild_lang(ctx.guild)

        ms = (ctx.message.created_at - ctx.message.created_at).total_seconds() * 1000

        await ctx.send(embed=discord.Embed(
            description = util.get_str(lang, 'command_string_pong_ms').format(miliseconds = ms),
            color = discord.Colour.blue()
        ))

    @commands.command(usage='info')
    @commands.cooldown(3, 5)
    async def info(self, ctx):
        """
        Shows general info of the bot
        """

        lang = util.get_guild_lang(ctx.guild)

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
            color = discord.Colour.blue()
        )
        embed.add_field(name = util.get_str(lang, 'command_string_developer'), value = '`Bay#1111`')
        embed.add_field(name = util.get_str(lang, 'command_string_servers'), value = f'`{len(self.bot.guilds)}`')
        embed.add_field(name = util.get_str(lang, 'command_string_uptime'), value = f'`{bot_uptime}`')
        embed.add_field(name = util.get_str(lang, 'command_string_translations'), value = translations_credits)

        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Other(bot))