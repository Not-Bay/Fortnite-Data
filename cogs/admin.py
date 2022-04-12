from discord.commands import slash_command, Option, permissions
from discord.ext import commands
import discord
import ast

from modules import util
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

    @slash_command(name = 'sync-commands', description = 'Syncs commands', guild_ids=util.debug_guilds)
    @permissions.is_owner()
    async def _sync_commands(
        self,
        ctx: discord.ApplicationContext
    ):

        await ctx.respond(
            embed = discord.Embed(
                description = 'Syncing commands...',
                color = util.Colors.YELLOW
            )
        )

        await self.bot.sync_commands(force = True)

        await ctx.interaction.edit_original_message(
            embed = discord.Embed(
                description = 'Synced commands!',
                color = util.Colors.GREEN
            )
        )

    @slash_command(name = 'restart', description = 'Restarts the bot', guild_ids=util.debug_guilds)
    @permissions.is_owner()
    async def _restart(
        self,
        ctx: discord.ApplicationContext
    ):

        try:
            cog = self.bot.cogs['Tasks']

            cog.shop_check.stop()
            cog.updates_check.stop()

            await ctx.respond('The bot should restart in a few seconds.')
            os.system('systemctl restart FortniteData.service')
        except Exception as e:
            await ctx.respond(f'Could not restart: {e}')

    @slash_command(name = 'reload', description = 'Reloads a cog', guild_ids=util.debug_guilds)
    @permissions.is_owner()
    async def _reload(
        self,
        ctx: discord.ApplicationContext,
        cog: Option(
            str,
            description = 'Cog to reload',
            required = True
        )
    ):

        try:
            self.bot.reload_extension(f'cogs.{cog}')
            await ctx.respond(f'The cog `{cog}` was reloaded correctly.')
        except Exception as e:
            await ctx.respond(f'Could not reload the cog: {e}')

    @slash_command(name = 'load', description = 'Load a cog', guild_ids=util.debug_guilds)
    @permissions.is_owner()
    async def _load(
        self,
        ctx: discord.ApplicationContext,
        cog: Option(
            str,
            description = 'Cog to load',
            required = True
        )
    ):

        try:
            self.bot.load_extension(f'cogs.{cog}')
            await ctx.respond(f'The cog `{cog}` was loaded correctly.')
        except Exception as e:
            await ctx.respond(f'Could not load the cog: {e}')

    @slash_command(name = 'unload', description = 'Unload a cog', guild_ids=util.debug_guilds)
    @permissions.is_owner()
    async def _unload(
        self,
        ctx: discord.ApplicationContext,
        cog: Option(
            str,
            description = 'Cog to unload',
            required = True
        )
    ):
        try:
            self.bot.unload_extension(f'cogs.{cog}')
            await ctx.respond(f'The cog `{cog}` was unloaded correctly.')
        except Exception as e:
            await ctx.respond(f'Could not unload the cog: {e}')

    @slash_command(name = 'eval', description = 'Evaluates code', guild_ids=util.debug_guilds)
    @permissions.is_owner()
    async def eval(
        self,
        ctx: discord.ApplicationContext,
        cmd: Option(
            str,
            description = 'Code to evaluate',
            required = True
        )
    ):
        
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
            await ctx.respond(f'```py\n{error}```', ephemeral=True)

        try:
            result = (await eval(f"{fn_name}()", env))
            await ctx.respond(f'```py\n{result}```', ephemeral=True)
        except Exception as error:
            await ctx.respond(f'```py\n{error}```', ephemeral=True)

def setup(bot):
    bot.add_cog(Admin(bot))