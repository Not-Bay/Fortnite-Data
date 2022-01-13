from discord.ext import commands
import discord
import datetime
import time

import util

class Other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='invite')
    @commands.cooldown(2, 5)
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
    @commands.cooldown(2, 5)
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