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
    async def _command(self, ctx, commandName: str):
        """Enable/disable a command"""

        try:
            cmd = self.bot.get_command(commandName)

            if cmd.enabled == True:
                cmd.update(enabled = False)
                await ctx.send(f'The command `{commandName}` was disabled.')
            else:
                cmd.update(enabled = True)
                await ctx.send(f'The command `{commandName}` was enabled.')
        except Exception as e:
            await ctx.send(f'Could not enable/disable `{commandName}`: {e}')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def _restart(self, ctx):
        """Stops the cogs/tasks running tasks and restarts the bot"""

        try:
            cog = self.bot.cogs['Tasks']

            cog.shop_check.stop()
            cog.updates_check.stop()

            await ctx.send('The bot should restart in a few seconds.')
            os.system('systemctl restart FortniteData.service')
        except Exception as e:
            await ctx.send(f'Could not restart: {e}')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def _reload(self, ctx, cog: str):
        """Reloads a cog"""
        try:
            self.bot.reload_extension(f'cogs.{cog}')
            await ctx.send(f'The cog `{cog}` was reloaded correctly.')
        except Exception as e:
            await ctx.send(f'Could not reload the cog: {e}')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def _load(self, ctx, cog: str):
        """Load a cog"""
        try:
            self.bot.load_extension(f'cogs.{cog}')
            await ctx.send(f'The cog `{cog}` was loaded correctly.')
        except Exception as e:
            await ctx.send(f'Could not load the cog: {e}')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def _unload(self, ctx, cog: str):
        """Unload a cog"""
        try:
            self.bot.unload_extension(f'cogs.{cog}')
            await ctx.send(f'The cog `{cog}` was unloaded correctly.')
        except Exception as e:
            await ctx.send(f'Could not unload the cog: {e}')

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