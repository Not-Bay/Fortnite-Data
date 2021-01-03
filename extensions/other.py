from discord.ext import commands
from io import BytesIO
from funcs import *
import datetime
import asyncio
import discord
import requests
import time

start_time = time.time()

class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='invite')
    @commands.cooldown(2, 14, commands.BucketType.user)
    async def invite(self, ctx):
        with open('values.json', 'r', encoding='utf-8') as f:
            values = json.load(f)

        embed = discord.Embed(
            title = f"{main.text(ctx, 'bot_invite_link')}",
            description = f"{values['current_invite']}",
            timestamp = ctx.message.created_at,
            color = 0x570ae4
        )
        await ctx.send(embed=embed)


    @commands.command(usage='info')
    @commands.cooldown(3, 20, commands.BucketType.user)
    async def info(self, ctx):

        current_time = time.time()
        difference = int(round(current_time - start_time))
        final = str(datetime.timedelta(seconds=difference))

        embed = discord.Embed(
            title = f'Fortnite Data',
            description = 'Powered by [Fortnite-API.com](https://fortnite-api.com/) , [benbotfn.tk](https://benbotfn.tk/) , [nitestats.com](https://nitestats.com/) and [api.peely.de](https://api.peely.de)',
            color = 0x570ae4
        )

        embed.add_field(name=main.text(ctx, 'owner'), value='``BayGamerYT#7849``') #rip nitro xd
        embed.add_field(name=main.text(ctx, 'servers'), value=f'``{len(self.bot.guilds)}``')
        embed.add_field(name=main.text(ctx, 'users'), value=f'``{len(self.bot.users)}``')
        embed.add_field(name=main.text(ctx, 'uptime'), value=f'``{final}``')
        embed.add_field(name=main.text(ctx, 'translators'), value='``gomashio#4335``')
        embed.add_field(name=main.text(ctx, 'official_support_server'), value='[discord.gg/UU9HjA5](https://www.discord.com/invite/UU9HjA5)')

        image = BytesIO(requests.get(url='https://top.gg/api/widget/729409703360069722.png').content)
        
        embed.set_image(url=f'attachment://topgg_stats.png')

        await ctx.send(embed=embed, file=discord.File(image, 'topgg_stats.png'))

    @commands.command(usage='uptime')
    @commands.cooldown(2, 15, commands.BucketType.user)
    async def uptime(self, ctx):

        current_time = time.time()

        difference = int(round(current_time - start_time))

        txt = str(datetime.timedelta(seconds=difference))

        embed = discord.Embed(
            description = f'{main.text(ctx, "uptime")}: ``{txt}``',
            colour = 0x570ae4
        )

        await ctx.send(embed=embed)


    @commands.command(usage='ping')
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def ping(self, ctx):
        
        embed1 = discord.Embed(
            description = f'{main.text(ctx, "pinging")} <a:loading:757475019759550504>',
            color = 0x570ae4
        )
        msg = await ctx.send(embed=embed1)

        t = msg
        ms = (t.created_at-ctx.message.created_at).total_seconds() * 1000
        await asyncio.sleep(self.bot.latency)

        embed2 = discord.Embed(
            description = f'``{ms}`` ms <a:check:757475072155058308>',
            color = 0x570ae4
        )
        await msg.edit(embed=embed2)

    @commands.command(usage='feedback <content>')
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def feedback(self, ctx, *, content=None):

        if content == None:

            embed = discord.Embed(
                description = main.text(ctx, 'feedback_text_when_no_args'),
                color = 0x570ae4
            )
            await ctx.send(embed=embed)
        
        else:

            attachments = ''.join(f"{x.url}\n" for x in ctx.message.attachments)

            feedback_embed = discord.Embed(
                title = 'New feedback',
                description = f'**User ID**\n`{ctx.author.id}`\n**Content**\n_{content}_\n**Attachments**\n{attachments}',
                color = 0x570ae4
            )
            channel = self.bot.get_channel(786437973306638346)
            await channel.send(embed=feedback_embed)

            await ctx.send(main.text(ctx, 'feedback_sended'))


def setup(bot):
    bot.add_cog(info(bot))