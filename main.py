from discord_components import DiscordComponents
from discord.ext import commands
import coloredlogs
import traceback
import logging
import discord
import asyncio
import time
import sys

import util

log = logging.getLogger('FortniteData')
coloredlogs.install(level=None if util.debug == False else 'DEBUG')

bot = commands.AutoShardedBot(
    command_prefix=util.get_prefix,
    intents=discord.Intents.default()
)
bot.remove_command('help')

@bot.event
async def on_connect():
    log.debug('Connected to Discord')

@bot.event
async def on_ready():

    DiscordComponents(bot)

    for cog in util.configuration.get('cogs'):
        try:
            bot.load_extension(f'cogs.{cog}')
            log.debug(f'Loaded cog {cog}.')
        except:
            log.error(f'An error ocurred loading cog "{cog}". Traceback: {traceback.format_exc()}')

    for guild in bot.guilds:
        util.database_store_server(guild)

    await util.wait_cache_load()

    util.ready = True

    log.info(f'Fortnite Data is ready! • Took {int((time.time() - util.start_time))} seconds.')


def run():

    i = True
    if i:
        for v in list(logging.Logger.manager.loggerDict):
            if v != 'FortniteData':
                logging.getLogger(v).disabled = True

    log.info('Booting...')

    util.log = logging.getLogger('FortniteData.util')

    util.configuration = util.get_config()
    util.database = util.get_mongoclient().fortnitedata
    util.fortniteapi = util.FortniteAPI()

    log.debug('Starting discord bot...')

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.start(util.configuration.get('bot_token')))
    except Exception:
        log.critical(f'An error ocurred starting discord bot. Traceback:\n{traceback.format_exc()}')
        loop.run_until_complete(bot.close())
    finally:
        loop.close()
        sys.exit()


if __name__ == '__main__':

    run()