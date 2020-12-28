from sys import platform
from discord.ext import commands
import traceback
import requests
import discord
import asyncio
import json
import funcs
import main
import ast
import sys
import io
import os


def insert_returns(body):

    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class admin(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def eval(self, ctx, *, cmd):
        fn_name = "_eval_expr"

        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            'requests': requests,
            'os': os,
            'funcs': funcs,
            'main': main,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        try:
            result = (await eval(f"{fn_name}()", env))
            if result == None:
                return
            await ctx.send(f'```py\n{result}```')
        except Exception as error:
            await ctx.send(f'```\n{error}```')


    @commands.command()
    @commands.is_owner()
    async def _updatefile(self, ctx, path):

        giturl = 'https://raw.githubusercontent.com/BayGamerYT/Fortnite-Data-Stuff/master/'

        response = requests.get(f'{giturl}{path}')

        if response.status_code != 200:
            await ctx.send(f'Error, response status `{response.status_code}`')

        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            await ctx.send(f'Updated `{path}`')

    @commands.command()
    @commands.is_owner()
    async def _getguilds(self, ctx):

        msg = await ctx.send(file=discord.File('settings/servers.json', filename='servers.json'))
        await asyncio.sleep(30)
        await msg.delete()




def setup(bot):
    bot.add_cog(admin(bot))