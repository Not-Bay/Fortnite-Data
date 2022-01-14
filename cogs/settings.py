from discord.ext import commands
from discord_components import *
import asyncio
import discord
import logging

import util

log = logging.getLogger('FortniteData.cogs.settings')

class General(commands.Cog):

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
            embed.add_field(name=util.get_str(lang, 'command_string_updates_channel'), value=f'`{util.get_str(lang, "command_string_configured") if data["updates_channel"]["enabled"] == True else util.get_str(lang, "command_string_not_configurated")}`', inline=False)

            components = [
                [
                    Button(style=ButtonStyle.blue ,label=util.get_str(lang, 'command_string_change_prefix'), custom_id='SERVER_PREFIX_CONFIGURE'),
                    Button(style=ButtonStyle.blue ,label=util.get_str(lang, 'command_string_change_language'), custom_id='SERVER_LANG_CONFIGURE')
                ],
                [
                    Button(style=ButtonStyle.blue ,label=util.get_str(lang, 'command_string_manage_updates_channel'), custom_id='SERVER_UPDATES_CHANNEL_CONFIGURE'),
                    Button(style=ButtonStyle.blue ,label=util.get_str(lang, 'command_string_manage_shop_channel'), custom_id='SERVER_SHOP_CHANNEL_CONFIGURE')
                ]
            ]

            await ctx.send(
                embed = embed,
                components = components
            )


def setup(bot):
    bot.add_cog(General(bot))