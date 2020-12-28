from discord.ext import commands
import traceback
import discord
import funcs
import main

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            await funcs.create_config(guild)
        except Exception as e:
            funcs.log(f'Failed to create config for a new server: ```\n{"".join(traceback.format_exception(None, e, e.__traceback__))}```')


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            await funcs.delete_config(guild)
        except Exception as e:
            funcs.log(f'Failed to delete config for a server ```\n{"".join(traceback.format_exception(None, e, e.__traceback__))}```')


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot == True:
            return

        if message.content in [f'<@{self.bot.user.id}>', f'<@!{self.bot.user.id}>']:

            servers = main.serverconfig()

            embed = discord.Embed(
                description = f'{main.text(message, "prefix")}: `{servers[str(message.guild.id)]["prefix"]}`',
                color = 0x570ae4
            )
            await message.channel.send(embed=embed)
            return



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(main.text(ctx, 'on_cooldown').format(int(error.retry_after)))
            return

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(main.text(ctx, 'command_not_found'))
            return

        elif isinstance(error, commands.MissingPermissions):
            perms = ''.join(f'`{x}` ' for x in error.missing_perms)
            await ctx.send(main.text(ctx, 'command_insuficient_permissions').format(perms))
            return

        elif isinstance(error, commands.BotMissingPermissions):
            perms = ''.join(f'`{x}` ' for x in error.missing_perms)
            await ctx.send(f'{funcs.text(ctx, "bot_insuficient_permissions")}\n{perms}')
            return
        
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(funcs.text(ctx, 'error_command_disabled'))

        else:
            funcs.log(f'Error:```\n{"".join(traceback.format_exception(None, error, error.__traceback__))}```')
            raise error


def setup(bot):
    bot.add_cog(Events(bot))