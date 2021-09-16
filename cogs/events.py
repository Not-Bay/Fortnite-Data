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
    async def on_button_click(self, interaction):

        if interaction.custom_id == 'SERVER_PREFIX_CONFIGURE':

            def check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            server = util.database_get_server(interaction.guild)
            
            msg = await interaction.respond(
                type = InteractionType.UpdateMessage,
                embed = discord.Embed(
                    description = 'Send the new prefix to use',
                    color = discord.Colour.blue()
                ).set_footer(text='Type "cancel" to cancel'),
                components = []
            )

            try:

                user_msg = await self.bot.wait_for('message', check=check, timeout=120)

                if user_msg.content.lower() == 'cancel':

                    await interaction.message.edit(
                        embed = discord.Embed(
                            description = f'Operation canceled by the user.',
                            color = discord.Colour.green()
                        )
                    )
                    return

                if len(user_msg.content) > 4:

                    await interaction.message.edit(
                        embed = discord.Embed(
                            description = 'Sorry but the prefix must be a maximum of 4 characters.',
                            color = discord.Colour.red()
                        )
                    )
                    return

                else:

                    new_prefix = user_msg.content

                    if new_prefix == server['prefix']:

                        await interaction.message.edit(
                            embed = discord.Embed(
                                description = 'The new prefix must be different from the old one.',
                                color = discord.Colour.red()
                            )
                        )
                        return

                    else:

                        change = util.database_update_server(interaction.guild, {'$set': {'prefix': new_prefix}})

                        await interaction.message.edit(
                            embed = discord.Embed(
                                description = f'Prefix changed to `{new_prefix}` successfully!',
                                color = discord.Colour.green()
                            )
                        )
                        return

            except asyncio.TimeoutError:

                await interaction.message.edit(
                    embed = discord.Embed(
                        description = 'Canceled by timeout',
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
                type = InteractionType.UpdateMessage,
                embed = discord.Embed(
                    description = 'Select the language to use',
                    color = discord.Colour.blue()
                ),
                components = components
            )

            try:

                i = await self.bot.wait_for('button_click', check=check, timeout=120)

                if i.custom_id == 'SERVER_LANG_OPTION_EN':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'en'}})

                    await i.respond(
                        type = InteractionType.UpdateMessage,
                        embed = discord.Embed(
                            description = f'Language changed to `English`!',
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

                elif i.custom_id == 'SERVER_LANG_OPTION_ES':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'es'}})

                    await i.respond(
                        type = InteractionType.UpdateMessage,
                        embed = discord.Embed(
                            description = f'Language changed to `Español`!',
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

                elif i.custom_id == 'SERVER_LANG_OPTION_JA':

                    change = util.database_update_server(interaction.guild, {'$set': {'language': 'ja'}})

                    await i.respond(
                        type = InteractionType.UpdateMessage,
                        embed = discord.Embed(
                            description = f'Language changed to `日本語`!',
                            color = discord.Colour.blue()
                        ),
                        components = []
                    )

            except asyncio.TimeoutError:

                await msg.edit(embed=discord.Embed(
                    description = 'Canceled by timeout.',
                    color = discord.Colour.blue()
                ))

        elif interaction.custom_id == 'SERVER_UPDATES_CHANNEL_CONFIGURE':

            server = util.database_get_server(interaction.guild)

            already_configurated = server['updates_channel']['enabled']

            embed = discord.Embed(
                description = 'Send the ID/mention of the channel' if already_configurated == False else 'Type "disable" to disable it or send the ID/mention of the new channel',
                color = discord.Colour.blue()
            )
            embed.set_footer(text='Type "cancel" to cancel')

            msg = await interaction.respond(
                type = InteractionType.UpdateMessage,
                embed = embed,
                components = []
            )

            def check(message):
                return message.author == interaction.author and message.channel == interaction.channel

            try:

                usrmsg = await self.bot.wait_for('message', check=check, timeout=120)

                if usrmsg.content.lower() == 'cancel':

                    await interaction.message.edit(embed=discord.Embed(
                        description = 'Operation canceled by user.',
                        color = discord.Colur.red()
                    ))
                    return

                elif usrmsg.content.lower() == 'disable':

                    if already_configurated == False:

                        await interaction.message.edit(embed=discord.Embed(
                            description = 'The channel is\'nt configurated yet!.',
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
                                description = 'An error ocurred deleting webhook. Please make sure the bot has `Manage Webhooks` permission or delete it yourself.',
                                color = discord.Colour.red()
                            ))
                            return

                        except Exception:

                            log.error(f'An error ocurred removing webhook in updates channel disabling. Traceback: {traceback.format_exc()}')


                        change = util.database_update_server(interaction.guild, {'$set': {'updates_channel.enabled': False, 'updates_channel.webhook': None, 'updates_channel.channel': None, 'updates_channel.webhook_id': None}})

                        await interaction.message.edit(embed=discord.Embed(
                            description = 'The updates channel was disabled correctly!',
                            color = discord.Colour.blue()
                        ))
                        return

                else:

                    channel_id = usrmsg.content.lower().strip('<#> ')

                    try:
                        channel = await self.bot.fetch_channel(int(channel_id))
                    except:
                        await interaction.message.edit(embed=discord.Embed(
                            description = 'You have to send the channel ID or mention **only**!',
                            color = discord.Colour.red()
                        ))
                        return

                    if channel == None:

                        await interaction.message.edit(embed=discord.Embed(
                            description = 'Sorry but the channel is\'nt valid or i do\'nt have access to it.',
                            color = discord.Colour.red()
                        ))
                        return
                    
                    else:

                        try: #create webhook

                            webhook = await channel.create_webhook(name='Fortnite Data Updates Channel', reason=f'Updates channel configured by {interaction.author}')

                        except:

                            await interaction.message.edit(embed=discord.Embed(
                                description = 'An error ocurred setting up updates channel. Make sure the bot has `Manage Webhooks` permission!',
                                color = discord.Colour.red()
                            ))
                            return
                            
                        change = util.database_update_server(interaction.guild, {'$set': {'updates_channel.enabled': True, 'updates_channel.webhook': webhook.url, 'updates_channel.channel': channel.id, 'updates_channel.webhook_id': webhook.id}})

                        if change != None:

                            await interaction.message.edit(embed=discord.Embed(
                                description = f'Channel <#{channel.id}> is now set as updates channel!',
                                color = discord.Colour.blue()
                            ))
                            return
                        
                        else:

                            await interaction.message.edit(embed=discord.Embed(
                                description = f'An unknown error ocurred while setting updates channel.',
                                color = discord.Colour.red()
                            ))
                            return

            except asyncio.TimeoutError:

                await interaction.message.edit(embed=discord.Embed(
                    description = 'Operation canceled by timeout.',
                    color = discord.Colour.red()
                ))
                return


def setup(bot):
    bot.add_cog(Events(bot))