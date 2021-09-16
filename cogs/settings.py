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
    async def settings(self, ctx, setting=None):

        if ctx.author.guild_permissions.administrator == False:

            await ctx.send(embed=discord.Embed(
                description = 'Sorry but this command is only for server administrators.',
                color = discord.Colour.red()
            ))

        else:

            data = util.database_get_server(ctx.guild)

            embed = discord.Embed(
                title = 'Server configuration',
                color = discord.Colour.blue()
            )
            embed.add_field(name='Prefix', value=f'`{data["prefix"]}`', inline=False)
            embed.add_field(name='Language', value=f'`{data["language"]}`', inline=False)
            embed.add_field(name='Updates channel', value=f'`{"Enabled" if data["updates_channel"]["enabled"] == True else "Not configurated"}`', inline=False)

            components = [
                [
                    Button(style=ButtonStyle.blue ,label='🔧 Prefix', custom_id='SERVER_PREFIX_CONFIGURE'),
                    Button(style=ButtonStyle.blue ,label='🔧 Language', custom_id='SERVER_LANG_CONFIGURE')
                ],
                [
                    Button(style=ButtonStyle.blue ,label='🔧 Updates channel', custom_id='SERVER_UPDATES_CHANNEL_CONFIGURE'),
                    Button(style=ButtonStyle.blue ,label='🔧 Shop channel', custom_id='SERVER_SHOP_CHANNEL_CONFIGURE')
                ]
            ]

            await ctx.send(
                embed = embed,
                components = components
            )


def setup(bot):
    bot.add_cog(General(bot))