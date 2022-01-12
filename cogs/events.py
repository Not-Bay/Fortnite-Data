from discord.ext import commands
from discord_components import *
import traceback
import asyncio
import discord
import logging

import util

log = logging.getLogger('FortniteData.cogs.settings')

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        lang = util.get_guild_lang(ctx.guild)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.CommandOnCooldown):

            end_seconds = int(str(error.retry_after)[0]) + 1

            embed = discord.Embed(
                description = util.get_str(lang, 'command_string_on_cooldown'),
                color = discord.Colour.orange()
            )
            embed.set_footer(text=util.get_str(lang, 'command_string_on_cooldown_retry_after').format(seconds = end_seconds))
            
            await ctx.send(
                embed=embed
            )
            return

        if isinstance(error, commands.DisabledCommand):

            embed = discord.Embed(
                title = util.get_str(lang, 'command_string_disabled_command'),
                description = util.get_str(lang, 'command_string_disabled_command_description'),
                color = discord.Colour.red()
            )
            embed.set_footer(text=util.get_str(lang, 'command_string_disabled_command_footer'))

            await ctx.send(
                embed = embed
            )
            return

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        util.database_store_server(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        util.database_remove_server(guild)


    @commands.Cog.listener()
    async def on_button_click(self, interaction):

        lang = util.get_guild_lang(interaction.guild)

        if interaction.custom_id == 'SERVER_PREFIX_CONFIGURE':

            def check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            server = util.database_get_server(interaction.guild)
            
            msg = await interaction.respond(
                type = 7,
                embed = discord.Embed(
                    description = util.get_str(lang, 'interaction_string_send_new_prefix'),
                    color = discord.Colour.blue()
                ).set_footer(text=util.get_Str(lang, 'interaction_string_cancel_text')),
                components = []
            )

            try:

                user_msg = await self.bot.wait_for('message', check=check, timeout=120)

                if user_msg.content.lower() == 'cancel':

                    await interaction.message.edit(
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_canceled_by_user'),
                            color = discord.Colour.green()
                        )
                    )
                    return

                if len(user_msg.content) > 4:

                    await interaction.message.edit(
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_error_new_prefix_too_long'),
                            color = discord.Colour.red()
                        )
                    )
                    return

                else:

                    new_prefix = user_msg.content

                    if new_prefix == server['prefix']:

                        await interaction.message.edit(
                            embed = discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_new_prefix_duplicate'),
                                color = discord.Colour.red()
                            )
                        )
                        return

                    else:

                        change = util.database_update_server(interaction.guild, {'$set': {'prefix': new_prefix}})

                        await interaction.message.edit(
                            embed = discord.Embed(
                                description = util.get_str(lang, 'interaction_string_changed_prefix'),
                                color = discord.Colour.green()
                            )
                        )
                        return

            except asyncio.TimeoutError:

                await interaction.message.edit(
                    embed = discord.Embed(
                        description = util.get_str(lang, 'interaction_string_canceled_by_timeout'),
                        color = discord.Colour.red()
                    )
                )
                return

        elif interaction.custom_id == 'SERVER_LANG_CONFIGURE':

            def check(i):
                return interaction.author == i.author and interaction.message == i.message

            server = util.database_get_server(interaction.guild)

            components = [[
                Button(style=ButtonStyle.green if server['language'] == 'en' else ButtonStyle.gray, label='English', disabled=True if server['language'] == 'en' else False, custom_id='SERVER_LANG_OPTION_EN'),
                Button(style=ButtonStyle.green if server['language'] == 'es' else ButtonStyle.gray, label='Español', disabled=True if server['language'] == 'es' else False, custom_id='SERVER_LANG_OPTION_ES'),
                Button(style=ButtonStyle.green if server['language'] == 'ja' else ButtonStyle.gray, label='日本語', disabled=True if server['language'] == 'ja' else False, custom_id='SERVER_LANG_OPTION_JA')
            ]]

            msg = await interaction.respond(
                type = 7,
                embed = discord.Embed(
                    description = util.get_str(lang, 'interaction_string_select_language'),
                    color = discord.Colour.blue()
                ),
                components = components
            )

            try:

                i = await self.bot.wait_for('button_click', check=check, timeout=120)

                if i.custom_id == 'SERVER_LANG_OPTION_EN':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'en'}})

                    await i.respond(
                        type = 7,
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_language_changed_to').format(lang = 'English'),
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

                elif i.custom_id == 'SERVER_LANG_OPTION_ES':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'es'}})

                    await i.respond(
                        type = 7,
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_language_changed_to').format(lang = 'Español'),
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

                elif i.custom_id == 'SERVER_LANG_OPTION_JA':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'ja'}})

                    await i.respond(
                        type = 7,
                        embed = discord.Embed(
                            description = util.get_str(lang, 'interaction_string_language_changed_to').format(lang = '日本語'),
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

            except asyncio.TimeoutError:

                await msg.edit(embed=discord.Embed(
                    description = util.get_str(lang, 'interaction_string_canceled_by_timeout'),
                    color = discord.Colour.blue()
                ))

        elif interaction.custom_id == 'SERVER_UPDATES_CHANNEL_CONFIGURE':

            server = util.database_get_server(interaction.guild)

            already_configurated = server['updates_channel']['enabled']

            embed = discord.Embed(
                description = util.get_str(lang, 'interaction_string_send_channel') if already_configurated == False else util.get_str(lang, 'interaction_string_send_channel_extra_to_disable'),
                color = discord.Colour.blue()
            )
            embed.set_footer(text=util.get_Str(lang, 'interaction_string_cancel_text'))

            msg = await interaction.respond(
                type = 7,
                embed = embed,
                components = []
            )

            def check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            try:

                usrmsg = await self.bot.wait_for('message', check=check, timeout=120)

                if usrmsg.content.lower() == 'cancel':

                    await interaction.message.edit(embed=discord.Embed(
                        description = util.get_str(lang, 'interaction_string_canceled_by_user'),
                        color = discord.Colour.red()
                    ))
                    return

                elif usrmsg.content.lower() == 'disable':

                    if already_configurated == False:

                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_error_channel_not_configurated'),
                            color = discord.Colour.red()
                        ))
                        return

                    else:

                        try:
                            webhook = await self.bot.fetch_webhook(server['updates_channel']['webhook_id'])
                            await webhook.delete()
                        except discord.NotFound:
                            log.debug('Ignoring webhook delete. It does not exists anymore')

                        except discord.Forbidden:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_webhook_delete'),
                                color = discord.Colour.red()
                            ))
                            return

                        except Exception:

                            log.error(f'An error ocurred removing webhook in updates channel disabling. Traceback: {traceback.format_exc()}')


                        change = util.database_update_server(interaction.guild, {'$set': {'updates_channel.enabled': False, 'updates_channel.webhook': None, 'updates_channel.channel': None, 'updates_channel.webhook_id': None}})

                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_channel_disabled'),
                            color = discord.Colour.blue()
                        ))
                        return

                else:

                    channel_id = usrmsg.content.lower().strip('<#> ')

                    try:
                        channel = await self.bot.fetch_channel(int(channel_id))
                    except:
                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_send_channel_only'),
                            color = discord.Colour.red()
                        ))
                        return

                    if channel == None:

                        await interaction.message.edit(embed=discord.Embed(
                            description = util.get_str(lang, 'interaction_string_error_invalid_channel_or_not_accesible'),
                            color = discord.Colour.red()
                        ))
                        return
                    
                    else:

                        try: #create webhook

                            webhook = await channel.create_webhook(name='Fortnite Data Updates Channel', reason=f'Updates channel configured by {interaction.author}')

                        except:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_webhook_create'),
                                color = discord.Colour.red()
                            ))
                            return
                            
                        change = util.database_update_server(interaction.guild, {'$set': {'updates_channel.enabled': True, 'updates_channel.webhook': webhook.url, 'updates_channel.channel': channel.id, 'updates_channel.webhook_id': webhook.id}})

                        if change != None:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_channel_configured').format(channel = f'<#{channel.id}>'),
                                color = discord.Colour.blue()
                            ))
                            return
                        
                        else:

                            await interaction.message.edit(embed=discord.Embed(
                                description = util.get_str(lang, 'interaction_string_error_unknown'),
                                color = discord.Colour.red()
                            ))
                            return

            except asyncio.TimeoutError:

                await interaction.message.edit(embed=discord.Embed(
                    description = util.get_str(lang, 'interaction_string_canceled_by_timeout'),
                    color = discord.Colour.red()
                ))
                return


def setup(bot):
    bot.add_cog(Events(bot))