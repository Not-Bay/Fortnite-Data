from discord.ext import commands
import discord
import funcs
import json
import main
import sys

with open('values.json', 'r', encoding='utf-8') as vf:
    values = json.load(vf)

langs = values['settings']['available langs']
api_langs = values['settings']['available api langs']

available_langs = ' '.join([f'`{x}`' for x in langs])
search_langs = ' '.join([f'`{x}`' for x in api_langs])

class settings(commands.Cog, name='Settings'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def settings(self, ctx):

        servers = main.db.guilds

        embed = discord.Embed(
            title=f'{str(main.text(ctx, "config_for"))} {ctx.guild.name}\n',
            timestamp=ctx.message.created_at,
            color = 0x570ae4
        )

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(
            text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

        embed.add_field(name=main.text(ctx, 'prefix'), value=f'`{servers.find_one({"server_id": ctx.guild.id})["prefix"]}`', inline=False)
        embed.add_field(name=main.text(ctx, "lang"), value=f'`{servers.find_one({"server_id": ctx.guild.id})["lang"]}`', inline=False)
        
        embed.add_field(name=main.text(ctx, 'search_lang'), value=f'`{servers.find_one({"server_id": ctx.guild.id})["search_lang"]}`', inline=False)
        embed.add_field(name=main.text(ctx, 'max_search_results'), value=f'`{servers.find_one({"server_id": ctx.guild.id})["max_results"]}`', inline=False)


        chan = f'<#{servers.find_one({"server_id": ctx.guild.id})["shop_channel"]}>' if servers.find_one({"server_id": ctx.guild.id})["shop_channel"] != 1 else main.text(ctx, 'none')
        embed.add_field(name=main.text(ctx, 'shop_channel'),
                        value=chan)

        uchan = f'<#{servers.find_one({"server_id": ctx.guild.id})["updates_channel"]}>' if servers.find_one({"server_id": ctx.guild.id})["updates_channel"] != 1 else main.text(ctx, 'none')
        embed.add_field(name=main.text(ctx, 'updates_channel'),
                        value=uchan)

        await ctx.send(embed=embed)
        return


    @commands.command(pass_context=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def prefix(self, ctx, value=None):

        if value == None:

            embed = discord.Embed(
                description=main.text(ctx, 'must_enter_value'),
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        else:

            await funcs.set_config(ctx, 'prefix', value)

            embed = discord.Embed(
                description=main.text(ctx, 'prefix_changed_to').format(value),
                color=discord.Colour.green()
            )
            await ctx.send(embed=embed)


    @commands.command(aliases=['language'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def lang(self, ctx, value=None):

        if value == None:

            embed = discord.Embed(
                description=f"{main.text(ctx, 'available_langs').format(available_langs)}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        else:

            if value == 'es':

                await funcs.set_config(ctx, 'lang', 'es')

                embed = discord.Embed(
                    description=f"{main.text(ctx, 'lang_changed_to').format(value)}",
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

            elif value == 'en':

                await funcs.set_config(ctx, 'lang', 'en')

                embed = discord.Embed(
                    description=f"{main.text(ctx, 'lang_changed_to').format(value)}",
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

            elif value == 'ja':

                await funcs.set_config(ctx, 'lang', 'ja')

                embed = discord.Embed(
                    description=f"{main.text(ctx, 'lang_changed_to').format(value)}",
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                description=f"{main.text(ctx, 'available_langs').format(available_langs)}",
                color=discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return
                


    @commands.command(pass_context=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def shopchannel(self, ctx, newchannel=None):

        if newchannel != None:

            if newchannel not in ['disable', 'off', 'false']:

                c4 = newchannel.strip('<># ')

                try:
                    chan = self.bot.get_channel(int(c4))
                except:

                    embed = discord.Embed(
                            description=main.text(ctx, 'error_invalid_channel'),
                            color=discord.Colour.red()
                        )
                    await ctx.send(embed=embed)
                    return

                if chan != None:

                    if chan.guild == ctx.guild:

                        await funcs.set_config(ctx, 'shop_channel', int(c4))

                        embed = discord.Embed(
                            description=main.text(ctx, 'itemshop_channel_changed_to').format(
                                f'<#{chan.id}>'),
                            color=discord.Colour.green()
                        )
                        await ctx.send(embed=embed)

                    else:

                        embed = discord.Embed(
                            description=main.text(ctx, 'error_invalid_channel'),
                            color=discord.Colour.red()
                        )
                        await ctx.send(embed=embed)

                else:

                    embed = discord.Embed(
                        description=main.text(ctx, 'error_invalid_channel'),
                        color=discord.Colour.red()
                    )
                    await ctx.send(embed=embed)

            else:
                await funcs.set_config(ctx, config='shop_channel', value=1)

                embed = discord.Embed(
                    description=main.text(ctx, 'itemshop_channel_disabled'),
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description=main.text(ctx, 'must_mention_channel'),
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)


    @commands.command(aliases=['search_language'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def search_lang(self, ctx, newlang=None):

        if newlang == None:

            embed = discord.Embed(
                description=f"{main.text(ctx, 'available_langs').format(search_langs)}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        else:

            if newlang in api_langs:

                await funcs.set_config(ctx, 'search_lang', newlang)

                embed = discord.Embed(
                    description=main.text(ctx, 'search_lang_changed_to').format(newlang),
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)
                return

            else:

                embed = discord.Embed(
                    description=f"{main.text(ctx, 'available_langs').format(search_langs)}",
                    color=discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return

    @commands.command(pass_context=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def maxresults(self, ctx, newvalue=None):

        if newvalue == None:
            embed = discord.Embed(
                description = f'{main.text(ctx, "must_more_than_zero")}',
                color = discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        entered = int(newvalue.strip(' '))

        if entered > 0:

            if entered > 50:

                embed = discord.Embed(
                    description = f'{main.text(ctx, "max_value_is_50")}',
                    color = discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return

            servers = main.db.guilds

            if servers.find_one({"server_id": ctx.guild.id})['max_results'] == entered:

                embed = discord.Embed(
                    description = f'{main.text(ctx, "must_be_another_than_actual")}',
                    color = discord.Colour.red()
                )
                await ctx.send(embed=embed)
                return
            
            else:

                await funcs.set_config(ctx, 'max_results', entered)

                embed = discord.Embed(
                    description = f'{main.text(ctx, "max_results_changed_to").format(entered)}',
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)
                return

        
        else:

            embed = discord.Embed(
                description = f'{main.text(ctx, "must_more_than_zero")}',
                color = discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

    @commands.command(pass_context=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_guild_permissions(administrator=True)
    async def updateschannel(self, ctx, newchannel=None):

        if newchannel != None:

            if newchannel not in ['disable', 'off', 'false']:

                c4 = newchannel.strip('<># ')

                try:
                    chan = self.bot.get_channel(int(c4))
                except:

                    embed = discord.Embed(
                            description=main.text(ctx, 'error_invalid_channel'),
                            color=discord.Colour.red()
                        )
                    await ctx.send(embed=embed)
                    return

                if chan != None:

                    if chan.guild == ctx.guild:

                        await funcs.set_config(ctx, 'updates_channel', int(c4))

                        embed = discord.Embed(
                            description=main.text(ctx, 'updates_channel_changed_to').format(
                                f'<#{chan.id}>'),
                            color=discord.Colour.green()
                        )
                        await ctx.send(embed=embed)

                    else:

                        embed = discord.Embed(
                            description=main.text(ctx, 'error_invalid_channel'),
                            color=discord.Colour.red()
                        )
                        await ctx.send(embed=embed)

                else:

                    embed = discord.Embed(
                        description=main.text(ctx, 'error_invalid_channel'),
                        color=discord.Colour.red()
                    )
                    await ctx.send(embed=embed)

            else:
                await funcs.set_config(ctx, config='updates_channel', value=1)

                embed = discord.Embed(
                    description=main.text(ctx, 'updates_channel_disabled'),
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description=main.text(ctx, 'must_mention_channel'),
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)

    @commands.command(usage='updatesconfig <cosmetics / playlists / blogposts / news / aes> <enable / disable>')
    @commands.cooldown(1, 2)
    @commands.has_guild_permissions(administrator=True)
    async def updatesconfig(self, ctx, value1=None, value2=None):

        servers = main.db.guilds

        server = servers.find_one({"server_id": ctx.guild.id})

        if value1 == None:

            embed = discord.Embed(
                title = main.text(ctx, 'updates_channel_configuration'),
                color = 0x570ae4
            )
            embed.add_field(name='Cosmetics', value=f'`{main.text(ctx, "enabled") if server["updates_config"]["cosmetics"] == True else main.text(ctx, "disabled")}`')
            embed.add_field(name='Playlists', value=f'`{main.text(ctx, "enabled") if server["updates_config"]["playlists"] == True else main.text(ctx, "disabled")}`')

            embed.add_field(name='Blogposts', value=f'`{main.text(ctx, "enabled") if server["updates_config"]["blogposts"] == True else main.text(ctx, "disabled")}`')
            embed.add_field(name='News', value=f'`{main.text(ctx, "enabled") if server["updates_config"]["news"] == True else main.text(ctx, "disabled")}`')

            embed.add_field(name='Aes', value=f'`{main.text(ctx, "enabled") if server["updates_config"]["aes"] == True else main.text(ctx, "disabled")}`')
            
            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)

        elif value1 == 'cosmetics':

            if value2 in ['true', 'enable', 'on']:

                if server['updates_config']['cosmetics'] == True:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_enabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.cosmetics": True}})

                embed = discord.Embed(
                    description = main.text(ctx, 'enabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)

            elif value2 in ['false', 'disable', 'off']:

                if server['updates_config']['cosmetics'] == False:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_disabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.cosmetics": False}})

                embed = discord.Embed(
                    description = main.text(ctx, 'disabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                    description = '`enable / disable`',
                    color = 0x570ae4
                )
                await ctx.send(embed=embed)

        elif value1 == 'aes':

            if value2 in ['true', 'enable', 'on']:

                if server['updates_config']['aes'] == True:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_enabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.aes": True}})

                embed = discord.Embed(
                    description = main.text(ctx, 'enabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)

            elif value2 in ['false', 'disable', 'off']:

                if server['updates_config']['aes'] == False:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_disabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.aes": False}})

                embed = discord.Embed(
                    description = main.text(ctx, 'disabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                    description = '`enable / disable`',
                    color = 0x570ae4
                )
                await ctx.send(embed=embed)

        elif value1 == 'playlists':

            if value2 in ['true', 'enable', 'on']:

                if server['updates_config']['playlists'] == True:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_enabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.playlists": True}})

                embed = discord.Embed(
                    description = main.text(ctx, 'enabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)

            elif value2 in ['false', 'disable', 'off']:

                if server['updates_config']['playlists'] == False:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_disabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.playlists": False}})

                embed = discord.Embed(
                    description = main.text(ctx, 'disabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)
            
            else:
                embed = discord.Embed(
                    description = '`enable / disable`',
                    color = 0x570ae4
                )
                await ctx.send(embed=embed)

        elif value1 == 'blogposts':

            if value2 in ['true', 'enable', 'on']:

                if server['updates_config']['blogposts'] == True:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_enabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.blogposts": True}})

                embed = discord.Embed(
                    description = main.text(ctx, 'enabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)

            elif value2 in ['false', 'disable', 'off']:

                if server['updates_config']['blogposts'] == False:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_disabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.blogposts": False}})

                embed = discord.Embed(
                    description = main.text(ctx, 'disabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)
            
            else:
                embed = discord.Embed(
                    description = '`enable / disable`',
                    color = 0x570ae4
                )
                await ctx.send(embed=embed)

        elif value1 == 'news':

            if value2 in ['true', 'enable', 'on']:

                if server['updates_config']['news'] == True:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_enabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.news": True}})

                embed = discord.Embed(
                    description = main.text(ctx, 'enabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)

            elif value2 in ['false', 'disable', 'off']:

                if server['updates_config']['news'] == False:
                    embed = discord.Embed(
                        description = main.text(ctx, "already_disabled"),
                        color = 0x570ae4
                    )
                    await ctx.send(embed=embed)
                    return

                servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"updates_config.news": False}})

                embed = discord.Embed(
                    description = main.text(ctx, 'disabled'),
                    color = discord.Colour.green()
                )
                await ctx.send(embed=embed)
            
            else:
                embed = discord.Embed(
                    description = '`enable / disable`',
                    color = 0x570ae4
                )
                await ctx.send(embed=embed)

        else:

            await ctx.send('`cosmetics / playlists / blogposts / news / aes`')



    @commands.command(pass_context=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def shopconfig(self, ctx, config=None, *, newvalue=None):

        servers = main.db.guilds
        server = servers.find_one({"server_id": ctx.guild.id})
        configs = ['header', 'subheader', 'footer', 'background']

        if ctx.author.guild_permissions.administrator:

            if config == None:

                embed = discord.Embed(
                    title = main.text(ctx, 'shop_config'),
                    color = 0x570ae4,
                    timestamp = ctx.message.created_at
                )
                embed.add_field(name=main.text(ctx, 'shop_header'), value=f'`{server["shop_config"]["header"] if server["shop_config"]["header"] != "" else "None"}`')
                embed.add_field(name=main.text(ctx, 'shop_subheader'), value=f'`{server["shop_config"]["subheader"] if server["shop_config"]["subheader"] != "" else "None"}`')
                embed.add_field(name=main.text(ctx, 'shop_footer'), value=f'`{server["shop_config"]["footer"] if server["shop_config"]["footer"] != "" else "None"}`')
                embed.add_field(name=main.text(ctx, 'shop_background'), value=f'`{server["shop_config"]["background"] if server["shop_config"]["background"] != "" else "None"}`')

                embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

                await ctx.send(embed=embed)
                return

            elif config == 'header':

                if newvalue == None:

                    embed = discord.Embed(
                        description=f'{main.text(ctx, "shop_header")}: `{server["shop_config"]["header"] if server["shop_config"]["header"] != "" else "None"}`',
                            color = discord.Colour.blue()
                    )
                    await ctx.send(embed=embed)
                    return
                
                else:

                    servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"shop_config.header": newvalue if newvalue != 'clear' else ''}})

                    if newvalue == 'clear':

                        embed = discord.Embed(
                            description=f'{main.text(ctx, "header_cleared")}',
                            color = discord.Colour.green()
                        )
                        await ctx.send(embed=embed)
                        return

                    embed = discord.Embed(
                        description=f'{main.text(ctx, "header_changed_to")} `{newvalue}`',
                        color = discord.Colour.green()
                    )
                    await ctx.send(embed=embed)
                    return

            elif config == 'subheader':

                if newvalue == None:

                    embed = discord.Embed(
                            description=f'{main.text(ctx, "shop_subheader")}: `{server["shop_config"]["subheader"] if server["shop_config"]["subheader"] != "" else "None"}`',
                        color = discord.Colour.blue()
                    )
                    await ctx.send(embed=embed)
                    return

                else:

                    servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"shop_config.subheader": newvalue if newvalue != 'clear' else ''}})

                    if newvalue == 'clear':

                        embed = discord.Embed(
                            description=f'{main.text(ctx, "subheader_cleared")}',
                            color = discord.Colour.green()
                        )
                        await ctx.send(embed=embed)
                        return

                    embed = discord.Embed(
                        description=f'{main.text(ctx, "subheader_changed_to")} `{newvalue}`',
                        color = discord.Colour.green()
                    )
                    await ctx.send(embed=embed)
                    return


            elif config == 'footer':

                if newvalue == None:

                    embed = discord.Embed(
                        description=f'{main.text(ctx, "shop_footer")}: `{server["shop_config"]["footer"] if server["shop_config"]["footer"] != "" else "None"}`',
                        color = discord.Colour.blue()
                    )
                    await ctx.send(embed=embed)
                    return

                else:

                    servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"shop_config.footer": newvalue if newvalue != 'clear' else ''}})
                        
                    if newvalue == 'clear':

                        embed = discord.Embed(
                            description=f'{main.text(ctx, "footer_cleared")}',
                            color = discord.Colour.green()
                        )
                        await ctx.send(embed=embed)
                        return

                    embed = discord.Embed(
                        description=f'{main.text(ctx, "footer_changed_to")} `{newvalue}`',
                        color = discord.Colour.green()
                    )
                    await ctx.send(embed=embed)
                    return

            elif config == 'background':

                if newvalue == None:

                    embed = discord.Embed(
                        description=f'{main.text(ctx, "shop_background")}: `{server["shop_config"]["background"] if server["shop_config"]["background"] != "" else "None"}`',
                        color = discord.Colour.blue()
                    )
                    await ctx.send(embed=embed)
                    return

                else:

                    servers.find_one_and_update({"server_id": ctx.guild.id}, {"$set": {"shop_config.background": newvalue if newvalue != 'clear' else ''}})

                    if newvalue == 'clear':

                        embed = discord.Embed(
                            description=f'{main.text(ctx, "background_cleared")}',
                            color = discord.Colour.green()
                        )
                        await ctx.send(embed=embed)
                        return

                    embed = discord.Embed(
                        description=f'{main.text(ctx, "background_changed_to")} `{newvalue}`',
                        color = discord.Colour.green()
                    )
                    await ctx.send(embed=embed)
                    return

            else:

                embed = discord.Embed(
                description=f"{main.text(ctx, 'available_configs')} {''.join(f'`{x}` ' for x in configs)}",
                color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

        else:

            embed = discord.Embed(
                title = main.text(ctx, 'shop_config'),
                color = 0x570ae4,
                timestamp = ctx.message.created_at
                )
            embed.add_field(name=main.text(ctx, 'shop_header'), value=f'`{server["shop_config"]["header"] if server["shop_config"]["header"] != "" else "None"}`')
            embed.add_field(name=main.text(ctx, 'shop_subheader'), value=f'`{server["shop_config"]["subheader"] if server["shop_config"]["subheader"] != "" else "None"}`')
            embed.add_field(name=main.text(ctx, 'shop_footer'), value=f'`{server["shop_config"]["footer"] if server["shop_config"]["footer"] != "" else "None"}`')
            embed.add_field(name=main.text(ctx, 'shop_background'), value=f'`{server["shop_config"]["background"] if server["shop_config"]["background"] != "" else "None"}`')

            embed.set_footer(text=f"{main.text(ctx, value='executed_by')} {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
            return


def setup(bot):
    bot.add_cog(settings(bot))