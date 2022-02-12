from discord.ext import commands
import discord
import ast

import util
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


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(hidden=True)
    async def eval(self, ctx, *, cmd):
        """Evaluates code"""
        
        try:
            fn_name = "_eval_expr"
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            insert_returns(body)
            env = {
                'import': __import__,
                'discord': discord,
                'bot': self.bot,
                'ctx': ctx,
                'util': util,
                'os': os
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
        except Exception as error:
            await ctx.send(f'```py\n{error}```')

        try:
            result = (await eval(f"{fn_name}()", env))
            await ctx.send(f'```py\n{result}```')
        except Exception as error:
            await ctx.send(f'```py\n{error}```')

def setup(bot):
    bot.add_cog(Admin(bot))